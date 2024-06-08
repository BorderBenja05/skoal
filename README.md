# SKOAL (scheduling kilonovae algebraic lightweight)
A lightweight, comprehensive scheduling package built for ultrafast follow-up observations of FERMI notices and LVC notices. I originally built this for the TURBO project so it's optimized for an array of telescope mounts requiring subsecond scheduling times.


PACKAGING IN PROGRESS,
email Borderbenja@gmail.com for questions

The code can currently:
- interact with gracedb to download and read skymaps
- read and produce telescope configuration files
- create an moc tiling for square and nonsquare telescope footprints of arbitrary dimensions
- produce probability ordered target list of observable targets for given FERMI and LVC notices
- divide target list based on clusters or probability for arbitrarily sized telescope array

Planned improvements:
- add other tiling methods(Shaon's method)
- coordination between multiple telescope arrays
- add option to use balltree and compare method times
- implement algebraic option for fermi notices


Related repositories:
- https://github.com/shaonghosh/sky_tiling.git 
- https://github.com/mcoughlin/gwemopt
