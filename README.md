# ASTR490
Creating a deep learning algorithm with the goal of classifying HII Regions using
the WISE Catalog.

configcreator.py creates config.ini file that can be read into to a script containing
all of the parameters required to build a catalog of images for the machine learning
(ML) code to use as the test catalog.

config.ini contains multiple sections for the different ways to produce either a
singular image based off coordinates or a known WISE Catalog HII Region name, or a
catalog based on the entire sky or a specific subsection specified in the file.

displayregion.py implements the config.ini file to create either the singular image or
catalog of images to be used as the test/dev set by the ML code. The actual pixel
values for flux can be returned in the form of .fits files, and a 3-color image is
returned in the form of a .pdf file.

Future adaptations are going to be adding a feature that will randomize the location
of an HII Region in the frame to not bias the convolutional neural network and making
the code generate a catalog of HII Regions to train with automatically ([knownregion]
in the config.ini file). Also, will be looking to add a function that will return
space that does not contain an HII Region by picking a spot and making sure no HII
Regions lie in that spot based off their size and central coordinates. (verify that 
randomly selecting a spot will be the quickest method.)

