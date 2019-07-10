# evdevice 0.1 Alpha

This code emulates the serial communication between OpenEVSE and OCPP module. To run this on debian or any other flavour of linux you need to satisfy following dependencies. The instructions will be for debian(jessie) :

Step 1.

Clone this repo, preferably in root folder. Instructions will assume that the git repo resides in '/root/'.

git clone https://<your-github-userid>@github.com/gitibeyonde/openevse-ocpp.git evdevice

IF the above repo is private then you need to provide login and password for github to clone it.

Step 2:

Change directory to evdevice/base

run base.sh to install prerequisites

Step 3

Setup OCPP Server (Steve) and the emulator device. A demo server is set here and the codebase is configured to use it.
The config is in system.properties file

On the Steve add a device, by choosing a uuid. # opptitest is a existing user on demo steve and is set by default
Set this uuid in evdevice/.uuid file.


Step 4

Run ocpp.py in evdevice/ocpp folder. 
./ocpp.py
This will start the process that listens to status changes form OpenEVSE and contacts OCPP server to pass on information if required.

Step 5

You can simulate openEVSE by running commands like "./cmdln.py rfid <id of user set in step 5>" in evdevice/ocpp folder. For exampole this command will send an Authorize request to OCPP 1.5J server implementation.

./cmdln.py rfid d6gsNICFc5UQq4mxwpnV # you can use this id, it is precreated on demo server
./cmdln.py connect
./cmdln.py start
./cmdln.py stop
./cmdln.py disconnect

The above commands will simulate typical openEVSE charging session.


Step 6

Setup the serial connection on raspberry pi to connect to openevse. You will need a level shifter to be able to do that. ref: https://www.sparkfun.com/products/12009

The respberrypi side of the serial port runs optimally at 0 to 3.3V while at the openevse end they run at 0 to 5V. The Tx (physical pin 8) and Rx (physical pin 10) pins on raspberry pi
need to be connected to the LV pins while the Tx and Rx of the OpenEVSE needs to be connected to HV pins of the level shifter. Note that Tx of Pi needs to connect to Rx or OpenEVSE and similary for the other serial port. 

Also connect the Raspberry pi's physical pin 4 (5V input) and 6 (Gnd) to the corresponding power pins on openEVSE.

Edit system.properties and change the line "capability=OPENEVSE_EMULATOR" to "capability=OPENEVSE". This will enable the serial port to openEVSE. Now you are all set to interact with openEVSE.

For any queries contact info@ibeyonde.com
