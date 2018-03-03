import yaml
import os
import pprint

print("Application started")

config_file = os.environ.get('CONFIG_FILE')

if config_file is None:
    config_file = 'config/env.yml'

pp = pprint.PrettyPrinter(indent=4)

print('Getting log from: %s' % (config_file))

with open(config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

if (cfg['environmet']['printConfig'] is True):
    print("Configuration:")
    pp.pprint(cfg)


def get_config():
    return cfg
