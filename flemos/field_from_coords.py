import numpy as np


def field_from_coords(coords, rafov,decfov, scale=.97):

    rafov *= scale
    decfov *= scale
    rafov = np.deg2rad(rafov)
    decfov = np.deg2rad(decfov)
    phis = np.ceil(np.pi/decfov)
    phi_step = np.pi /phis


    phi = -np.pi/2
    phis = []
    thetas = []
    thetasteps = []
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
        hc=int(horizontal_count)
        thetas.append(hc)
        thetasteps.append(2*np.pi/hc)
        phis.append(phi)
        phi += phi_step
    thetas.append(1)
    # print(thetas)

    start_index = []
    count = 0
    for n in thetas:
        start_index.append(count)
        count += n


    field_ids = []
    centers = []

    i = 0
    for ra,dec in coords:
        ddex = dec_num(dec,phi_step)
        raN = ra_number(ra, thetas[ddex]) 
        id = raN + start_index[ddex]
        field_ids.append(id-1)
        centers.append((thetasteps[ddex]*(raN-1), phis[ddex]))
    return field_ids, centers
        


# These aren't actually called by field_from_coords but they are the same math and provide helpful understanding
# into how the script actually works

def ra_number(ra, thetas):
    h = np.floor((ra/ (2*360/thetas)) + (3/2))
    if h == thetas + 1:
        h = 1
    return int(h)
# print(ra_number(85,2))

def dec_num(dec,phi_step):
    a = dec/phi_step
    num=np.round(a) 
    return int(num)
# print(dec_num(1,30))
ra = np.deg2rad(129.2)
dec = np.deg2rad(-71.4)
print(field_from_coords([(ra, dec)], 3.2, 2.1, .98))