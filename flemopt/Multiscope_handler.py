import numpy as np
import astropy.units as u
from astropy.coordinates import SkyCoord, EarthLocation, AltAz
from astropy.time import Time
from pathlib import Path

DIR = Path(__file__).parent.absolute()


def determine_visibility(input_file, observer_location, output_file, observation_time=None):
    tstart = Time.now()
    empty = False
    # Load input file
    data = np.genfromtxt(input_file, delimiter=',', dtype=str)
    ras = data[:, 1].astype(float) * u.deg
    decs = data[:, 2].astype(float) * u.deg
    priorities = data[:, 3].astype(int)

    # Convert input coordinates to SkyCoord objects
    coords = SkyCoord(ra=ras, dec=decs, frame='icrs')

    # Define observation time (default to current time if not provided)
    if observation_time is None:
        observation_time = Time.now() #+ 6.*u.hour

    # Convert observation time to AltAz frame
    altaz_frame = AltAz(obstime=observation_time, location=observer_location)
    coords_altaz = coords.transform_to(altaz_frame)

    # Check altitude of each object
    observable_indices = np.where(coords_altaz.alt > 0)[0]
    if len(observable_indices) ==0:
        empty = True
    time= Time.now()-tstart
    print(time)
    # Write observable objects to output file
    with open(output_file, 'w') as f:
        for idx in observable_indices:
            f.write(f"{data[idx, 0]},{data[idx, 1]},{data[idx, 2]},{data[idx, 3]}\n")
    return empty


def save_table_to_file(table, filename):
    np.savetxt(filename, table, delimiter=',', fmt='%s')


def split_schedule(infile, outfolder, num_tables):
    tables = [[] for _ in range(num_tables)]
    data=np.genfromtxt(infile,delimiter=',',dtype=str)
    
    for i, row in enumerate(data):
        table_index = i % num_tables
        tables[table_index].append(row)
    for i, table in enumerate(tables):
        table_filename = f"{outfolder}/telescope_{i+1}.txt"  # Name of the text file
        save_table_to_file(table, table_filename)
        #print(f"Schedule {i+1} saved to '{table_filename}'")

    return tables
# loc = EarthLocation(lat=44.990307*u.deg, lon=-93.179719*u.deg, height=242*u.m)

# determine_visibility(f'{DIR}/current_schedules/CurrentEventSchedule.txt', loc,f'{DIR}/current_schedules/ObservableCurrentEventSchedule.txt' )
