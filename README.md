# SKOAL (scheduling kilonovae algebraic linear)
A lightweight, comprehensive scheduling package built for ultrafast follow-up observations of FERMI notices and LVC notices. I originally built this for the TURBO project so it's optimized for an array of telescope mounts requiring subsecond scheduling times. Because this was built with speed in mind, algebraic reverse tile lookups are used in favor of tree(balltree, kdtree) based approaches, meaning it is truly linear!

Author: Benny Border

PACKAGING IN PROGRESS,
email Borderbenja@gmail.com for questions

The code can currently:
- interact with gracedb to download and read skymaps
- automatically determine VOEvent notice types and handle them accordingly
- read and produce telescope configuration files
- create an moc tiling for square and nonsquare telescope footprints of arbitrary dimensions
- determine tiles needed to cover 90% confidence region
- rank 90% tiles in order of their total probability to give an initial target list
- cut target list down to observable targets
- divide target list based on probability for arbitrarily sized telescope array

Planned improvements:
- add support for updating fovs
- add other tiling methods(Shaon's method)
- coordination between multiple telescope arrays
- add option to use balltree and compare method times
- implement algebraic option for fermi notices
- implement cluster based array splitting option
- add option to return observation chance



Installation:
> pip install skoal

dont worry about making a config file for your telescope, if skoal doesn't recognize the name it will ask for all the necessary information and then make one for you!!
if you don't like the other default settings, you can either add the unincluded settings in your own config file or change the defaults by changing default.cfg

Usage example:
> skoal -t RASA11 -e S240609c -multiscopes 7

this will produce a folder of eight observable target lists, one master and 7 individual lists, for a telescope RASA11, based on the gracedb event S240609c

if you instead, have the path to a VOEvent.xml file of the event youd like to make a schedule for, use the -voe argument instead:
> skoal -t RASA11 -voe path/to/voevent.xml -multiscopes 7

and if you want to output to a specific path, just include -o your/own/outpath in your arguments

Special thanks to:
- Austin Korpi for initial prototyping help, clustering, and using dictionaries so i didn't have to
- Michael Coughlin for his excellent skymap grabber
- Pat Kelly for his labratory resources
- Mandeep Gill for his role as a test user


Related repositories:
- https://github.com/shaonghosh/sky_tiling.git 
- https://github.com/mcoughlin/gwemopt
