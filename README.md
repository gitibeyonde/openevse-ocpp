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

