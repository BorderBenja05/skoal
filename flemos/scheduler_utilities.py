from astroplan import FixedTarget, AirmassConstraint, AtNightConstraint, MoonSeparationConstraint, AltitudeConstraint, is_observable, Observer
from scipy.optimize import linear_sum_assignment
from scipy.spatial.distance import cdist
from astropy.coordinates import SkyCoord, EarthLocation
from astropy.time import Time
import astropy.units as u
from sklearn.cluster import KMeans
import numpy as np

def read_targets_from_file(file_name):
    targets = []
    for row in np.genfromtxt(file_name, delimiter=',', dtype=str):
        # (ra, dec, name, exposure)
        targets.append([float(row[1]), float(row[2]), row[0], 30])
    return targets

def _get_even_clusters(X, n_clusters):
    # Source: https://stackoverflow.com/questions/5452576/k-means-algorithm-variation-with-equal-cluster-size
    cluster_size = int(np.ceil(len(X)/n_clusters))
    kmeans = KMeans(n_clusters, n_init='auto')
    kmeans.fit(X)
    centers = kmeans.cluster_centers_
    centers = centers.reshape(-1, 1, X.shape[-1]).repeat(
        cluster_size, 1).reshape(-1, X.shape[-1])
    distance_matrix = cdist(X, centers)
    clusters = linear_sum_assignment(distance_matrix)[1]//cluster_size
    return clusters


def separate_targets_into_clusters(targets, n):
    # Convert targets into 3D points on the unit sphere
    targets_3d = []
    for target in targets:
        targets_3d.append([np.cos(np.radians(target[1]))*np.cos(np.radians(target[0])),
                           np.cos(np.radians(target[1]))*np.sin(np.radians(target[0])),
                           np.sin(np.radians(target[1]))])
    # Perform k-means clustering
    clusters = _get_even_clusters(np.array(targets_3d), n)
    # Split blocks between the telescopes.
    telescope_targets = [[] for _ in range(n)]
    for (label, target) in zip(clusters, targets):
        telescope_targets[label].append(target)

    return telescope_targets

def separate_targets_evenly(targets, n):
    # Split blocks between the telescopes.
    telescope_targets = [[] for _ in range(n)]
    for i in range(len(targets)):
        telescope_targets[i % n].append(targets[i])

    return telescope_targets

def filter_for_visibility(targets, lat, lon, altitude, twilight, telescope, horizon):

    # Constraints for the telescope
    constraints = [AirmassConstraint(max=2, boolean_constraint=False),
                    # AtNightConstraint.twilight_nautical() 
                    # if twilight == 'nautical' else AtNightConstraint.twilight_astronomical(),
        MoonSeparationConstraint(min=5*u.deg),
        AltitudeConstraint(min=horizon*u.deg)]
    loc = EarthLocation(lat=float(lat)*u.deg, 
                        lon=float(lon)*u.deg, 
                        height=float(altitude)*u.m)
    observer = Observer(loc, name=telescope, timezone="US/Central")    
    # The offset is for testing what happens if you schedule during the night
    t = Time.now()+12.*u.hour
    t_start = Time(t, format='jd')

    # Change targets to FixedTarget's
    fixed_targets = []
    for target in targets:
        fixed_targets.append(FixedTarget(coord=SkyCoord(
            target[1]*u.deg, target[2]*u.deg), name=target[0]))

    # Check if targets will be observable in the time window
    observable = is_observable(constraints, observer, fixed_targets, times=[t_start])
    # print(observable)
    filtered_targets = []
    for i in range(len(targets)):
        if observable[i]:
            filtered_targets.append(targets[i])
    return filtered_targets