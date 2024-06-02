import numpy as np
from sklearn.neighbors import BallTree
from astropy.table import Table
import xml.etree.ElementTree as ET
from pathlib import Path

wk_dir = Path(__file__).parent.absolute()

def rect_tess_maker(telescope, rafov,decfov, scale=0.97):
    sphere_radius = 1.0
    rafov = np.deg2rad(rafov)*scale
    decfov = np.deg2rad(decfov)*scale
    vertical_count = np.ceil((np.pi * sphere_radius) / (decfov)) 

    phis = []
    thetas = []

    phi = -0.5 * np.pi
    phi_step = np.pi / vertical_count
    while phi < 0.5 * np.pi:
        horizontal_count = np.ceil(
            (2 * np.pi * np.cos(phi) * sphere_radius) / (rafov)
        )
        theta = 0
        theta_step = 2 * np.pi / horizontal_count
        while theta < 2 * np.pi - 1e-8:
            phis.append(phi)
            thetas.append(theta)
            theta += theta_step
        phi += phi_step
    dec = np.array(np.rad2deg(phis))
    ra = np.array(np.rad2deg(thetas))
    tessfile_path = f'{wk_dir}/data/tesselations/{telescope}.tess'


    fid = open(tessfile_path, "w")
    for ii in range(len(ra)):
        fid.write("%d %.5f %.5f\n" % (ii, ra[ii], dec[ii]))
    fid.close()











