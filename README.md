# ASTR490
Creating a deep learning algorithm with the goal of classifying HII Regions using
the WISE Catalog.

configcreator.py creates the config.ini file that can be read into to a script
containing all of the parameters required to build a catalog of images for the
machine learning (ML) code to use as the test catalog.

config.ini contains multiple sections for the different ways to produce either a
singular image based off coordinates or a known WISE Catalog HII Region name, or a
catalog based on the entire sky or a specific subsection specified in the file.

The config.ini file will need to be updated to match the directory of the location
of the database ("'db'") and the output directory ("'outputdir'") for the device it
is running on.

displayregion.py implements the config.ini file to create either the singular image
or catalog of images to be used as the test/dev set by the ML code. The actual pixel
values for flux can be returned in the form of .fits files, and a 3-color image is
returned in the form of a .pdf file.

the ml folder is meant to be a package that can be imported into python scripts if
need be. Therefore to run it, runner.py is used. To use the different keywords in 
the config.ini file and create a different catalog or image of HII Regions, runner.py
must be updated by changing the parameter passed into main()

[baseparams]
Type "'baseparams'" as the parameter for main() in runner.py and the code will run 
creating images that are 1 degree of galactic longitude by 1 degree of galactic 
latitude in between the coordinates (301,-1) and (305,1). The images are produced
using the WISE Catalog in the 3.4, 12, and 22 micron filters.

[knownregion]
Type "'knownregion'" as the parameter for main() in runner.py and the code will
create an image of the HII Region given in the "gname" parameter spot of the
config.ini file. These images are also 1 degree of galactic longitude by 1 degree
of galactic latitude. Currently does not work for automation or multiple inputs at
the same time. The images are produced using the WISE Catalog in the 3.4, 12, and
22 micron filters.

[Allskyparams]
Type "'Allskyparams'" as the parameter for main() in runner.py and the code will run 
creating images that are 1 degree of galactic longitude by 1 degree of galactic 
latitude for the entire sky. The images are produced using the WISE Catalog in the
3.4, 12, and 22 micron filters.

[coords]
Type "'Allskyparams'" as the parameter for main() in runner.py and the code will
create an image centered on the coordinates given in the config.ini file. Currently
does not work for automation or multiple inputs at the same time. The images are
produced using the WISE Catalog in the 3.4, 12, and 22 micron filters.

Future adaptations are going to be adding a feature that will randomize the location
of an HII Region in the frame to not bias the convolutional neural network and making
the code generate a catalog of HII Regions to train with automatically ([knownregion]
in the config.ini file). Also, will be looking to add a function that will return
space that does not contain an HII Region by picking a spot and making sure no HII
Regions lie in that spot based off their size and central coordinates. (verify that 
randomly selecting a spot will be the quickest method.)

Code needs commenting and to be completed as of this commit.

