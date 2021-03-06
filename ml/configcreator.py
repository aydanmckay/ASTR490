# -*- coding: utf-8 -*-
"""
Created on Fri Jul  2 12:06:45 2021

@author: aydan
"""

from configparser import ConfigParser

def main():
    #Get the configparser object
    config_object = ConfigParser()
    
    # create (so far) 4 sections of the config file such that I only need to
    # change the section being being used to change how the program operates.
    config_object['baseparams'] = {
        'db': 'D:/dataverse_files/v2/hii_v2_20201203.db',
        'outputdir': 'D:/ASTR490/Catalog/',
        'imsize': '0.5',
        'Allsky': '0',
        'glongmax': '305',
        'glongmin': '301',
        'glatmax': '1',
        'glatmin': '-1',
        'gname': 'None',
        'glong': '361',
        'glat': '0',
        'catalogs': 'WISE 3.4,WISE 12,WISE 22'
    }
    
    config_object['Allskyparams'] = {
        'db': 'D:/dataverse_files/v2/hii_v2_20201203.db',
        'outputdir': 'D:/ASTR490/Allskyfolder/',
        'imsize': '0.5',
        'Allsky': '1',
        'glongmax': '0',
        'glongmin': '0',
        'glatmax': '0',
        'glatmin': '0',
        'gname': 'None',
        'glong': '361',
        'glat': '0',
        'catalogs': 'WISE 3.4,WISE 12,WISE 22'
    }
    
    config_object['coords'] = {
        'db': 'D:/dataverse_files/v2/hii_v2_20201203.db',
        'outputdir': 'D:/ASTR490/randcoords/',
        'imsize': '0.5',
        'Allsky': '0',
        'glongmax': '0',
        'glongmin': '0',
        'glatmax': '0',
        'glatmin': '0',
        'gname': 'None',
        'glong': '0.31', 
        'glat': '0.02',
        'catalogs': 'WISE 3.4,WISE 12,WISE 22'
    }
    
    config_object['noregion'] = {
        'db': 'D:/dataverse_files/v2/hii_v2_20201203.db',
        'outputdir': 'D:/ASTR490/noregions/',
        'imsize': '0.5',
        'Allsky': '0',
        'glongmax': '317',
        'glongmin': '313',
        'glatmax': '2',
        'glatmin': '0',
        'gname': 'None',
        'glong': '361', 
        'glat': '0',
        'catalogs': 'WISE 3.4,WISE 12,WISE 22'
    }
    
    config_object['knownregion'] = {
        'db': 'D:/dataverse_files/v2/hii_v2_20201203.db',
        'outputdir': 'D:/ASTR490/knownreg/',
        'imsize': '0.5',
        'Allsky': '0',
        'glongmax': '0',
        'glongmin': '0',
        'glatmax': '0',
        'glatmin': '0',
        # gname can equal 'all' which will create a catalog of every known HII
        # Region
        'gname': 'G297.651-00.973,G114.526-00.543,G247.467+02.181,G301.489+00.125,G052.750+00.334',
        'glong': '361',
        'glat': '0',
        'catalogs': 'WISE 3.4,WISE 12,WISE 22' # Make the known region catalog
        # options fixed
    }
    
    config_object['SNRcatalog'] = {
        'db': 'D:/githubfiles/ASTR490/SNRcatalog.tsv',
        'outputdir': 'D:/ASTR490/SNRs/',
        'imsize': '0.5',
        'Allsky': '0',
        'glongmax': '317',
        'glongmin': '313',
        'glatmax': '2',
        'glatmin': '0',
        # can be equal to 'all' or as above (knownregion)
        'gname': 'G011.1-01.0',
        'glong': '361', 
        'glat': '0',
        'catalogs': 'WISE 3.4,WISE 12,WISE 22'
    }
    
    config_object['PNecatalog'] = {
        'db': 'D:/githubfiles/ASTR490/PNecatalog.tsv',
        'outputdir': 'D:/ASTR490/PNe/',
        'imsize': '0.5',
        'Allsky': '0',
        'glongmax': '317',
        'glongmin': '313',
        'glatmax': '2',
        'glatmin': '0',
        # can be equal to 'all' or as above (knownregion)
        # PNe catalog has space at the end of most names, add
        # a comma after even if last name in list
        'gname': '060-03.1 ,198-06.1 ,240-07.1 ,',
        'glong': '361', 
        'glat': '0',
        'catalogs': 'WISE 3.4,WISE 12,WISE 22'
    }
    
    #Write the above sections to config.ini file
    with open('D:/githubfiles/ASTR490/ml/config.ini', 'w') as conf:
        config_object.write(conf)

if __name__ == "__main__":
    main()