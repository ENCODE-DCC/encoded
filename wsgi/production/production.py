import configparser
from logging.config import fileConfig
from pathlib import Path

from paste.deploy import loadapp

configfile = str(Path(__file__).resolve().parents[2] / "production.ini")

try:
    fileConfig(configfile)
except configparser.NoSectionError:
    pass

application = loadapp("config:" + configfile, name=None)
