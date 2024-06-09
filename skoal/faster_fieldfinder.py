import numpy as np

def field_from_coords(coords, rafov, decfov, scale=.97):
    # Scaling and converting degrees to radians
    rafov = np.deg2rad(rafov * scale)
    decfov = np.deg2rad(decfov * scale)
    phi_step = np.pi / np.ceil(np.pi / decfov)

    # Generate phi values
    phi_start = -np.pi / 2
    phi_end = np.pi / 2
    phis = np.arange(phi_start, phi_end + phi_step, phi_step)

    # Compute horizontal counts (thetas) for each phi
    cos_phi = np.cos(phis + phi_step / 2)
    horizontal_counts = np.ceil(2 * np.pi * cos_phi / rafov).astype(int)

    # Handle edge cases
    horizontal_counts[phis < -phi_step / 2] = np.ceil(2 * np.pi * np.cos(phis[phis < -phi_step / 2] + phi_step / 2) / rafov).astype(int)
    horizontal_counts[phis > phi_step / 2] = np.ceil(2 * np.pi * np.cos(phis[phis > phi_step / 2] - phi_step / 2) / rafov).astype(int)
    horizontal_counts[np.abs(phis) <= phi_step / 2] = np.ceil(2 * np.pi / rafov).astype(int)
    horizontal_counts[phis == -np.pi / 2] = 1

    # Compute start indices
    start_index = np.cumsum(horizontal_counts) - horizontal_counts

    # Compute theta steps
    thetasteps = 2 * np.pi / horizontal_counts

    # Initialize results
    field_ids = np.empty(len(coords), dtype=int)
    centers = np.empty((len(coords), 2), dtype=float)

    # Convert input coords to numpy array
    coords = np.array(coords)
    ra = coords[:, 0]
    dec = coords[:, 1]

    # Vectorized computation of dec indices
    dec_indices = np.round((dec + np.pi / 2) / phi_step).astype(int)

    # Adjusting dec_indices that are out of bounds due to rounding
    dec_indices = np.clip(dec_indices, 0, len(horizontal_counts) - 1)

    # Vectorized computation of ra numbers and field IDs
    theta_div = 2 * np.pi / horizontal_counts[dec_indices]
    ra_numbers = np.floor((ra / theta_div) + 1.5).astype(int)
    ra_numbers[ra_numbers > horizontal_counts[dec_indices]] = 1

    field_ids[:] = ra_numbers + start_index[dec_indices] - 1

    # Vectorized computation of centers
    centers[:, 0] = thetasteps[dec_indices] * (ra_numbers - 1)
    centers[:, 1] = phis[dec_indices]

    return field_ids.tolist(), centers.tolist()

def ra_number(ra, thetas):
    h = np.floor((ra / (2 * np.pi / thetas)) + 1.5)
    if h == thetas + 1:
        h = 1
    return int(h)

def dec_num(dec, phi_step):
    return int(np.round((dec + (np.pi / 2)) / phi_step))

# # Example usage
# ra = np.deg2rad(32.7)
# dec = np.deg2rad(89.8)
# print(field_from_coords([(ra, dec)], 3.2, 2.1, .98))
