from astropy.table import QTable
from astropy import units as u
import astropy_healpix as ah
import numpy as np

skymap = QTable.read('bayestar.multiorder.fits')
skymap.sort('PROBDENSITY', reverse=True)
level, ipix = ah.uniq_to_level_ipix(skymap['UNIQ'])
pixel_area = ah.nside_to_pixel_area(ah.level_to_nside(level))
prob = pixel_area * skymap['PROBDENSITY']
cumprob = np.cumsum(prob)
i = cumprob.searchsorted(0.9)
area_90 = pixel_area[:i].sum()
area=area_90.to_value(u.deg**2)

print(area)