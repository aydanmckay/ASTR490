# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 17:05:00 2021

@author: Aydan McKay
"""

import os
import sys
import numpy as np
import sqlite3
import shutil
import astropy.units as u
from astroquery.skyview import SkyView
import matplotlib.pyplot as plt
# from matplotlib.patches import Circle
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import time
from configparser import ConfigParser

def get_wise_catalog(db):
    """
    Returns a pandas dataframe containing relevant data from the 
    WISE Catalog. Originally created by Trey Wenger

    Parameters
    ----------
    db : string
         Filename to the HII Region database.

    Returns
    -------
    data : np.ndarray
        DataFrame containing the WISE Catalog data.

    """
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute("SELECT gname, ra, dec, radius FROM Catalog")
        data = np.array(
            cur.fetchall(),dtype=[('gname','<U16'), ('ra', '<f8'), 
                            ('dec', '<f8'), ('radius','<f8')])
    return data

def getcoords(coords,framekwarg = 'galactic'):
    """
    Converts user inputted coordinates to RA and Dec.

    Parameters
    ----------
    coords : list of strings
        The coordinates in Galactic coordinates inputted by the user.
    framekwarg : string, optional
        The format that the coordinates are to be changed from. The
        default is 'galactic'.

    Returns
    -------
    newcoords : list of strings
        The coordinates in RA and Dec.

    """
    if framekwarg == 'galactic':
        skycoordthing = SkyCoord(frame=framekwarg, l=coords[0],
                                 b=coords[1], unit='deg').icrs
        newcoords = [skycoordthing.ra.deg,skycoordthing.dec.deg]
        return newcoords
    else:
        skycoordthing = SkyCoord(coords, frame=framekwarg,
                                 unit=(u.hourangle, u.deg),
                                 obstime="J2000").icrs
        newcoords = [skycoordthing.ra.deg,skycoordthing.dec.deg]
        return newcoords

def scale(data, vmin, vmax):
    """
    Clip and logarithmically scale some data. Originally created by 
    Trey Wenger.

    Parameters
    ----------
    data : ndarray of scalars
        Data to clip and scale.
    vmin : scalar
        Minimum percentiles for clipping.
    vmax : scalar
        Maximum percentile for clipping.

    Returns
    -------
    data : ndarray of scalars
        Clipped and scaled data.

    """
    # logarithimically scale
    data = np.log10(data)

    # percentile clip
    cut = np.nanpercentile(data, vmin)
    data[data < cut] = cut
    cut = np.nanpercentile(data, vmax)
    data[data > cut] = cut

    # set minimum value to zero
    data = data - np.nanmin(data)

    # set maximum value to one
    data = data / np.nanmax(data)
    return data

def knownreg(db, outfile, catalogs, gname, imsize, section):
    """
    Returns a catalog of known HII Regions based off the names
    given in the config.ini file. Similar to the wise_demo.py
    precursor file created by Trey Wenger.

    Parameters
    ----------
    db : string
        Filename to the HII Region/SNR/PNe database.
    outfile : string
        Directory where downloaded FITS and PNG images are saved.
    catalogs : list of strings
        List of catalogs from which to pull the data from
        (e.g. WISE 3.4, WISE 12, etc.).
    gname : string
        Source name or list of source names. Images are saved to
            f"{outdir}/{gname}_wise.fits", etc..
    imsize : scalar (deg)
        Image cutout size.
    section : string
        Section of the config.ini file that determines either PNe,
        SNR, or HII Region catalog.

    Raises
    ------
    ValueError
        Raised when the HII Region given isn't a part 
        of the known HII Regions or HII Region Candidates.

    Returns
    -------
    None.

    """
    if section == 'knownregion':
        # Get the WISE Catalog data
        catalog = get_wise_catalog(db)
            
    elif section == 'SNRcatalog':
        # Get the SNR catalog data
        catalog = np.genfromtxt(db,skip_header=38,delimiter = ";",
                                dtype=[('gname', '<U16'), ('ra', '<U16'), 
                                       ('dec', '<U16'),])
    
    elif section == 'PNecatalog':
        # Get the PNe catalog data
        catalog = np.genfromtxt(db,skip_header=37,delimiter = ";",
                                dtype=[('gname', '<U16'), ('ra', '<U16'),
                                       ('dec', '<U16'),])
    
    if gname == 'all':
        names = catalog['gname']
    elif len(gname.split(',')) > 1:
        names = gname.split(',')
    else:
        names = [gname]
    for name in names:
         # Verify source is in the catalog (given that gname != 'all')
        row = catalog[catalog["gname"] == name]
        
        # Since PNe catalog may have a space at the end of the source name,
        # this will stop the code from crashing on the last source in a 
        # given list
        if len(name) == 0:
            continue
        rowra = row['ra'][0]
        rowdec = row['dec'][0]
        
        if len(row) == 0:
            raise ValueError(f"{gname} not found in catalog!")
        
        if (section == 'PNecatalog') or (section == 'SNRcatalog'):
            coord = str(rowra)+' '+str(rowdec)
            print(coord)
            rowra, rowdec = getcoords(coord,framekwarg='icrs')
        
        # Get WISE infrared data
        wise_3, wise_12, wise_22 = get_images(
            name, rowra, rowdec, imsize, catalogs, outfile)
        
        # For failed download from get_images(), moves to next item 
        # in list
        if wise_3 == 'fail':
            continue
    
        # Clip and scale infrared data
        image_r = scale(wise_22.data, 10.0, 99.0)
        image_g = scale(wise_12.data, 10.0, 99.5)
        image_b = scale(wise_3.data, 10.0, 99.5)
        image = np.stack([image_r, image_g, image_b], axis=-1)
    
        # Generate figure
        fig = plt.figure()
        wcs = WCS(wise_3.header).celestial
        ax = plt.subplot(projection=wcs)
        ax.imshow(image, origin="lower", interpolation="none")
        ax.set_xlabel("RA (J2000)")
        ax.set_ylabel("Declination (J2000)")
# =============================================================================
#       get pixel position of the WISE Catalog source
#       xpos, ypos = wcs.wcs_world2pix(row["ra"], row["dec"], 1)
#       radius = row["radius"] / 3600.0 / wise_3.header["CDELT2"]
#       circle = Circle(
#           (xpos, ypos), radius, fill=False,
#           linestyle="dashed", color="yellow")
#       ax.add_artist(circle)
# =============================================================================
        fig.savefig(outfile+name+'_wise.png', bbox_inches="tight")
        plt.close(fig)
    
def get_images(gname, ra, dec, size, catalogs, outdir):
    """
    Return the data in a given catalog (or catalogs) for a given sky
    position. Automated version based off code originally created
    by Trey Wenger.

    Parameters
    ----------
    gname : string
        Source name. Images are saved to
            f"{outdir}/{gname}_{catalog}.fits", etc..
    ra : scalar (deg)
        Cental sky position (J2000).
    dec : scalar (deg)
        Cental sky position (J2000).
    size : scalar (deg)
        Image cutout size.
    catalogs : list of strings
        List of catalogs from which to pull the data from
        (e.g. WISE 3.4, WISE 12, etc.).
    outdir : string
        Directory where downloaded FITS images are saved.

    Returns
    -------
    list : list of strings or list of astropy.fits.HDU objects
        Either a lis t of strings if the download from SkyView 
        fails or a list of FITS HDUs.

    """
    if not os.path.exists(outdir):
        os.mkdir(outdir)

    # SkyView occasionally fails, so we attempt multiple downloads
    success = False
    count = 0
    while not success:
        if count > 0:
            # Due to bug in astroquery.SkyView, a failed download is
            # cached and the cache directory must be deleted before
            # a new attempt is made
            shutil.rmtree(SkyView.cache_location)
            os.mkdir(SkyView.cache_location)
        if count > 10:
            print(f"Exceeded download attempt limit for {gname}")
            return 'fail','fail','fail'
        try:
            hdus = []
            for it,cat in enumerate(catalogs):
                fname = os.path.join(outdir, f'{gname}_'+cat.split(' ')[0]+cat.split(' ')[1]+'.fits')
                # Still dependent on the spaces in between eg WISE 22,
                # will need to determine if this needs to be changed
        
                # attempt to acquire hdu of the given coordinates
                # Each pixel is 4" across for WISE 22 micron
                images = SkyView.get_images(
                    position=f"{ra:.3f}, {dec:.3f}", coordinates="J2000",
                    pixels=900, width=size*u.deg, survey=cat)
                hdus.append(images[0][0])
                images[0][0].writeto(fname, overwrite=True)

            # success
            success = True
        except:
            count += 1
            time.sleep(0.2)    
    return hdus

def noregion(ra,dec,wise_catalog,imsize):
    """
    A sort of "self-checker" to make sure that no HII Regions
    lie within the image of the non-HII Region data. Incorporates
    the size of the HII Regions as listed in the WISE Catalog.

    Parameters
    ----------
    ra : float
        The right ascension at the center of the frame.
    dec : float
        The declination at the center of the frame.
    db : string
        Filename to the HII Region database.
    imsize : string
        The size in degrees of horizontal and vertical axes of
        the image.

    Returns
    -------
    string
        Returns either 'Regions' or 'Good' based on whether there
        were HII Regions in the dataframe (Regions) or not (Good).

    """
    imsize = float(imsize)
    # Finding all the HII Regions whose radius may make them appear
    # in the frame of a non-HII Region image
    rows = wise_catalog[((wise_catalog['ra']-wise_catalog['radius']/3600) < (ra+imsize/2)) & ((wise_catalog['ra']+wise_catalog['radius']/3600) > (ra-imsize/2)) & ((wise_catalog['dec']-wise_catalog['radius']/3600) < (dec+imsize/2)) & ((wise_catalog['dec']+wise_catalog['radius']/3600) > (dec-imsize/2))]
    
    # If in the frame return 'Regions', otherwise 'Good'
    if len(rows) > 0:
        print('\nRegions in frame')
        print(rows)
        print(ra,' ',dec)
        return 'Regions'
    else:
        print('\nNo Regions in frame')
        return 'Good'

def main(section,config_location):
    """
    Generate a WISE infrared three-color catalog containing
    WISE HII Regions.

    Parameters
    ----------
    section : string
        Specfic section of the config file to be used, determining
        what catalog will be generated.
    config_location : string
        Directory of the location of the config.ini file.

    Returns
    -------
    None.

    """
    #Read config.ini file
    clock = time.time()
    config_object = ConfigParser()
    config_object.read(config_location)
    config = config_object[section]
    dims = [float(config['imsize']),float(config['imsize'])]
    catalogs = config['catalogs'].split(',')
    
    # Creating the catalog of known HII Regions
    if (section == 'knownregion') or (section == 'PNecatalog') or (section == 'SNRcatalog'):
        knownreg(config['db'], config['outputdir'], catalogs, config['gname'],
                 config['imsize'], section)
        
    else:
        # Grabbing central coordinates of images of a set size of 
        # the entire Galaxy without checking what is in the images
        if section == 'Allskyparams':
            l_list = np.arange(0,360,dims[0])+dims[0]/2
            b_list = np.arange(-90,90,dims[1])+dims[1]/2
            ll,bb = np.meshgrid(l_list,b_list)
            ls = ll.flatten()
            bs = bb.flatten()
            string = 'A'
        
        # Grabbing central coordinates of images in a specific 
        # subsection of the Galaxy
        elif (section == 'baseparams') or (section == 'noregion'):
            upperglong = float(config['glongmax'])
            lowerglong = float(config['glongmin'])
            upperglat = float(config['glatmax'])
            lowerglat = float(config['glatmin'])
            l_list = np.arange(lowerglong,upperglong,dims[0])+dims[0]/2
            b_list = np.arange(lowerglat,upperglat,dims[1])+dims[1]/2
            ll,bb = np.meshgrid(l_list,b_list)
            ls = ll.flatten()
            bs = bb.flatten()
            
            # Not checking what is in the images of this specfic 
            # subsection
            if section == 'baseparams':
                string = 'A'
            
            # Verifying that there are no HII Regions in this specific
            # subsection to create the catalog of non-HII Regions
            else:
                string = 'NR'
                catalog = get_wise_catalog(config['db'])
        
        # Grabbing central coordinates of images based on coordinates
        # given in the config.ini file
        elif section == 'coords':
            ls = [config['glong']]
            bs = [config['glat']]
            string = 'NG'
        
        # Stepping through each central coordinate from which an image
        # will be created
        for it,(l,b) in enumerate(zip(ls,bs)):    
            # convert galactic longitude and latitude to RA and Dec
            radec = getcoords([l,b])
            
            # determines if there are HII Regions in the bounds of the
            # image and if so moves to the next item in list
            if section == 'noregion':
                ans = noregion(radec[0],radec[1],catalog,config['imsize'])
                if ans == 'Regions':
                    continue
                
            # obtain the hdus for the given coordinates from 
            # the given catalogs
            if float(b) >= 0:
                gname = string+str(l)+'+'+str(b)
            else:
                gname = string+str(l)+str(b)
            hdu_list = get_images(
            gname, radec[0], radec[1], dims[0], catalogs, config['outputdir'])
            
            # For failed download from get_images(), moves to next item 
            # in list
            if hdu_list[0] == 'fail':
                continue
        
            # Clip and scale infrared data
            frames = []
            
            for it,hdu in enumerate(hdu_list[::-1]):
                # Unused method of replacing the NaNs in data with a constant
                # hdu.data = np.where(np.isnan(hdu.data),10000,hdu.data)
                
                frames.append(scale(hdu.data, 10.0, 95.0))
                
                # Just a sanity check on which images contained NaNs.
                # for num,i in enumerate(hdu.data[0]):
                #     if np.isnan(i):
                #         print('listnumber:',it,'index:',num)
            image = np.stack(frames, axis=-1)
        
            # Generate figure
            fig = plt.figure()
            wcs = WCS(hdu_list[0].header).celestial
            ax = plt.subplot(projection=wcs)
            ax.imshow(image, origin="lower", interpolation="none")
            ax.set_xlabel("RA (J2000)")
            ax.set_ylabel("Declination (J2000)")
            fig.savefig(config['outputdir']+gname+'_'+catalogs[0].split(' ')[0]+'.png',
                        bbox_inches="tight")
            plt.close(fig)
    print('Elapsed time',time.time() - clock)
    
if __name__ == '__main__':
# =============================================================================
#     Code to run displayregion.py from author's database example:
#     python displayregion.py 'D:/githubfiles/ASTR490/ml/config.ini' noregion
# 
#     Where
# 
#     str(sys.argv[1]) = 'D:/githubfiles/ASTR490/ml/config.ini'
#     str(sys.argv[2]) = e.g. noregion, baseparams, etc. 
# =============================================================================

    main(str(sys.argv[2]),str(sys.argv[1]))