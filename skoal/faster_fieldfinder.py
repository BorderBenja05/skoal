import numpy as np


def field_from_coords(coords, rafov, decfov, scale=0.97):
    rafov *= scale
    decfov *= scale
    rafov = np.deg2rad(rafov)
    decfov = np.deg2rad(decfov)
    phis_count = int(np.ceil(np.pi / decfov))
    phi_step = np.pi / phis_count

    phis = []
    thetas = []
    thetasteps = []
    phi = -np.pi / 2

    while phi < 0.5 * np.pi - 1e-8:
        if phi < (0 - (phi_step / 2)) and phi != (-0.5 * np.pi):
            horizontal_count = np.ceil((2 * np.pi * np.cos(phi + (phi_step / 2))) / rafov)
        elif phi > (phi_step / 2) and phi < ((0.5 * np.pi) - (phi_step / 2)):
            horizontal_count = np.ceil((2 * np.pi * np.cos(phi - (phi_step / 2))) / rafov)
        elif phi < (phi_step / 2) and phi > (-phi_step / 2):
            horizontal_count = np.ceil(2 * np.pi / rafov)
        else:
            horizontal_count = 1
        hc = int(horizontal_count)
        thetas.append(hc)
        thetasteps.append(2 * np.pi / hc)
        phis.append(phi)
        phi += phi_step

    thetas.append(1)
    thetasteps.append(2 * np.pi)
    phis.append(np.pi / 2)

    start_index = np.zeros(len(thetas), dtype=np.int64)
    for i in range(1, len(thetas)):
        start_index[i] = start_index[i-1] + thetas[i-1]

    num_coords = len(coords)
    field_ids = np.empty(num_coords, dtype=np.int64)
    centers = np.empty((num_coords, 2), dtype=np.float64)

    for i in range(num_coords):
        ra, dec = coords[i]
        ddex = int(np.round((dec + np.pi / 2) / phi_step))
        ddex = max(0, min(ddex, len(phis) - 1))
        raN = int(np.floor((ra / (2 * np.pi / thetas[ddex])) + 1.5))
        if raN == (thetas[ddex] + 1):
            raN = 1
        id = raN + start_index[ddex] - 1
        field_ids[i] = id
        centers[i] = (thetasteps[ddex] * (raN - 1), phis[ddex])

    return field_ids.tolist(), centers.tolist()

# # Example usage
# coords = np.deg2rad(np.array([[0, -89.999], [185.0, 90.0]]))
# rafov = 10
# decfov = 5

# import time

# start = time.time()
# field_ids, centers = field_from_coords(coords, rafov, decfov)
# end = time.time()
# print(field_ids)
# print(centers)
# print(end - start)
