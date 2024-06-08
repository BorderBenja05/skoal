import configparser

def make_config_file(telescope, CONFIGS_DIR):
    config = configparser.ConfigParser()
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
    with open(f'{CONFIGS_DIR}/{telescope}.cfg', 'w') as configfile:
        config.write(configfile)

