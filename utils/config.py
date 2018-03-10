import yaml
import os
import pprint
from utils.crypto import decrypt_file

print("Application started")

config_file = os.environ.get('CONFIG_FILE')
decryption_pass = os.environ.get('DECRYPTION_PASS')

if config_file is None:
    config_file = 'config/env.yml.enc'

if config_file.endswith('.enc'):
    print("File encrypted, starting decryption")
    decrypt_file(decryption_pass, config_file, config_file[:-4])
    config_file = config_file[:-4]

pp = pprint.PrettyPrinter(indent=4)

print('Getting log from: %s' % (config_file))

with open(config_file, 'r') as ymlfile:
    cfg = yaml.load(ymlfile)

if (cfg['environmet']['printConfig'] is True):
    print("Configuration:")
    pp.pprint(cfg)


def get_config():
    return cfg
