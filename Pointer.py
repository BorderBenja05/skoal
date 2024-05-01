import numpy as np
import math
from astropy.table import Table
import xml.etree.ElementTree as ET

def round_list(list,decimal_place = 5):
    rounded_list = []
    for i in list:
        rounded_i = np.round(i ,decimal_place)
        rounded_list.append(rounded_i)
    return rounded_list


def generate_telescope_pointings(center_ra, center_dec, error_radius, telescope_width, telescope_height):


    W_increment = .97*telescope_width
    H_increment = np.round(.97*telescope_height,4)

    # get a parking space
    pointings = []
    
    # park the car(make the pointers)
    if center_dec + error_radius < 90:

        #print(H_increment)
        H_list = [center_dec]
        while H_list[0] > (center_dec - error_radius + (H_increment / 2)):
            H_list.insert(0,H_list[0]- H_increment)
        while H_list[-1] < (center_dec + error_radius - (H_increment / 2)):
            H_list.append(H_list[-1]+ H_increment)

        H_list = round_list(H_list)
        print(H_list)
        heights = []
        for i in H_list:
            if i < 0 or i == 0:
                heights.append(H_list +(H_increment / 2))
            elif i > 0:
                heights.append(H_list - (H_increment / 2))
        heights = round_list([(i - center_dec  ) for i in H_list])
        print(heights)

        #get width before adjusting for curvature:
        Width_at_H = [(error_radius **2 - (H_list[i] + i*H_increment - center_dec)**2)**(1/2) for i in range(len(H_list))]
        Width_at_H = round_list(Width_at_H)
        print(Width_at_H)
    return pointings


# test generation:
print(generate_telescope_pointings(16,45,18, 2,3))