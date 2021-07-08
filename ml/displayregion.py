# -*- coding: utf-8 -*-
"""
Created on Wed Jun 16 17:05:00 2021

@author: aydan
"""

import os
import numpy as np
import pandas as pd
import sqlite3
import shutil
import astropy.units as u
from astroquery.skyview import SkyView
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from astropy.wcs import WCS
from astropy.coordinates import SkyCoord
import time
from configparser import ConfigParser

def get_wise_catalog(db):
    """
    Return a pandas dataframe containing relevant data from
    the WISE Catalog.

    Inputs:
        db :: string
            Filename to the HII region database

    Returns: data
        data :: pandas.DataFrame
            DataFrame containing the WISE Catalog data
    """
    with sqlite3.connect(db) as conn:
        cur = conn.cursor()
        cur.execute("PRAGMA foreign_keys = ON")
        cur.execute("SELECT gname, ra, dec, radius FROM Catalog")
        data = pd.DataFrame(
            cur.fetchall(), columns=[d[0] for d in cur.description])
    return data

def getcoords(coords):
    """
    Convets user inputted galactic coordinates to RA and Dec.

    Parameters
    ----------
    coords : list of strings
        The coordinates in Galactic coordinates inputted by the user.

    Returns
    -------
    newcoords : list of strings
        The coordinates in RA and Dec.
    """
    
    skycoordthing = SkyCoord(frame='galactic', l=coords[0],
                             b=coords[1], unit='deg').icrs
    newcoords = [skycoordthing.ra.deg,skycoordthing.dec.deg]
    
    return newcoords


def scale(data, vmin, vmax):
    """
    Clip and logarithmically scale some data.

    Inputs:
        data :: ndarray of scalars
            Data to clip and scale
        vmin, vmax :: scalars
            Minimum and maximum percentiles for clipping

    Returns: newdata
        newdata :: ndarray of scalars
            Clipped and scaled data
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

def knownreg(db, outfile, catalogs, gname):
    # Get the WISE Catalog data
    wise_catalog = get_wise_catalog(db)

    # Get WISE infrared data
    row = wise_catalog.loc[wise_catalog["gname"] == gname]
    if len(row) == 0:
        raise ValueError(f"{gname} not found in WISE Catalog!")
    row = row.iloc[0]
    # image size is three times larger than source radius
    imsize = 3.0 * row["radius"]/3600.0
    wise_3, wise_12, wise_22 = get_images(
        gname, row["ra"], row["dec"], imsize, catalogs, outfile)

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
    # get pixel position and radius of the WISE Catalog source
    xpos, ypos = wcs.wcs_world2pix(row["ra"], row["dec"], 1)
    radius = row["radius"] / 3600.0 / wise_3.header["CDELT2"]
    circle = Circle(
        (xpos, ypos), radius, fill=False,
        linestyle="dashed", color="yellow")
    ax.add_artist(circle)
    fig.savefig(outfile+gname+'_wise.pdf', bbox_inches="tight")
    plt.close(fig)
    
def get_images(gname, ra, dec, size, catalogs, outdir):
    """
    Return the WISE 3.4, 12, and 22 micron data for a given sky
    position. Automatic version.

    Inputs:
        gname :: string
            Source name. Images are saved to
            f"{outdir}/{gname}_wise_3.4.fits", etc.
        ra, dec :: scalars (deg)
            Cental sky position (J2000)
        size :: scalar (deg)
            Image cutout size
        outdir :: string
            Directory where downloaded FITS images are saved

    Returns: wise_3, wise_12, wise_22
        wise_3, wise_12, wise_22 :: astropy.fits.HDU
            The WISE 3.4, 12, and 22 micron FITS HDUs
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
            hdus = [] # Want to use array here calling np.zeros but unsure of
            # hdu data type.
            for it,cat in enumerate(catalogs):
                # fname = os.path.join(outdir, f'{gname}_'+cat.split(' ')[0]+cat.split(' ')[1]+'.fits')
                # Still dependent on the spaces in between eg WISE 22, will need to determine if this
                # needs to be more general.
                
                images = SkyView.get_images(
                    position=f"{ra:.3f}, {dec:.3f}", coordinates="J2000",
                    pixels=1024, width=size*u.deg, survey=cat)
                hdus.append(images[0][0])
                # images[0][0].writeto(fname, overwrite=True)

            # success
            success = True
        except:
            count += 1
            time.sleep(0.2)
            
    return hdus


# def main(db, outfile, gname = 'None', coords = [361,0], dims = [0,0], Allsky = True):
def main(section):
    """
    Generate a WISE infrared three-color catalog containing WISE HII Regions.

    Inputs:
        section :: string
            specfic section of the config file to be used, 
            determining what catalog will be generated

    Returns: Nothing
    """
    
    #Read config.ini file
    config_object = ConfigParser()
    config_object_file = 'C:/Users/aydan/OneDrive/Documents/UVic_2021/Astr 490/ml/config.ini'
    config_object.read(config_object_file)
    config = config_object[section] #######################################
    dims = [float(config['imsize']),float(config['imsize'])]
    catalogs = config['catalogs'].split(',')
    
    if config['gname'] != 'None':
        knownreg(config['db'], config['outputdir'], catalogs, config['gname'])
        
    if dims[0] != 0:
        if bool(int(config['Allsky'])) == True:
            # startTime = time.time()
            l_list = np.arange(0,360,dims[0])+dims[0]/2
            b_list = np.arange(-90,90,dims[1])+dims[1]/2
            ll,bb = np.meshgrid(l_list,b_list)
            ls = ll.flatten()
            bs = bb.flatten()
            for it,(l,b) in enumerate(zip(ls,bs)):    
                radec = getcoords([l,b])
                gname = 'A'+str(l)+str(b)
                hdu_list = get_images(
                gname, radec[0], radec[1], dims[0], catalogs, config['outputdir'])
                
                # originally checking for wise_3 = 'fail', should still work
                if hdu_list[0] == 'fail':
                    continue
            
                # Clip and scale infrared data
                
                frames = []
                # same issue as for the hdus in the get_images function
                
                # Can definitely vectorize this loop.
                for hdu in hdu_list:
                    frames.append(scale(hdu.data, 10.0, 99.5))
                # image_r = scale(wise_22.data, 10.0, 99.0)
                # image_g = scale(wise_12.data, 10.0, 99.5)
                # image_b = scale(wise_3.data, 10.0, 99.5)
                image = np.stack(frames, axis=-1)
            
            
                # Generate figure
                fig = plt.figure()
                wcs = WCS(hdu_list[0].header).celestial
                ax = plt.subplot(projection=wcs)
                ax.imshow(image, origin="lower", interpolation="none")
                ax.set_xlabel("RA (J2000)")
                ax.set_ylabel("Declination (J2000)")
                fig.savefig(config['outputdir']+gname+'_'+catalogs[0].split(' ')[0]+'.pdf',
                            bbox_inches="tight")
                plt.close(fig)
                # executionTime = (time.time() - startTime)
                # print('Execution time in seconds: ' + str(executionTime))
                # break
            
            
        if bool(int(config['Allsky'])) == False:
            upperglong = float(config['glongmax'])
            lowerglong = float(config['glongmin'])
            upperglat = float(config['glatmax'])
            lowerglat = float(config['glatmin'])
            l_list = np.arange(lowerglong,upperglong,dims[0])+dims[0]/2
            b_list = np.arange(lowerglat,upperglat,dims[1])+dims[1]/2
            ll,bb = np.meshgrid(l_list,b_list)
            ls = ll.flatten()
            bs = bb.flatten()
            for it,(l,b) in enumerate(zip(ls,bs)):  
                # startTime = time.time()
                radec = getcoords([l,b])
                gname = 'A'+str(l)+str(b)
                hdu_list = get_images(
                gname, radec[0], radec[1], dims[0], catalogs, config['outputdir'])
                if hdu_list[0] == 'fail':
                    continue
            
                # Clip and scale infrared data
                
                # see above
                frames = []
                for hdu in hdu_list:
                    frames.append(scale(hdu.data, 10.0, 99.5))
                # image_r = scale(wise_22.data, 10.0, 99.0)
                # image_g = scale(wise_12.data, 10.0, 99.5)
                # image_b = scale(wise_3.data, 10.0, 99.5)
                image = np.stack(frames, axis=-1)
            
            
                # Generate figure
                fig = plt.figure()
                wcs = WCS(hdu_list[0].header).celestial
                ax = plt.subplot(projection=wcs)
                ax.imshow(image, origin="lower", interpolation="none")
                ax.set_xlabel("RA (J2000)")
                ax.set_ylabel("Declination (J2000)")
                fig.savefig(config['outputdir']+gname+'_'+catalogs[0].split(' ')[0]+'.pdf',
                            bbox_inches="tight")
                plt.close(fig)
                # executionTime = (time.time() - startTime)
                # print('Execution time in seconds: ' + str(executionTime))
                # break
        
    if float(config['glong']) != 361:
        
        # Get the WISE Catalog data
        wise_catalog = get_wise_catalog(config['db'])
    
        # Get WISE infrared data
        row = wise_catalog.loc[wise_catalog["gname"] == 'G'+config['glong']+config['glat']]
        if len(row) != 0:
            print('Actually a known HII Region!')
            gname = 'G'+config['glong']+config['glat']
            knownreg(config['db'], config['outputdir'], catalogs, gname)
        
        else:
            gname = 'NG'+config['glong']+config['glat']
            radec = getcoords([config['glong'],config['glat']])
            
            imsize = config['regionsize']
            
            hdu_list = get_images(
                gname, radec[0], radec[1], imsize, catalogs, config['outputdir'])
            
            # Clip and scale infrared data
            # see above
            frames = []
            for hdu in hdu_list:
                frames.append(scale(hdu.data, 10.0, 99.5))
            # image_r = scale(wise_22.data, 10.0, 99.0)
            # image_g = scale(wise_12.data, 10.0, 99.5)
            # image_b = scale(wise_3.data, 10.0, 99.5)
            image = np.stack(frames, axis=-1)
            
            
            # Generate figure
            fig = plt.figure()
            wcs = WCS(hdu_list[0].header).celestial
            ax = plt.subplot(projection=wcs)
            ax.imshow(image, origin="lower", interpolation="none")
            ax.set_xlabel("RA (J2000)")
            ax.set_ylabel("Declination (J2000)")
            fig.savefig(config['outputdir']+gname+'_'+catalogs[0].split(' ')[0]+'.pdf',
                            bbox_inches="tight")
            plt.close(fig)
            
    
# if __name__ == "__main__":
#     main()
    
# =============================================================================
#     gnamechecker = True
#     while gnamechecker:
#         batchcontrol = input('Automatically create image catalog? (y/n): ')
#         if batchcontrol == 'y':
#             print('Image Dimensions (For now choose factors of 360)')
#             dim_l = float(input('...For Galactic Longitude?: '))
#             dim_b = float(input('...For Galactic Latitude?: '))
#             dims = [dim_l,dim_b]
#             skycoverage = input('All sky? (Type \"y\" for total sky coverage): ')
#             allsky = True
#             if skycoverage != 'y':
#                 allsky = False   
#             main("D:/dataverse_files/v2/hii_v2_20201203.db",
#                   "D:/ASTR490/",
#                   dims = dims, Allsky=allsky)
#             break
#         elif batchcontrol != 'n':
#             print('Invalid input...')
#             continue
#         boolregion = input('Known HII Region? (y/n): ')
#         if boolregion == 'y':
#             gname = input('Name of the region: ')
#             main("D:/dataverse_files/v2/hii_v2_20201203.db",
#                   "C:/Users/aydan/OneDrive/Documents/UVic_2021/Astr 490/",
#                   gname = gname)
#             gnamechecker = False
#         elif boolregion == 'n':
#             coordsstring = input('Galactic Coordinates? (l [###.###],b [+/-##.###]): ')
#             main("D:/dataverse_files/v2/hii_v2_20201203.db",
#                   "C:/Users/aydan/OneDrive/Documents/UVic_2021/Astr 490/",
#                   coords = coordsstring.split(','))
#             gnamechecker = False
#         else:
#             print('Invalid input...')
# =============================================================================