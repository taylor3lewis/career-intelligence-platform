import datetime
import os
from glob import glob
from os import sep
from shutil import copyfile

from config_app import DATA_ROOT
from config_app import LATEST_DATA
from config_app import MANUAL_DATA

latest = DATA_ROOT + str(datetime.datetime.now()).split(' ')[0] + sep + '*'
manual = MANUAL_DATA + '*'

if not os.path.exists(LATEST_DATA):
    os.makedirs(LATEST_DATA)

for of in glob(LATEST_DATA + '*'):
    os.remove(of)

for lf in glob(latest):
    copyfile(lf, LATEST_DATA + lf.split(sep)[-1])

for mf in glob(manual):
    copyfile(mf, LATEST_DATA + mf.split(sep)[-1])
