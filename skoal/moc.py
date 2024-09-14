from mocpy import MOC
from astropy.coordinates import Latitude, Longitude
import astropy.units as u
import astropy.io.fits as fits
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import Table
from geopy import Point                                                                                                                                                                       
from geopy.distance import geodesic 
import time
from joblib import dump, load
import os, sys


# Create a MOC
# vals = MOC.probabilities_in_multiordermap(moc, skymap)


def get_corners(dec, fov):
    # tstart = time.time()
    distKm = np.sqrt((fov[1]/2)**2 + (fov[0]/2)**2)*(np.pi/180) * 6371.009 #radius of earth
    ra = 0

    highcoords = geodesic(kilometers=distKm).destination(Point(dec, ra), 45).format_decimal()
    highcoords = tuple(map(float, highcoords.split(", ")))
    dechigh = highcoords[0]
    rastep_high = highcoords[1]

    lowcoords = geodesic(kilometers=distKm).destination(Point(dec, ra), 135).format_decimal()
    lowcoords = tuple(map(float, lowcoords.split(", ")))
    declow = lowcoords[0]
    rastep_low = lowcoords[1]
    # print(time.time() - tstart)

    return rastep_high, rastep_low, dechigh, declow

def moc_maker(tessfile, fov):
    tstart1 = time.time()
    moc_tess = []
    tess = np.loadtxt(tessfile, usecols=(1, 2))


    current_dec = None
    for i, row in enumerate(tess):

        if not row[1] == current_dec:
            ra_step_high, ra_step_low, cor_dec_high, cor_dec_low = get_corners(row[1], fov)
            current_dec = row[1]


            
        # tstart = time.time()
        ra = Longitude([row[0] + ra_step_high, row[0]-ra_step_high, row[0]-ra_step_low, row[0]+ra_step_low], u.deg)
        dec = Latitude([cor_dec_high, cor_dec_high, cor_dec_low, cor_dec_low], u.deg)
        moc = MOC.from_polygon(ra, dec)
        moc_tess.append(moc)
        # if i ==3:
        #     time1 =time.time()-tstart
        #     print(time1)
        #     moc.save('example.fits', overwrite=True)
        #     ts = time.time()
        #     moc = MOC.load('example.fits', 'fits')
            # print('this one',time.time()-ts)
    # print('now this one', time.time() - tstart1)
    return moc_tess
        

ts = time.time()
tessfile = '/home/borderbenja/skoal/skoal/data/tesselations/RASA11.tess'
fov = (3,2)
# if os.path.exists('moc_list.pkl'):
with open('moc_list.pkl', 'rb') as f:
    moc_tess = pickle.load(f)
    print(time.time()-ts)
# else:
moc_tess = moc_maker(tessfile, fov)
with open('moc_list.pkl', 'wb') as f:
    pickle.dump(moc_tess, f)




# Open the FITS file containing the skymap
filename = "/home/borderbenja/skoal/skoal/data/skymaps/S240605a_2_bayestar.multiorder.fits,1"
with fits.open(filename) as hdulist:
    # print(hdulist[1].data)
    # Extract the probability column from the first table extension
    skymap_data = Table(hdulist[1].data)

probabilities = MOC.probabilities_in_multiordermap(moc_tess, skymap_data)
print(time.time()-ts)
print(sorted(range(len(probabilities)), key=lambda k: probabilities[k], reverse=True)[:15])
# lon = Longitude([45, -45, -45, 45], u.deg)
# lat = Latitude([45, 45, -45, -45], u.deg)
# moc = MOC.from_polygon(lon, lat)

# Plot the MOC using matplotlib
# fig = plt.figure(figsize=(10, 10))
# wcs = moc.wcs(fig)
# ax = fig.add_subplot(projection=wcs)
# moc.border(ax, wcs, color='blue')
# fig.show()
# fig.savefig(f'figure.png')

# print(get_corners(45, (3, 2)))

