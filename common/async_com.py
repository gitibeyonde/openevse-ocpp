
import pathlib
import sys
import time
import logging
from datetime import datetime, timedelta

dir_path = str(pathlib.Path(__file__).resolve().parent.parent)
logging.getLogger().setLevel(logging.INFO)

class AsyncCom:
    async_file = None
    
    OCPP_CMD_FILE = dir_path + '/http/slave/motion/cmd' 
    OCPP_RESP_FILE = dir_path + '/http/slave/motion/resp' 
    SERIAL_CMD_FILE = dir_path + '/http/slave/motion/scmd' 
    SERIAL_RESP_FILE = dir_path + '/http/slave/motion/sresp' 
    
    def __init__(self, shm_file):
        self.async_file = shm_file
        self.flush() 
        
    def flush(self):
        with open(self.async_file, 'w') as f: f.truncate()
        
    def write(self, cmd, params):
        logging.info("%s << Command = %s, Params=%s"%(self.async_file, cmd, params))
        with open(self.async_file, 'w') as f:
            if isinstance(params, (list, tuple)):
                f.write(cmd + ":" + ":".join(params))
            else:
                f.write(cmd + ":" + params)
            
    def read(self, timeout=5):
        txt = None
        start=int(time.time())
        while txt is None:
            delta = int(time.time())- start
            if delta > timeout:break
            time.sleep(0.5)
            txt = open(self.async_file, 'r').read().rstrip('\n').split(":")
            if (txt is not None and len(txt) > 0 and len(txt[0]) < 2 ): 
                txt=None
            else:
                logging.info("%s >> %s" % (self.async_file, txt))
        with open(self.async_file, 'w') as f: f.truncate()
        return txt
        
    def check(self):
        txt = open(self.async_file, 'r').read().rstrip('\n').split(":")
        if (len(txt) > 0 and len(txt[0]) < 2): return False
        else: return txt

def main():
    ascmd = AsyncCom(AsyncCom.SERIAL_CMD_FILE)
    ascmd.flush()
    ascmd.write('Authorize', 'Accepted')
    time.sleep(1)
    result = ascmd.read()
    print(result)
    
    
if __name__ == "__main__":
    main()
    