#!/usr/bin/env python
"""
 **** RAPI protocol ****
Fx - function
Sx - set parameter
Gx - get parameter
command formats
1. with XOR checksum (recommended)
$cc pp pp ...^xk\r
2. with additive checksum (legacy)
$cc pp pp ...*ck\r
3. no checksum (FOR TESTING ONLY! DON'T USE FOR APPS)
$cc pp pp ...\r
\r = carriage return = 13d = 0x0D
cc = 2-letter command
pp = parameters
xk = 2-hex-digit checksum - 8-bit XOR of all characters before '^'
ck = 2-hex-digit checksum - 8-bit sum of all characters before '*'
response format
$OK [optional parameters]\r - success
$NK [optional parameters]\r - failure
asynchronous messages
$ST state\r - EVSE state transition - sent whenever EVSE state changes
 state: EVSE_STATE_xxx
$WF mode\r - Request client WiFi mode
 mode: WIFI_MODE_XXX
 (currently very long press (10 sec) of menu btn on OpenEVSE will send WIFI_MODE_AP_DEFAULT
commands
FB color - set LCD backlight color
colors:
 OFF 0
 RED 1
 YELLOW 3
 GREEN 2
 TEAL 6
 BLUE 4
 VIOLET 5
 WHITE 7 
 $FB 7*03 - set backlight to white
FD - disable EVSE
 $FD*AE
FE - enable EVSE
 $FE*AF
FP x y text - print text on lcd display
FR - reset EVSE
 $FR*BC
FS - sleep EVSE
 $FS*BD
S0 0|1 - set LCD type
 $S0 0*F7 = monochrome backlight
 $S0 1*F8 = RGB backlight
S1 yr mo day hr min sec - set clock (RTC) yr=2-digit year
S2 0|1 - disable/enable ammeter calibration mode - ammeter is read even when not charging
 $S2 0*F9
 $S2 1*FA
S3 cnt - set charge time limit to cnt*15 minutes (0=disable, max=255)
SA currentscalefactor currentoffset - set ammeter settings
SC amps - set current capacity
   if amps < minimum current capacity, will set to minimum and return $NK
   if amps > maximum current capacity, will set to maximum and return $NK
SD 0|1 - disable/enable diode check
 $SD 0*0B
 $SD 1*0C
SE 0|1 - disable/enable command echo
 $SE 0*0C
 $SE 1*0D
 use this for interactive terminal sessions with RAPI.
 RAPI will echo back characters as they are typed, and add a <LF> character
 after its replies. Valid only over a serial connection, DO NOT USE on I2C
SF 0|1 - disable/enable GFI self test
 $SF 0*0D
 $SF 1*0E
SG 0|1 - disable/enable ground check
 $SG 0*0E
 $SG 1*0F
SH kWh - set cHarge limit to kWh
SK - set accumulated Wh (v1.0.3+)
 $SK 0*12 - set accumulated Wh to 0
SL 1|2|A  - set service level L1/L2/Auto
 $SL 1*14
 $SL 2*15
 $SL A*24
SM voltscalefactor voltoffset - set voltMeter settings
SO ambientthresh irthresh - set Overtemperature thresholds
 thresholds are in 10ths of a degree Celcius
SR 0|1 - disable/enable stuck relay check
 $SR 0*19
 $SR 1*1A
SS 0|1 - disable/enable GFI self-test
 $SS 0*1A
 $SS 1*1B
ST starthr startmin endhr endmin - set timer
 $ST 0 0 0 0*0B - cancel timer
SV 0|1 - disable/enable vent required
 $SV 0*1D
 $SV 1*1E
G3 - get time limit
 response: OK cnt
 cnt*15 = minutes
        = 0 = no time limit
GA - get ammeter settings
 response: OK currentscalefactor currentoffset
 $GA*AC
GC - get current capacity range in amps
 response: OK minamps maxamps
 $GC*AE
GE - get settings
 response: OK amps(decimal) flags(hex)
 $GE*B0
GF - get fault counters
 response: OK gfitripcnt nogndtripcnt stuckrelaytripcnt (all values hex)
 maximum trip count = 0xFF for any counter
 $GF*B1
GG - get charging current and voltage
 response: OK milliamps millivolts
 AMMETER must be defined in order to get amps, otherwise returns -1 amps
 VOLTMETER must be defined in order to get voltage, otherwise returns -1 volts
 $GG*B2
GH - get cHarge limit
 response: OK kWh
 kWh = 0 = no charge limit
GM - get voltMeter settings
 response: OK voltcalefactor voltoffset
 $GM^2E
GO get Overtemperature thresholds
 response: OK ambientthresh irthresh
 thresholds are in 10ths of a degree Celcius
 $GO^2C
GP - get temPerature (v1.0.3+)
 $GP*BB
 response: OK ds3231temp mcp9808temp tmp007temp
 ds3231temp - temperature from DS3231 RTC
 mcp9808temp - temperature from MCP9808
 tmp007temp - temperature from TMP007
 all temperatures are in 10th's of a degree Celcius
 if any temperature sensor is not installed, its return value will be 0
GS - get state
 response: OK state elapsed
 state: EVSE_STATE_xxx
 elapsed: elapsed charge time in seconds (valid only when in state C)
 $GS*BE
GT - get time (RTC)
 response OK yr mo day hr min sec       yr=2-digit year
 $GT*BF
GU - get energy usage (v1.0.3+)
 $GU*C0
 response OK Wattseconds Whacc
 Wattseconds - Watt-seconds used this charging session, note you'll divide Wattseconds by 3600 to get Wh
 Whacc - total Wh accumulated over all charging sessions, note you'll divide Wh by 1000 to get kWh
GV - get version
 response: OK firmware_version protocol_version
 $GV*C1
 *
 """

import logging, traceback
import datetime
import time
import pathlib
import sys
import thread
import logging
import random

logging.getLogger().setLevel(logging.WARN)

dir_path = str(pathlib.Path(__file__).resolve().parent.parent)
sys.path.append(dir_path + '/common/')

from async_com import AsyncCom 


_states = {
    0: 'unknown',
    1: 'not connected',
    2: 'connected',
    3: 'charging',
    4: 'vent required',
    5: 'diode check failed',
    6: 'gfci fault',
    7: 'no ground',
    8: 'stuck relay',
    9: 'gfci self-test failure',
    10: 'over temperature',
    254: 'sleeping',
    255: 'disabled'
}
_lcd_colors = ['off', 'red', 'green', 'yellow', 'blue', 'violet', 'teal', 'white']
_state_function = { 'FD' : 'ff', 'FE' : 2, 'FS' : 'fe', 'FR' : 2 }
_lcd_types = ['monochrome', 'rgb']
_service_levels = ['A', '1', '2']


state=0
lcd_color=4
# a Serial class emulator 
class Serial:
    
    serial_cmd = None

    ## init(): the constructor.  Many of the arguments have default values
    # and can be skipped when calling the constructor.
    def __init__( self, port='COM1', baudrate = 19200, timeout=1,
                  bytesize = 8, parity = 'N', stopbits = 1, xonxoff=0,
                  rtscts = 0):
        self.name     = port
        self.port     = port
        self.timeout  = timeout
        self.parity   = parity
        self.baudrate = baudrate
        self.bytesize = bytesize
        self.stopbits = stopbits
        self.xonxoff  = xonxoff
        self.rtscts   = rtscts
        self._isOpen  = True
        self._receivedData = None
        self._response = None
        self.serial_cmd = AsyncCom(AsyncCom.SERIAL_CMD_FILE)
        
        thread.start_new_thread(self.processSerialCommands, ((self.serial_cmd,))) 
        logging.debug("Initialising emulated serial connection")

    #$OK State - 1 Not Connected - 2 Connected - 3 Charging - 4 Error - 5 Error
   
    def processSerialCommands(self, serialCmd):
        while True:
            try:
                cmdv = serialCmd.read(2)
                time.sleep(1)
                if cmdv is not None:
                    if cmdv[0] == 'Connect':
                        print("Received Connect on serial shm")
                        self.update_status("$ST 2\r")
                        state=2
                    elif cmdv[0] == 'StartCharging':
                        print("Received StartCharging on serial shm")
                        self.update_status("$ST 3\r")
                        state=3
                    elif cmdv[0] == 'StopCharging':
                        print("Received StopCharging on serial shm")
                        self.update_status("$ST 2\r")
                        state=2
                    elif cmdv[0] == 'Disconnect':
                        print("Received Disconnect on serial shm")
                        self.update_status("$ST 1\r")
                        state=1
                    elif cmdv[0] == 'Disable':
                        print("Received Disable on serial shm")
                        self.update_status("$ST ff\r")
                        state=256
                    elif cmdv[0] == 'Enable':
                        print("Received Enable on serial shm")
                        self.update_status("$ST 2\r")
                        state=2
                    elif cmdv[0] == 'Sleep':
                        print("Received Sleep on serial shm")
                        self.update_status("$ST fe\r")
                        state=255
                    elif cmdv[0] == 'Reset':
                        print("Received Reset on serial shm")
                        self.update_status("$ST 2\r")
                        state=2
                    else:
                        logging.info("Unknown command %s" % cmdv[0])
            except:
                traceback.print_exc()
                logging.error("Exception occurred", exc_info=True)
                continue
                
                        
    def encode(self, response):
        checksum = 0
        for i in bytearray(response, 'ascii'):
            checksum ^= i
        checksum = format(checksum, '02X')
        return (response + '^' + checksum + '\r').encode('ascii')
    
    def time(self, the_datetime=None):
        now = datetime.datetime.now()
        logging.info("%s/%s/%s %s:%s:%s" % (now.month, now.day, now.year, now.hour, now.minute, now.second))
        return (now.year, now.month, now.day, now.hour, now.minute, now.second)
    
    def elapsed(self):
        done, data1 = self._request('GS')
        if done:
            if data1[0] != '3':
                raise KeyError
            done, data2 = self._request('GU')
            if done:
                return {
                    'seconds': int(data1[1]),
                    'Wh': float(data2[0]) / 3600
                }
        raise IOError
    
    def get_response(self, request):
        global state
        request = request.decode("utf-8") 
        print("EVSE Command: ", request, request[0:3])
        #b'$FF E 0^51\r'
        response = "$OK 20"
        rv = request.split(" ")
        request_for = request[0:3]
        p1 = None
        p2 = None
        if len(rv) == 2:
            p1 = rv[1]
        elif len(rv) == 3:
            p1 = rv[1]
            p2 = rv[2]
        else:
            print("Length of command is " + str(len(rv)))
        
        print(p1, p2)
        if random.random() > 0.9:
            return self.encode("$NK 0 0") 
        if request_for == '$FF':
            response = "$OK 20"
        elif request_for == '$FB':
            response =  "$OK 2"  # set backlight color
            print("Backlight color is " + p1)
            lcd_color = int(p1)
        elif request_for == '$FD':
            state = _state_function['FD']
            response =  "$ST " + str(state)  #disable EVSE
        elif request_for == '$FE':
            state = _state_function['FE']
            response =  "$ST " + str(state)  #enable EVSE
        elif request_for == '$FS':
            state = _state_function['FS']
            response =  "$ST " + str(state)  #sleep EVSE
        elif request_for == '$FR':
            state = _state_function['FR']
            response =  "$ST " + str(state)  #reset EVSE
        elif request_for == '$FP':
            response =  "$ST 2"  #enable EVSE
            print("LCD " + p1 + " " + p2)
        elif request_for == '$G3':
            response =  "$OK 2"  # response: OK cnt
        elif request_for == '$GA':
            response =  "$OK 4 1"  # response: OK currentscalefactor currentoffset
        elif request_for == '$GC':
            response =  "$OK 20 32"  # response: OK minamps maxamps
        elif request_for == '$GE': 
            response =  "$OK 32 2" #get settings
        elif request_for == '$GF':
            response =  "$OK 0"  # response: OK gfitripcnt nogndtripcnt stuckrelaytripcnt (all values hex)
        elif request_for == '$GG':
            response =  "$OK 2000, 5000"  # response: OK milliamps millivolts
        elif request_for == '$GH':
            response =  "$OK 200"  # OK kWh
        elif request_for == '$GM':
            response =  "$OK 3, 1"  # OK voltcalefactor voltoffset
        elif request_for == '$GO':
            response =  "$OK 30 40"  # OK ambientthresh irthresh
        elif request_for == '$GP':
            response =  "$OK 30  0  0"  # OK ds3231temp mcp9808temp tmp007temp
        elif request_for == '$GS':
            response =  "$OK " + str(state)  # OK state elapsed
        elif request_for == '$GT':
            response =  "$OK " + self.time()  # response OK yr mo day hr min sec       yr=2-digit year
        elif request_for == '$GU':
            response =  "$OK 600 7200"  # response OK Wattseconds Whacc
        elif request_for == '$GV':
            response =  "$OK 1.2 1.2"  # response: OK firmware_version protocol_version
        elif request_for == '$S0': 
            response =  "$OK"  #S0 0|1 - set LCD type $S0 0*F7 = monochrome backlight $S0 1*F8 = RGB backlight
        elif request_for == '$S1': 
            response =  "$OK" ##S1 yr mo day hr min sec - set clock (RTC) yr=2-digit year
        elif request_for == '$S2':
            response =  "$OK" #S2 0|1 - disable/enable ammeter calibration mode - ammeter is read even when not charging $S2 0*F9 $S2 1*FA
        elif request_for == '$SD':
            response =  "$OK"  #SD 0|1 - disable/enable diode check $SD 0*0B $SD 1*0C
        elif request_for == '$S3':
            response =  "$OK"  #S3 cnt - set charge time limit to cnt*15 minutes (0=disable, max=255)
        elif request_for == '$SA':
            response =  "$OK"  # SA currentscalefactor currentoffset - set ammeter settings
        elif request_for == '$SC':
            response =  "$OK"  #SC amps - set current capacity if amps < minimum current capacity, will set to minimum and return $NK if amps > maximum current capacity, will set to maximum and return $NK
        elif request_for == '$SE': 
            response =  "$OK" #  SE 0|1 - disable/enable command echo $SE 0*0C $SE 1*0D use this for interactive terminal sessions with RAPI.  RAPI will echo back characters as they are typed, and add a <LF> character after its replies. 
            #Valid only over a serial connection, DO NOT USE on I2C
        elif request_for == '$SF': 
            response =  "$OK" # SF 0|1 - disable/enable GFI self test $SF 0*0D $SF 1*0E
        elif request_for == '$SG':
            response =  "$OK" # SG 0|1 - disable/enable ground chec $SG 0*0E  $SG 1*0F
        elif request_for == '$SH':
            response =  "$OK" # SH kWh - set cHarge limit to kWh
        elif request_for == '$SK':
            response =  "$OK" # SK - set accumulated Wh (v1.0.3+) $SK 0*12 - set accumulated Wh to 0
        elif request_for == '$SL': 
            response =  "$OK" # SL 1|2|A  - set service level L1/L2/Auto  $SL 1*14  $SL 2*15  $SL A*24
        elif request_for == '$SM':
            response =  "$OK" #SM voltscalefactor voltoffset - set voltMeter settings
        elif request_for == '$SO': 
            response =  "$OK" #SO ambientthresh irthresh - set Overtemperature thresholds thresholds are in 10ths of a degree Celcius
        elif request_for == '$SR':
            response =  "$OK" #SR 0|1 - disable/enable stuck relay check $SR 0*19 $SR 1*1A
        elif request_for == '$SS':
            response =  "$OK"  # SS 0|1 - disable/enable GFI self-test $SS 0*1A  $SS 1*1B
        elif request_for == '$ST':
            response =  "$OK"  #ST starthr startmin endhr endmin - set timer $ST 0 0 0 0*0B - cancel timer
        elif request_for == '$SV':
            response =  "$OK" #SV 0|1 - disable/enable vent required $SV 0*1D $SV 1*1E
        elif request_for == '$S0':
            response =  "$OK"
        else:
            response = "$NK"
        return self.encode(response)
        
    ## isOpen()
    # returns True if the port to the Arduino is open.  False otherwise
    def isOpen( self ):
        return self._isOpen

    ## open()
    # opens the port
    def open( self ):
        self._isOpen = True

    ## close()
    # closes the port
    def close( self ):
        self._isOpen = False

    ## write()
    # writes a string of characters to the Arduino
    def write(self, byts):
        self._receivedData  = byts
        self._response = self.get_response(self._receivedData)

    def update_status(self, resp):
        self._response = str.encode(resp)
    ## read()
    # reads n characters from the fake Arduino. Actually n characters
    # are read from the string _data and returned to the caller.
    def read(self, n=1 ):
        s = self._response[0:n]
        self._response = self._response[n:]
        #print( "read: now self._data = ", self._data )
        return s

    ## readline()
    # reads characters from the fake Arduino until a \n is found.
    def readline( self ):
        returnIndex = self._response.index( "\n" )
        if returnIndex != -1:
            s = self._response[0:returnIndex+1]
            self._response = self._response[returnIndex+1:]
            return s
        else:
            return b'\r'
        
    ## __str__()
    # returns a string representation of the serial class
    def __str__( self ):
        return  "Serial<id=0xa81c10, open=%s>( port='%s', baudrate=%d," \
               % ( str(self.isOpen), self.port, self.baudrate ) \
               + " bytesize=%d, parity='%s', stopbits=%d, xonxoff=%d, rtscts=%d)"\
               % ( self.bytesize, self.parity, self.stopbits, self.xonxoff,
                   self.rtscts )

def main():
    serial = Serial()
    print(serial.isOpen())
    
    
if __name__ == "__main__":
    main()
    
