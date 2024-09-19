from mocpy import MOC
from astropy.coordinates import Latitude, Longitude, EarthLocation, AltAz, SkyCoord
import astropy.units as u
import astropy.io.fits as fits
import matplotlib.pyplot as plt
import numpy as np
from astropy.table import Table
from geopy import Point                                                                                                                                                                       
from geopy.distance import geodesic 
import time
import pickle
import os, sys
import datetime
from astropy.wcs import WCS
from astropy.time import Time
from astropy.visualization.wcsaxes.frame import EllipticalFrame
from plot_tiles import make_tile_plots, plotter




def observable_area(latitude, longitude, horizons, altitude=0):
        # Define location on Earth
    ts = time.time()
    location = EarthLocation(lat=latitude * u.deg, lon=longitude * u.deg, height=altitude * u.m)

    # Get the current time
    current_time = Time.now()
    
    # Define the AltAz frame for the current time and location
    altaz_frame = AltAz(obstime=current_time, location=location)
    
    # Define zenith as Altitude = 90 degrees
    zenith = SkyCoord(alt=90 * u.deg, az=0 * u.deg, frame=altaz_frame)
    # print(time.time()-ts)
    # Transform to ICRS (RA/Dec)
    zenith_icrs = zenith.transform_to('icrs')
    ra = zenith_icrs.ra.deg
    dec = zenith_icrs.dec.deg
    # print(time.time()-ts)

    horizon_ras = []
    horizon_decs = []
    for horizon in horizons:
        distKm = ((90-horizon[0])*np.pi/180) * 6371.009 #radius of earth
        coords = geodesic(kilometers=distKm).destination(Point(dec, ra), horizon[1]).format_decimal()
        coords = tuple(map(float, coords.split(", ")))
        horizon_ras.append(coords[1])
        horizon_decs.append(coords[0])
    ra = Longitude(horizon_ras, u.deg)
    dec = Latitude(horizon_decs, u.deg)
    
    observable_moc = MOC.from_polygon(ra, dec)
    # print(time.time()-ts)
    return observable_moc



    

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
        


tessfile = '/home/borderbenja/skoal/skoal/data/tesselations/RASA11.tess'
fov = (3,2)
if os.path.exists('moc_list.pkl'):
    with open('moc_list.pkl', 'rb') as f:
        ts = time.time()
        moc_tess = pickle.load(f)
        print('time spent loading file:',time.time()-ts)
else:
    moc_tess = moc_maker(tessfile, fov)
    with open('moc_list.pkl', 'wb') as f:
        pickle.dump(moc_tess, f)




# Open the FITS file containing the skymap
filename = "/home/borderbenja/skoal/skoal/data/skymaps/MS240324c_3_bayestar.multiorder.fits.gz"
with fits.open(filename) as hdulist:
    # print(hdulist[1].data)
    # Extract the probability column from the first table extension
    skymap_data = Table(hdulist[1].data)
    skymap_data
ts = time.time()
probabilities = MOC.probabilities_in_multiordermap(moc_tess, skymap_data, n_threads=24)
# print(np.sum(probabilities))
print('time spent summing:',time.time()-ts)
indexes = sorted(range(len(probabilities)), key=lambda k: probabilities[k], reverse=True)[:30]
print(indexes)
probs = []
good_moc = []

for i in indexes:
    probs.append(probabilities[i])
    good_moc.append(moc_tess[i])
# print(probs)


# make_tile_plots(filename, moc_tess, probs)
plotter(good_moc, hdulist[1])

aitoff = WCS(
    {
        "naxis": 2,
        "naxis1": 324,
        "naxis2": 162,
        "crpix1": 162.5,
        "crpix2": 81.5,
        "cdelt1": -1,
        "cdelt2": 1,
        "ctype1": "RA---AIT",
        "ctype2": "DEC--AIT",
    },
)
# m1 = MOC.from_multiordermap_fits_file(filename)

# horizons = [(10, 0),(10, 90),(10, 180),(10, 270)]

# m2 = observable_area(45, -93, horizons)
# fig = plt.figure(111)

# ax = fig.add_subplot(1, 1, 1, projection="mollweide", frame_class=EllipticalFrame)

# m1.fill(ax=ax, wcs=aitoff, alpha=0.5, fill=True, color="green")
# m2.fill(ax=ax, wcs=aitoff, alpha=0.5, fill=True, color="dodgerblue")

# ax.set_aspect(1.0)

# plt.xlabel("ra")
# plt.ylabel("dec")
# plt.grid(color="black", linestyle="dotted")
# plt.savefig('figure1.png')
# m_intersect = m1.intersection(m2)

# fig = plt.figure(111)

# ax = fig.add_subplot(1, 1, 1, projection=aitoff, frame_class=EllipticalFrame)

# m_intersect.fill(ax=ax, wcs=aitoff, alpha=0.5, fill=True, color="y")
# m_intersect.border(ax=ax, wcs=aitoff, alpha=0.5, fill=True, color="black")

# ax.set_aspect(1.0)

# plt.xlabel("ra")
# plt.ylabel("dec")
# plt.grid(color="black", linestyle="dotted")
# plt.savefig('figure2.png')

