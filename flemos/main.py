import argparse
import configparser
import os
from pathlib import Path
from tesselation_generator import rect_tess_maker
import GCN_utils as gcn
from lvc_handler import generate_fields_from_skymap
from scheduler_utilities import filter_for_visibility
import numpy as np




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
    LVCevent = args.e
    config = configparser.ConfigParser()
    default = configparser.ConfigParser()
    default.read(f'data/configs/default.cfg')
    
    if telescope == None:
        # telescope = input('please enter telescope name: ')
        telescope = 'RASA11'
    
    if not eventfile and not LVCevent:
        # entry = input('please provide event name or VOEvent.xml file: ')
        # if entry[-4:] == '.xml':
        #     eventfile = entry
        # else:
        #     LVCevent = entry
        eventfile = 


    if eventfile:
        if gcn.get_ivorn(eventfile) == 'Fermi':
            fermi = True
        elif gcn.get_ivorn(eventfile) == 'LVC':
            LVCevent = gcn.getEvent(eventfile)
            LVC = True



    if LVCevent and eventfile:
        print('it is unnecessary to provide both event and event file, either will do')
        if fermi and LVC:
            print('okay if you are going to give both an event and event file, at least make sure theyre for the same kind of event, pick a lane buddy...')
            exit        
        elif not LVCevent == gcn.getEvent(eventfile):
            print('okay if you are going to give both an event and event file, at least make sure theyre for the same event')
            exit
    
        


    if os.path.exists(f'{FLEMOPT_DIR}/data/configs/{telescope}.cfg'):
        config.read(f'{FLEMOPT_DIR}/data/configs/{telescope}.cfg')
    else:
        lat = input(f'please enter {telescope} latitude: ')
        lon = input(f'please enter {telescope} longitude: ')
        RAfov = input(f'please enter {telescope} RAfov: ')
        DECfov = input(f'please enter {telescope} DECfov: ')
        elevation = input(f'please enter {telescope} elevation: ')
        config.add_section(telescope)
        config.set(telescope, 'lat', lat)
        config.set(telescope, 'lon', lon)
        config.set(telescope, 'RAfov', RAfov)
        config.set(telescope, 'DECfov', DECfov)
        config.set(telescope, 'elevation', elevation)
        with open(f'data/configs/{telescope}.cfg', 'w') as configfile:
            config.write(configfile)

    try:
        lat = float(config[telescope]['lat'])
        lon = float(config[telescope]['lon'])
        RAfov = float(config[telescope]['RAfov'])
        DECfov = float(config[telescope]['DECfov'])
        elevation = float(config[telescope]['elevation'])
    except:
        print('flemopt config files MUST contain the following items: lat, lon, RAfov, DECfov and elevation. Default settings will be used for parameters not provided in configuration file')
    
    try:
        tileScale = float(config[telescope]['tileScale'])
    except:
        tileScale = float(default['telescope']['tileScale'])

    try:
        minObsChance = float(config[telescope]['minObsChance'])
    except:
        minObsChance = float(default['telescope']['minObsChance'])

    try:
        horizon = float(config[telescope]['horizon'])
    except:
        horizon = float(default['telescope']['horizon'])

    if not os.path.exists(f'{FLEMOPT_DIR}/data/tesselations/{telescope}.tess'):
        rect_tess_maker(telescope, RAfov, DECfov, tileScale)

    if LVCevent:
        skymap_path =gcn.get_skymap(LVCevent, f'{FLEMOPT_DIR}/skymaps')
        fields, ids_to_fields = generate_fields_from_skymap(skymap_path, RAfov, DECfov, tileScale, minObsChance)
        filtered_fields = filter_for_visibility(fields, lat, lon, elevation, 'nautical', telescope, horizon)
        with open(f'{outpath}/{LVCevent}_schedule.txt', 'w') as file:
            for id, _ in filtered_fields:
                file.write(f"{id},{np.rad2deg(ids_to_fields[id][0]):.5f},{np.rad2deg(ids_to_fields[id][1]):.5f},1\n")

        if args.area:
            gcn.area(minObsChance, skymap_path)
        

    


if __name__ == '__main__':
    main()
