'''
Created on May 25, 2014

@author: rtxn0378
'''

from os import sys
import argparse
import serial
import RPi.GPIO as GPIO
import log
import time
import string
import traceback # from debugging
import threading

test = ''
logger = log.setup_logger('reader.log')

def throws(error_message):
    raise RuntimeError(error_message)

class Authenticator(object):
    '''
    classdocs
    '''
    @staticmethod
    def query(rfidkey):
        with open('acl') as text:
            for line in text:
                member = line.split('|')
                id = member[0]
                key = member[1].strip()
                if rfidkey == key:
                    logger.info("id:%s has successfully authenticated" % id)
                    text.close()
                    return True
        logger.info("rfid did not authenticate")
        return False


class Solenoid(object):
    '''
    classdocs
    '''

    def __init__(self, pin=12, openduration=10):
        '''
        Constructor
        '''
        self.pin = pin
        self.openduration = openduration
        self.setup_gpio()
        
    # Setup GPIO (for later use)
    def setup_gpio(self):
        
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pin, GPIO.OUT)
        
    # Open the door
    def open_door(self):
        logger.info("door is open")
        GPIO.output(self.pin, True)
        time.sleep(self.openduration)
        GPIO.output(self.pin, False)
        logger.info("door is closed")
    
    



class Reader(object):
    '''
    classdocs
    '''
  

    def __init__(self, solenoid=None, port="/dev/ttyAMA0", baudrate=9600, readtimeout=10):
        '''
        Constructor
        '''
        
        self.rfidInput = None
        self.incoming_message = None
        self.solenoid = solenoid
        self.port= port 
        self.baudrate = baudrate
        self.readtimeout = readtimeout
        self.thread = None
        self.lastkey = ''
        self.connection = None

    
    # Validating the incoming message
    # upon success, input returned with message and checksum only
    def enclosing_tags_check(self):
    
        startTag = "\x02"
        endTag = "\x03"

        logger.info(self.rfidInput)
        logger.info(startTag)
        #check for startTag
        if self.rfidInput.startswith(startTag):
            self.rfidInput = self.rfidInput.replace(startTag, '')
        else:
            throws("Enclosing tag not present")
        #check for endTag
        if self.rfidInput.endswith(endTag):
            self.rfidInput = self.rfidInput.replace(endTag, '')
        else:
            throws("Enclosing tag not present")
        #length check
        if len(self.rfidInput) != 12:
            throws("Message is not correct length")
        
        
    # Get the rfid message, log/break if message format is bad
    def extract_message(self):
    
        self.enclosing_tags_check() 
        self.hex_check()
        self.compute_check_sum()
        self.rfidInput = self.rfidInput[:-2]
    
    def hex_check(self):
        
        if not all(c in string.hexdigits for c in self.rfidInput):
            throws("Message contains invalid hex characters")


    def compute_check_sum(self):
        given = hex(int(self.rfidInput[10:], 16))
        self.rfidInput = self.rfidInput[:-2]
        uncomp = bytearray.fromhex(self.rfidInput)
        computed = (
            hex(uncomp[0] ^ uncomp[1] ^ uncomp[2] ^ uncomp[3] ^ uncomp[4]))
    
        #logger.info("Given checksum is %s" % given)
        #logger.info("Computed checksum is %s" % computed)
        if computed != given:
            throws("Checksum is bad")
            

    # Take the incoming message and do stuff
    def handle_message(self, solenoid):
        
        logger.info("******** Start Message ********")
        logger.info("Received a new message")
        #logger.info("Received a new message: %s" % incoming_message)
        try:
            # Get the rfid message, log/break if message format is bad
            self.extract_message()
            self.lastkey = self.rfidInput
            # check access list for the rfid tag
            if Authenticator.query(self.rfidInput):
                if solenoid is not None:
                    logger.info("Opening door")
                    solenoid.open_door()  # Open the door
        except:
            logger.exception("Exception as follows")
            raise
        finally:
            logger.info("********* End Message *********")
            logger.info("")

    def stop(self):
        
        self.connection = False
        self.thread.join()
            
    def read_from_port(self, connection):
        self.connection = True
        while self.connection:
            try:
                self.rfidInput = connection.read(14)  # Get the incoming message
                if self.rfidInput != '':
                    self.handle_message(self.solenoid)  # Parse the incoming message
            except:
                traceback.print_exc()
        
    def start(self):

        connection = serial.Serial(self.port, baudrate=self.baudrate, timeout=self.readtimeout)
        self.thread = threading.Thread(target=self.read_from_port, args=(connection,))
        self.thread.start()

def parse_args(args):
    """Takes command line arguments and processes them

    -p          --port            <string>   "/dev/ttyAMA0"
    -b          --baudrate        <int>      9600
    -r          --readtimeout    <float>    3.0A
    -l          --logging        <boolean>  True
    -lo         --log            <string>   "/reader.log"
    -s          --solenoid        <int>      12
    -o          --openduration    <int>    10
    sudo python readertest.py -p "/dev/ttyAMA0" -b 9600 -t 3.0 -l True -lo "/reader.log" -s 12
    """

    parser = argparse.ArgumentParser(prefix_chars='-')

    parser.add_argument('-p', '--port', type=str)
    parser.add_argument('-b', '--baudrate', type=int)
    parser.add_argument('-r', '--readtimeout', type=float)
    parser.add_argument('-l', '--logging', type=bool)
    parser.add_argument('-lo', '--log', type=str)
    parser.add_argument('-s', '--solenoid', type=int)
    parser.add_argument('-o', '--openduration', type=int)

    parsed_args, unknown = parser.parse_known_args(args)

    return parsed_args


def main():
    """Parse the command line config and start listening on associated ports.
    """

    # parse the args
    args = parse_args(sys.argv)
    # setup the logger
    print args.log
    logger = log.setup_logger(args.log)
    # make a solenoid
    solenoid = Solenoid(args.solenoid, args.openduration)
    # make an rfid reader
    reader = Reader(solenoid, args.port, args.baudrate, args.readtimeout)
    # start the reader
    reader.start()

if __name__ == "__main__":
    main()
