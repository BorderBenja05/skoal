from astropy.table import QTable
import astropy_healpix as ah
from pathlib import Path
import numpy as np
from skoal.field_from_coords import field_from_coords

FLEMOPT_DIR = Path(__file__).parent.absolute()

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
    # print(sorted_fields)
    return sorted_fields, ids_to_fields

def save_targets_to_file(filtered_targets, out_dir):
    with open(out_dir, 'w') as file:
        for target in filtered_targets:
            id = target[0]
            ra_deg = target[1]
            dec_deg = target[2]
            file.write(f"{id},{ra_deg:.5f},{dec_deg:.5f},1\n")
    