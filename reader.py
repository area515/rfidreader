#!/usr/bin/env python
# Title: reader.py
# Author: Sean O'Bryan, Ross Hendrickson
# Goal: Use rfid reader with raspberry pi.
# Description:
#	1.	When presented with an appropriate rfid tag (uem4100), rfid reader gives raspberry pi a message through serial (uart pins).
#	2.	Raspberry pi (code below) parses key from valid message and checks the key against a text file (access control list).
#	3.	Raspberry pi opens door.

# Links: 	rfid reader - http://www.seeedstudio.com/depot/Electronic-brick-125Khz-RFID-Card-Reader-p-702.html
#			raspberry pi model b revision 2.0

# The exception will generate a custom message (error_message)
# The exception will generate a stacktrace

from os import sys
import RPi.GPIO as GPIO
import argparse
import logging
import serial
import string
import time
import traceback # for debuging

def throws(error_message):
    raise RuntimeError(error_message)


# Get the rfid message, log/break if message format is bad
def extract_message(logger, rfidInput):

    rfidInput = enclosing_tags_check(rfidInput) 
    hex_check(rfidInput)
    compute_check_sum(logger, rfidInput)
    return rfidInput[:-2]


def hex_check(rfidInput):
    if not all(c in string.hexdigits for c in rfidInput):
        throws("Message contains invalid hex characters")


def compute_check_sum(logger, rfidInput):
    given = hex(int(rfidInput[10:], 16))
    rfidInput = rfidInput[:-2]
    uncomp = bytearray.fromhex(rfidInput)
    computed = (
        hex(uncomp[0] ^ uncomp[1] ^ uncomp[2] ^ uncomp[3] ^ uncomp[4]))

    #logger.info("Given checksum is %s" % given)
    #logger.info("Computed checksum is %s" % computed)
    if computed != given:
        throws("Checksum is bad")


# Validating the incoming message
# upon success, input returned with message and checksum only
def enclosing_tags_check(rfidInput):

    startTag = "\x02"
    endTag = "\x03"
    #check for startTag
    if rfidInput.startswith(startTag):
        rfidInput = rfidInput.replace(startTag, '')
    else:
        throws("Enclosing tag not present")
    #check for endTag
    if rfidInput.endswith(endTag):
        rfidInput = rfidInput.replace(endTag, '')
    else:
        throws("Enclosing tag not present")
    #length check
    if len(rfidInput) != 12:
        throws("Message is not correct length")

    return rfidInput


# Query the access control list (acl)
# check access list for the rfid tag
def query_acl(logger, rfid):
    with open('acl') as text:
        for line in text:
            member = line.split('|')
            id = member[0]
            key = member[1].strip()
            if rfid == key:
                logger.info("id:%s has successfully authenticated" % id)
                text.close()
                return True
    logger.info("rfid did not authenticate")
    return False


# Open the door
def open_door(logger, solenoid, speed):
    logger.info("door is open")
    GPIO.output(solenoid, True)
    time.sleep(speed)
    GPIO.output(solenoid, False)
    logger.info("door is closed")


# Take the incoming message and do stuff
def handle_message(logger, incoming_message, solenoid, speed):
    logger.info("******** Start Message ********")
    logger.info("Received a new message")
    #logger.info("Received a new message: %s" % incoming_message)
    try:
        # Get the rfid message, log/break if message format is bad
        rfid_message = extract_message(logger, incoming_message)

        # check access list for the rfid tag
        if query_acl(logger, rfid_message):
            logger.info("Opening door")
            open_door(logger, solenoid, speed)  # Open the door
    except:
        logger.exception("Exception as follows")
        raise
    finally:
        logger.info("********* End Message *********")
        logger.info("")


class Server(object):

    def __init__(self, solenoid, speed, args):

        self.solenoid = solenoid
        self.speed = speed
        self.args = args
        self.logger = None


def setup_server(args):

    server = Server(solenoid=args.solenoid, speed=10, args=args)

    return server


# Setup GPIO (for later use)
def setup_gpio(solenoid):
    
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(solenoid, GPIO.OUT)


def setup_logger(log_filename):

    # Setup logger
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)
    # create a file handler
    handler = logging.FileHandler(log_filename)
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    logger.addHandler(handler)
    
    return logger


def setup_serial(logger, port="/dev/ttyAMA0", baudrate=9600, timeout=3.0, solenoid=12, speed=10):

    connection = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=3.0)
    while True:
        try:
            incoming_message = connection.read(14)  # Get the incoming message
            if incoming_message != '':
                handle_message(logger, incoming_message, solenoid, speed)  # Parse the incoming message
        except:
            logger.info("Exception")
            logger.info("Cleaning up pin resources...")
            GPIO.cleanup()


def start_server(args):

    server = setup_server(args)

    setup_gpio(server.solenoid)
    if args.logging:
        server.logger = setup_logger(args.log)
    server.logger.info("Heading into the setup serial")
    setup_serial(server.logger, args.port, args.baudrate, args.timeout, args.solenoid, server.speed)


def parse_args(args):
    """Takes command line arguments and processes them

    -p          --port       <string>   "/dev/ttyAMA0"
    -b          --baudrate   <int>      9600
    -t          --timeout    <float>    3.0A
    -l          --logging    <boolean>  True
    -lo         --log        <string>   "/reader.log"
    -s          --solenoid   <int>      12
    sudo python readertest.py -p "/dev/ttyAMA0" -b 9600 -t 3.0 -l True -lo "/reader.log" -s 12
    """

    parser = argparse.ArgumentParser(prefix_chars='-')

    parser.add_argument('-p', '--port', type=str)
    parser.add_argument('-b', '--baudrate', type=int)
    parser.add_argument('-t', '--timeout', type=float)
    parser.add_argument('-l', '--logging', type=bool)
    parser.add_argument('-lo', '--log', type=str)
    parser.add_argument('-s', '--solenoid', type=int)

    parsed_args, unknown = parser.parse_known_args(args)

    return parsed_args


def main():
    """Parse the command line config and start listening on associated ports.
    """

    args = parse_args(sys.argv)
    start_server(args)


if __name__ == "__main__":
    main()
