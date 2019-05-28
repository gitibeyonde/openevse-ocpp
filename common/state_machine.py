#!/usr/bin/env python3

import ephemeral
import logging
import time

logging.getLogger().setLevel(logging.DEBUG)
tstore = ephemeral.Ephemeral()

class StateMachine:

    states = {
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

    def login(self, username):
        tstore.setValue("username", username)
        tstore.setValue("state", 1)
        
    def connect(self):
        cur_state = self.getState()
        if cur_state != 1:
            print("Connected bad state")
            return False
        print("Connected")
        tstore.setValue("state", 2)
        return True
    
    def startCharging(self, transId):
        cur_state = self.getState()
        if cur_state != 2:
            print("Charging started bad state")
            return False
        print("Charging started")
        tstore.setValue("state", 3)
        tstore.setValue("start_time", int(time.time()))
        tstore.setValue("transactionId", transId)
        return True
    
    def stopCharging(self):
        cur_state = self.getState()
        if cur_state != 3:
            print("Charging stop bad state")
            return False
        print("Charging stopped")
        tstore.setValue("state", 2)
        delta = time.time() - int(tstore.getValue("start_time"))
        tstore.delValue("start_time")
        tstore.delValue("transactionId")
        return delta
        
    def disconnect(self):
        cur_state = self.getState()
        if cur_state != 2:
            print("Disconnected bad state")
            return False
        print("DisConnected")
        tstore.setValue("state", 0)
        return True
    
    def transitionTo(self, next_state):
        cur_state = self.getState()
        next_state = self.getStateKey(next_state)
        logging.debug("Cur State = %s, Next State = %s"%(cur_state, next_state))
        if cur_state == 0:
            print("Please login")
            return True
        elif cur_state == 1 and next_state == 2:
            print("Charger connected")
            self.setState(key=next_state)
            return True
        elif cur_state == 2 and next_state == 3:
            print("Charging started")
            self.setState(key=next_state)
            tstore.setValue("start_time", int(time.time()))
            return True
        elif cur_state == 3 and next_state == 2:
            print("Charging stopped")
            return True
            self.setState(key=next_state)
        elif cur_state == 3 and next_state == 1:
            print("Charging stopped and charger disconnected")
            return True
        elif cur_state == 2 and next_state == 1:
            print("Charger disconnected")
            self.setState(key=next_state)
            return True
        elif cur_state == 1 and next_state == 0:
            self.setState(key=next_state)
            print("Logged out")
            return True
        else:
            print("Invalid state transition")
            return False
        
    def isCharging(self):       
        cur_state = self.getState()
        if cur_state == 3: return True
        else: return False
    
    def isConnected(self):       
        cur_state = self.getState()
        if cur_state == 3 or cur_state == 2: return True
        else: return False
    
    def reset(self):
        self.setState("unknown")
        tstore.delValue("transactionId")
        tstore.delValue("username")

    def setState(self, state_name=None, key=None):
        global tstore
        if state_name is not None:
            key = self.getStateKey(state_name)
        tstore.setValue("state", key)
            
    def getStringState(self):
        global tstore
        state = tstore.getValue("state")
        if not state: state = 0
        return self.states[int(state)]
    
    def getState(self):
        global tstore
        state = tstore.getValue("state")
        if not state: 
            state = 0
            self.setState(key=0)
        return int(state)
    
    def getUsername(self):
        return tstore.getValue("username")
        
    def setUsername(self, name):
        tstore.setValue("username", name)
            
    def getTransactionId(self):
        return tstore.getValue("transactionId") 
        
    def getStateKey(self, state_name):
        for key, name in self.states.items():
            print(state_name, " -> getStateKey Name=",name,", Key=" ,key)
            if state_name == name:
                return int(key)
            else:
                continue
        return 0

def main():#'tIrBKzpACDpNc9il3Vbn'
    sm = StateMachine()
    sm.login('tIrBKzpACDpNc9il3Vbn')
    tstore.printAllKeys()
    sm.transitionTo("connected")
    tstore.printAllKeys()
    sm.transitionTo("charging")
    tstore.printAllKeys()
    sm.transitionTo("connected")
    tstore.printAllKeys()
    sm.transitionTo("not connected")
    tstore.printAllKeys()
    sm.transitionTo("unknown")
    tstore.printAllKeys()
    
    
if __name__ == "__main__":
    main()
    
