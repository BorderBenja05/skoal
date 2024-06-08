import numpy as np
from sklearn.neighbors import BallTree
from astropy.table import Table
import xml.etree.ElementTree as ET
from pathlib import Path

wk_dir = Path(__file__).parent.absolute()

def rect_tess_maker(telescope, rafov,decfov, scale=0.97):
    rafov = np.deg2rad(rafov)*scale
    decfov = np.deg2rad(decfov)*scale
    vertical_count = np.ceil(np.pi / (decfov))  

    phis = []
    thetas = []

    phi = -0.5 * np.pi
    phi_step = np.pi / vertical_count
    # print('phi_step is', np.rad2deg(phi_step))
    while phi < 0.5 * np.pi - 1e-8 :
        if phi < (0-(phi_step/2)) and not phi == (-.5*np.pi):
            horizontal_count = np.ceil(
                (2 * np.pi * np.cos(phi + (phi_step/2))) / (rafov)
            )
        elif phi > (phi_step/2) and phi<((.5*np.pi)-(phi_step/2)):
            horizontal_count = np.ceil(
                (2 * np.pi * np.cos(phi - (phi_step/2))) / (rafov)
            )
        elif phi < (phi_step/2) and phi > (-phi_step/2):
            horizontal_count = np.ceil(2*np.pi/rafov)
        else:
            horizontal_count = 1
        # print(horizontal_count)
        theta = 0
        theta_step = 2 * np.pi / horizontal_count
        # print(np.rad2deg(theta_step))
        while theta < 2 * np.pi - 1e-8:
            phis.append(phi)
            thetas.append(theta)
            theta += theta_step
        phi += phi_step
    phis.append(np.pi/2)
    thetas.append(1)
    dec = np.array(np.rad2deg(phis))
    ra = np.array(np.rad2deg(thetas))
    tessfile_path = f'{wk_dir}/data/tesselations/{telescope}.tess'


    fid = open(tessfile_path, "w")
    for ii in range(len(ra)):
        fid.write("%d %.5f %.5f\n" % (ii, ra[ii], dec[ii]))
    fid.close()


# rect_tess_maker( 'kasa11', 3.2, 2.1, .98)



