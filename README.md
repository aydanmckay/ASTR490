# ASTR490
Creating a deep learning algorithm with the goal of identifying HII Regions in
the WISE Catalog.

configcreator.py creates the config.ini file that can be read into to a script
containing all of the parameters required to build a catalog of images for the
machine learning (ML) code to use as the test catalog.

config.ini contains multiple sections for the different ways to produce images. 
The options are producing a catalog of the entire sky without specifying what
is contained in the images, a catalog of a subsection of the sky without specifying
what is contained in the images, a catalog of known HII Regions, a catalog based on
coordinates given in the file, and a catalog verified to be containing no HII 
Regions. These are separated into sections easily identifiable in the file

The config.ini file will need to be updated to match the directory of the location
of the database ("'db'") and the output directory ("'outputdir'") for the device it
is running on. *** Need to change the config_object_file parameter in main() from
displayregion.py to where the config file is located as well ***

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
creating images that are 0.25 square degrees between the coordinates (301,-1) and 
(305,1) (in galactic longitude and latitude). The images are produced using the WISE
Catalog in the 3.4, 12, and 22 micron filters.

[knownregion]
Type "'knownregion'" as the parameter for main() in runner.py and the code will
create an image of the HII Region given in the "gname" parameter spot of the
config.ini file. These images are also 1 degree of galactic longitude by 1 degree
of galactic latitude. The images are produced using the WISE Catalog in the 3.4, 12, and
22 micron filters.

[Allskyparams]
Type "'Allskyparams'" as the parameter for main() in runner.py and the code will run 
creating images that are 0.25 square degrees for the entire sky. The images are produced 
using the WISE Catalog in the 3.4, 12, and 22 micron filters.

[coords]
Type "'Allskyparams'" as the parameter for main() in runner.py and the code will
create an image centered on the coordinates given in the config.ini file. Currently
does not work for automation or multiple inputs at the same time. The images are
produced using the WISE Catalog in the 3.4, 12, and 22 micron filters.

[noregion]
Type "'noregion'" as the parameter for main() in reunner.py and the code with create
a catalog containing no HII Regions in 0.25 square degree images of a subsection of
the sky. This subsection is (308,0) to (312,2) in galactic longitude and latitude.
The images are produced using the WISE Catalog in the 3.4, 12, and 22 micron filters.

Future adaptations are going to be adding a feature that will randomize the location
of an HII Region in the frame to not bias the convolutional neural network and making
the code generate a catalog of HII Regions to train with automatically ([knownregion]
in the config.ini file).

Automation for [knownregion] added tentatively. For automation, HII Regoin names must 
be inserted manually (Will be drawn from the WISE Catalog in future version of code)
and in the format shown for the 5 Regions already appearing in the config.ini file.

*In Progress/Recent Updates*
~Updated runner.py to take the kwargs from the cmd, commented the script with reminders
for my specific device.
~Switched output PDF files to PNG files.
~Removed hardcoded location of config.ini file (see first point)
~"Fixed" colours of the output images
~Changed file names for sources with positive galactic latitudes to be more readable
~Need to account for reading in CSV files for other celestial object catalogs
~May remove runner.py entirely and add kwargs from cmd to displayregion.py
