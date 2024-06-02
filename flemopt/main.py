import argparse
import configparser
import os
from pathlib import Path
from flemopt.tesselation_generator import rect_tess_maker
import flemopt.GCN_utils as gcn
from flemopt.lvc_handler import generate_fields_from_skymap
from flemopt.scheduler_utilities import filter_for_visibility
import numpy as np


FLEMOPT_DIR = Path(__file__).parent.absolute()



def main():
    parser = argparse.ArgumentParser(description="My Script Description")
    parser.add_argument('-t', dest='t', type=str)
    parser.add_argument('-voe', dest='voe', type=str)
    parser.add_argument('-e', dest='e', type=str)
    parser.add_argument('-area', dest='area', type=str)
    parser.add_argument('-o', dest='o', type=str)

    args = parser.parse_args()
    outpath = args.o
    telescope = args.t
    eventfile = args.voe
    event = args.e
    config = configparser.ConfigParser()
    default = configparser.ConfigParser()
    default.read(f'data/configs/default.cfg')
    
    if telescope == None:
        telescope = input('please enter telescope name:')
    if eventfile and event == None:
        entry = input('please provide event name or VOEvent.xml file')
        if entry[-4:] == '.xml':
            eventfile = entry
        else:
            event = entry


    if eventfile:
        if gcn.get_ivorn(eventfile) == 'Fermi':
            fermi = True
        elif gcn.get_ivorn(eventfile) == 'LVC':
            event = gcn.getEvent(eventfile)
            LVC = True




    if event and eventfile:
        print('it is unnecessary to provide both event and event file, either will do')
        if fermi and LVC:
            print('okay if you are going to give both an event and event file, at least make sure theyre for the same kind of event, pick a lane buddy...')
            exit        
        elif not event == gcn.getEvent(eventfile):
            print('okay if you are going to give both an event and event file, at least make sure theyre for the same event')
            exit
    

    if not args.area == None:
        


    if os.path.exists(f'data/configs/{telescope}.cfg'):
        config.read(f'data/configs/{telescope}.cfg')
    else:
        lat = input(f'please enter {telescope} latitude:')
        lon = input(f'please enter {telescope} longitude:')
        RAfov = input(f'please enter {telescope} RAfov:')
        DECfov = input(f'please enter {telescope} DECfov:')
        elevation = input(f'please enter {telescope} elevation:')
        config.add_section(telescope)
        config.set(telescope, 'lat', lat)
        config.set(telescope, 'lon', lon)
        config.set(telescope, 'RAfov', RAfov)
        config.set(telescope, 'DECfov', DECfov)
        config.set(telescope, 'elevation', elevation)
        with open(f'data/configs/{telescope}.cfg', 'w') as configfile:
            config.write(configfile)

    try:
        lat = config[telescope]['lat']
        lon = config[telescope]['lon']
        RAfov = config[telescope]['RAfov']
        DECfov = config[telescope]['DECfov']
        elevation = config[telescope]['elevation']
    except:
        print('flemopt config files MUST contain the following items: lat, lon, RAfov, DECfov and elevation. Default settings will be used for parameters not provided in configuration file')
    
    try:
        tileScale = config[telescope]['tileScale']
    except:
        tileScale = default['telescope']['tileScale']

    try:
        minObsChance = config[telescope]['minObsChance']
    except:
        minObsChance = default['telescope']['minObsChance']

    try:
        horizon = config[telescope]['horizon']
    except:
        horizon = default['telescope']['horizon']

    if not os.path.exists(f'data/tesselations/{telescope}.tess'):
        rect_tess_maker(telescope, RAfov, DECfov, tileScale)

    if LVC:
        skymap_path =gcn.get_skymap(event, f'{FLEMOPT_DIR}/SKYMAP_DIR')
        fields, ids_to_fields = generate_fields_from_skymap(skymap_path, RAfov, DECfov, tileScale, minObsChance)
        filtered_fields = filter_for_visibility(fields, lat, lon, elevation, 'nautical', telescope, horizon)
        with open(f'{outpath}/{event}_schedule.txt', 'w') as file:
            for id, _ in filtered_fields:
                file.write(f"{id},{np.rad2deg(ids_to_fields[id][0]):.5f},{np.rad2deg(ids_to_fields[id][1]):.5f},1\n")

        if args.area:
            gcn.area(minObsChance, skymap_path)
        

    


if __name__ == '__main__':
    main()
