from datetime import datetime, timedelta
from dateutil import parser
import pathlib
import platform
import traceback
import sys

platform = platform.system()  # Linux, Darwin, Windows
dir_path = str(pathlib.Path(__file__).resolve().parent.parent)

uuid_file = dir_path + '/.uuid'


def timestamp(utc_naive=datetime.utcnow()):
    return int((utc_naive.replace(tzinfo=None) - datetime(1970, 1, 1)).total_seconds())

def getUuid():
    with open(uuid_file, 'r') as f: uuid = f.read().strip()
    if uuid == '':
        # logging.fatal("FATAL: UUID needs to be present in /root/.uuid")
        raise ValueError("FATAL: UUID needs to be present in " + uuid_file)
    else:
        return uuid

    

