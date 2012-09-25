#! /usr/bin/env python2.7
"""
Register a FITS file ready to be converted into Work Units
"""
import argparse
from datetime import datetime
import logging
from sqlalchemy.engine import create_engine
from sqlalchemy.orm.session import sessionmaker
from config import db_login
from database.database_support import Register

LOG = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)-15s:' + logging.BASIC_FORMAT)

parser = argparse.ArgumentParser()
parser.add_argument('FITS_file', nargs=1, help='the input FITS file containing the galaxy')
parser.add_argument('redshift', type=float, nargs=1, help='the redshift of the galaxy')
parser.add_argument('galaxy_name', nargs=1, help='the name of the galaxy')
parser.add_argument('type', nargs=1, help='the hubble type')
parser.add_argument('priority', type=int, nargs=1, help='the higher the number the higher the priority')

args = vars(parser.parse_args())

REDSHIFT = args['redshift'][0]
INPUT_FILE = args['FITS_file'][0]
GALAXY_NAME = args['galaxy_name'][0]
GALAXY_TYPE = args['type'][0]
PRIORITY = args['priority'][0]

# Connect to the database - the login string is set in the database package
engine = create_engine(db_login)
Session = sessionmaker(bind=engine)
session = Session()

# Create and save the object
register = Register()
register.galaxy_name = GALAXY_NAME
register.redshift = REDSHIFT
register.galaxy_type = GALAXY_TYPE
register.filename = INPUT_FILE
register.priority = PRIORITY
register.register_time = datetime.now()

session.commit()

LOG.info('Registered %s %s %f %s %d', GALAXY_NAME, GALAXY_TYPE, REDSHIFT, INPUT_FILE, PRIORITY)
