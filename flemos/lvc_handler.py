import xml.etree.ElementTree as ET
from astropy.table import QTable
from gcn_kafka import Consumer
import astropy_healpix as ah
from pathlib import Path
import numpy as np
from GCN_utils import getEvent, get_skymap
from scheduler_utilities import filter_for_visibility

FLEMOPT_DIR = Path(__file__).parent.absolute()
def field_from_coords(coords, rafov, decfov, scale=0.97):
    ''' 
    Find the cooresponding tesselation for a list of (ra, dec) coordinates.
    All angles are in radians
    '''
    # Scale the fov
    rafov *= scale
    decfov *= scale
    rafov = np.deg2rad(rafov)
    decfov = np.deg2rad(decfov)

    # Find the number of fields in the vertical direction
    vertical_count = int(np.ceil(np.pi / (decfov)))
    # Calculate how tall each field should be
    phi_step = np.pi / vertical_count

    # Make a dictionary with the width of fields at each level
    theta_steps = [0]*(vertical_count+1)
    id_offsets = [0]*(vertical_count+1)
    current_offset = int(0)
    for i in range(vertical_count+1):
        # Calculate the number of fileds in the horizontal direction
        horizontal_count = np.ceil((2 * np.pi * np.cos(-0.5 * np.pi + phi_step * i)) / (rafov))
        # Calculte how wide each fied should be
        theta_steps[i] = 2 * np.pi / horizontal_count

        id_offsets[i] = current_offset
        current_offset += int(horizontal_count)

    # Find field coords
    ids = []
    fields = []

    for ra, dec in coords:
        # Find which number from the top the field is
        phi_index = int(np.round((dec+np.pi/2)/phi_step))
        # Find which number around the field is
        theta_index = np.round(ra/theta_steps[phi_index] * horizontal_count)
        # Calculate the field coords with the indexes and the step size
        fields.append(((theta_index * theta_steps[phi_index]), (phi_index * phi_step - np.pi/2)))
        ids.append(id_offsets[phi_index]+int(theta_index))
        
    return ids, fields

def generate_fields_from_skymap(skymap_path, rafov, decfov, scale, minobs):
    # Read the file
    
    skymap = QTable.read(skymap_path)

    # Sort by probability density
    skymap.sort('PROBDENSITY', reverse=True)
    # Get the pixel area
    level, nested_index = ah.uniq_to_level_ipix(skymap['UNIQ'])
    pixel_area = ah.nside_to_pixel_area(ah.level_to_nside(level))
    # Calculate the probability of each pixel
    probabilities = pixel_area * skymap['PROBDENSITY']
    # Find minimum cutoff
    cumprob = np.cumsum(probabilities)
    i = cumprob.searchsorted(minobs)

    # Find the corresponding tesselations of those pixels
    sky_coordinates = ah.healpix_to_lonlat(nested_index, ah.level_to_nside(level), order='nested')
    sky_coordinates = np.array(sky_coordinates).transpose()
    ids, fields = field_from_coords(sky_coordinates[:i], rafov, decfov, scale)
    ids_to_fields = dict(zip(ids, fields))

    # Sum the probabilities of the tesselations
    weights = {}
    for id, probability in zip(ids, probabilities):
        if id in weights:
            weights[id] += probability
        else:
            weights[id] = probability
    # Sort by total probability
    sorted_fields = sorted(weights.items(), key=lambda item: item[1], reverse=True)

    # Write targets to file
    # with open(f'{out_dir}/{event}_targets.txt', 'w') as file:
    #     for id, _ in filtered_fields:
    #         file.write(f"{id},{np.rad2deg(ids_to_fields[id][0]):.5f},{np.rad2deg(ids_to_fields[id][1]):.5f},1\n")
    return sorted_fields, ids_to_fields


