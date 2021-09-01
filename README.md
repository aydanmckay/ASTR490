# ASTR490
Creating a deep learning algorithm with the goal of identifying HII Regions in
the WISE Catalog.

[configcreator.py](https://github.com/aydanmckay/ASTR490/blob/main/ml/configcreator.py) creates the config.ini file that can be read into to a script
containing all of the parameters required to build a catalog of images for the
machine learning (ML) code to use as the test catalog.

[config.ini](https://github.com/aydanmckay/ASTR490/blob/main/ml/config.ini) contains multiple sections for the different ways to produce images. 
The options are producing a catalog of the entire sky without specifying what
is contained in the images, a catalog of a subsection of the sky without specifying
what is contained in the images, a catalog of known HII Regions, a catalog of 
Planetary Nebulae, a catalog of Supernova Remnants, a catalog based on
coordinates given in the file, and a catalog verified to be containing no HII 
Regions. These are separated into sections easily identifiable in the file

The config.ini file will need to be updated to match the directory of the location
of the database ("'db'") and the output directory ("'outputdir'") for the device it
is running on.

[displayregion.py](https://github.com/aydanmckay/ASTR490/blob/main/ml/displayregion.py) implements the config.ini file to create either the singular image
or catalog of images to be used as the train/test/dev set by the ML code. The actual
pixel values for flux can be returned in the form of .fits files, and a 3-color image
is returned in the form of a .png file.

runner.py has been removed and now displayregion.py can be used by itself calling
parameters from the command line pointing to where the config.ini file is and the
section of the config.ini file wished to be used to create a catalog.

[SNRcatalog.tsv](https://github.com/aydanmckay/ASTR490/blob/main/SNRcatalog.tsv) is a catalog of supernova remnants from the paper "[A revised 
catalogue of 294 Galactic supernova remnants (Green, 2019)](https://ui.adsabs.harvard.edu/abs/2019JApA...40...36G/abstract)" accessed through VizieR.

[PNecatalog.tsv](https://github.com/aydanmckay/ASTR490/blob/main/PNecatalog.tsv) is a catalog of planetary nebulae from the paper "[Version 2000 of the
Catalogue of Galactic Planetary Nebulae](https://ui.adsabs.harvard.edu/abs/2001A%26A...378..843K/abstract)" accessed through VizieR.

[baseparams]
Type "'baseparams'" as the parameter for main() in displayregion.py and the code will
run creating images that are 0.25 square degrees between the coordinates (301,-1) and 
(305,1) (in galactic longitude and latitude). The images are produced using the WISE
Catalog in the 3.4, 12, and 22 micron filters.

[Allskyparams]
Type "'Allskyparams'" as the parameter for main() in displayregion.py and the code will 
run creating images that are 0.25 square degrees for the entire sky. The images are
produced using the WISE Catalog in the 3.4, 12, and 22 micron filters.

[coords]
Type "'Allskyparams'" as the parameter for main() in displayregion.py and the code 
will create an image centered on the coordinates given in the config.ini file. Currently
does not work for automation or multiple inputs at the same time. The images are
produced using the WISE Catalog in the 3.4, 12, and 22 micron filters.

[noregion]
Type "'noregion'" as the parameter for main() in displayregion.py and the code with
create a catalog containing no HII Regions in 0.25 square degree images of a subsection
of the sky. This subsection is (308,0) to (312,2) in galactic longitude and latitude.
The images are produced using the WISE Catalog in the 3.4, 12, and 22 micron filters.

[knownregion]
Type "'knownregion'" as the parameter for main() in displayregion.py and the code will
create a catalog of images for the HII Regions given in the "gname" parameter spot of 
the config.ini file. These images are also 1 degree of galactic longitude by 1 degree
of galactic latitude. The images are produced using the WISE Catalog in the 3.4, 12, and
22 micron filters. Can have a parameter set to 'all' which will produce images for all
HII Regions in the WISE Catalog.

[SNRcatalog]
Type "'SNRcatalog'" as the parameter for main() in displayregion.py and the code will
create a catalog of images for the Supernova Remnants given in the "gname" parameter 
spot of the config.ini file. Works the same as [knownregion].

[PNecatalog]
Type "'PNecatalog'" as the parameter for main() in displayregion.py and the code will
create a catalog of images for the Planetary Nebulae given in the "gname" parameter 
spot of the config.ini file. Works the same as [knownregion] and [SNRcatalog].

Automation for [knownregion] added. For automation, HII Region names can be inserted
manually and in the format shown for the 5 Regions already appearing in the
config.ini file, or drawn from the catalog automatically.
