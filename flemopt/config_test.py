import configparser
import os


config = configparser.ConfigParser()
default = configparser.ConfigParser()
default.read(f'data/configs/default.cfg')
telescope = 'Bennyscope'

if os.path.exists(f'data/configs/{telescope}.cfg'):
    config.read(f'data/configs/{telescope}.cfg')
else:
    print('no configuration file found, requesting minimal required telescope information...')
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


print( lat, lon, RAfov, DECfov, elevation, tileScale, minObsChance, horizon)