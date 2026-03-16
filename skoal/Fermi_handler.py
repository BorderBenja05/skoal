from sklearn.neighbors import BallTree
import xml.etree.ElementTree as ET
import numpy as np
from skoal.GCN_utils import getFERMICoordinates


def spherical_to_cartesian(spherical_cartesian_coords):
    theta = np.radians(spherical_cartesian_coords[:, 0])
    phi = np.radians(spherical_cartesian_coords[:, 1] + 90)
    x = np.sin(phi) * np.cos(theta)
    y = np.sin(phi) * np.sin(theta)
    z = np.cos(phi)
    return np.column_stack((x, y, z))


def fields_in_error_circle(tiling, ra, dec, error, ra_fov, dec_fov):
    """Find tessellation fields within a FERMI-style error circle.

    Parameters
    ----------
    tiling : numpy.ndarray, shape (N, 3)
        Tessellation array [field_id, ra_deg, dec_deg] as returned by make_tiling().
    ra : float
        Centre RA in degrees.
    dec : float
        Centre Dec in degrees.
    error : float
        Error radius in degrees.
    ra_fov : float
        Telescope RA field-of-view in degrees (used to buffer the search radius).
    dec_fov : float
        Telescope Dec field-of-view in degrees.

    Returns
    -------
    list of (field_id, ra_deg, dec_deg, probability)
        Fields within the buffered error circle, probability set to 1.0.
    """
    error_buff = (((ra_fov ** 2) + (dec_fov ** 2)) ** 0.5) / 2
    buffed_error = error + error_buff

    ra_rad = np.radians(ra)
    dec_rad = np.radians(dec + 90)
    center = [[np.sin(dec_rad) * np.cos(ra_rad),
               np.sin(dec_rad) * np.sin(ra_rad),
               np.cos(dec_rad)]]
    r = 2 * np.sin(np.radians(buffed_error) / 2)

    coords = tiling[:, 1:3]  # ra_deg, dec_deg columns
    tree = BallTree(spherical_to_cartesian(coords), leaf_size=40)
    indices = tree.query_radius(center, r=r, sort_results=True, return_distance=True)[0][0]

    return [
        (int(tiling[idx, 0]), float(tiling[idx, 1]), float(tiling[idx, 2]), 1.0)
        for idx in indices
    ]


def Fermi_handle(tiling, ra, dec, error, ra_fov, dec_fov):
    """Wrapper kept for CLI compatibility. Prefer fields_in_error_circle() directly."""
    targets = fields_in_error_circle(tiling, ra, dec, error, ra_fov, dec_fov)
    return targets, error
