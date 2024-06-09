# SKOAL (scheduling kilonovae algebraic linear)
A lightweight, comprehensive scheduling package built for ultrafast follow-up observations of FERMI notices and LVC notices. I originally built this for the TURBO project so it's optimized for an array of telescope mounts requiring subsecond scheduling times. Because this was built with speed in mind, algebraic reverse tile lookups are used in favor of tree(balltree, kdtree) based approaches, meaning it is truly linear!


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
- add other tiling methods(Shaon's method)
- coordination between multiple telescope arrays
- add option to use balltree and compare method times
- implement algebraic option for fermi notices
- implement cluster based array splitting option


Related repositories:
- https://github.com/shaonghosh/sky_tiling.git 
- https://github.com/mcoughlin/gwemopt
