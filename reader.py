# Title: reader.py
# Author: Sean O'Bryan
# Goal: Use rfid reader with raspberry pi.
# Description: 
#	1.	When presented with an appropriate rfid tag (uem4100), rfid reader gives raspberry pi a message through serial (uart pins).  
#	2.	Raspberry pi (code below) parses key from valid message and checks the key against a text file (access control list).  
#	3.	Raspberry pi opens door.

# Links: 	rfid reader - http://www.seeedstudio.com/depot/Electronic-brick-125Khz-RFID-Card-Reader-p-702.html
#			raspberry pi model b revision 2.0

# The exception will generate a custom message (error_message)
# The exception will generate a stacktrace
def throws(error_message):
	raise RuntimeError(error_message)

# Get the rfid message, log/break if message format is bad
def extract_message(rfidInput):
	rfidInput = enclosing_tags_check(rfidInput)
	hex_check(rfidInput)
	compute_check_sum(rfidInput)
	return rfidInput[:-2]
	
def hex_check(rfidInput):
	import string
	if not all(c in string.hexdigits for c in rfidInput):
		throws("Message contains invalid hex characters")
		
def compute_check_sum(rfidInput):
	given = hex(int(rfidInput[10:],16))
	rfidInput = rfidInput[:-2]
	uncomputed = bytearray.fromhex(rfidInput)
	computed = hex(uncomputed[0] ^ uncomputed[1] ^ uncomputed[2] ^ uncomputed[3] ^ uncomputed[4])
	logger.info("Given checksum is %s" % given)
	logger.info("Computed checksum is %s" % computed)
	if computed != given:
		throws("Checksum is bad")

# Validating the incoming message
# upon success, input returned with message and checksum only 
def enclosing_tags_check(rfidInput):
	startTag = "\x02"
	endTag = "\x03"
	if rfidInput.startswith(startTag):
		rfidInput = rfidInput.replace(startTag,'')
	else:
		throws("Enclosing tag not present")
	if rfidInput.endswith(endTag):
		rfidInput = rfidInput.replace(endTag,'')
	else:
		throws("Enclosing tag not present")
	if len(rfidInput) != 12:
		throws("Message is not correct length")
	return rfidInput

# Query the access control list (acl)
# check access list for the rfid tag
def query_acl(rfid):
	with open('acl') as text:
		for line in text:
			member = line.split('|')
			id = member[0]
			key = member[1]
			if rfid == key:
				logger.info("id:%s has successfully authenticated" % id)
				text.close()
				return True
	return False;
	
# Open the door
def request_access():
	logger.info("access granted")
	
# Take the incoming message and do stuff
def handle_message(incoming_message):
	logger.info("******** Start Message ********") # Start logging block
	logger.info("Received a new message: %s" % incoming_message) # log incoming message
	try:
		rfid_message = extract_message(incoming_message) # Get the rfid message, log/break if message format is bad
		query_acl(rfid_message) # check access list for the rfid tag
		request_access() # Open the door
	except:
		logger.exception("Exception as follows")
		raise
	finally:
		logger.info("********* End Message *********")
		logger.info("")

	
# Setup logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# create a file handler
handler = logging.FileHandler('reader.log')
handler.setLevel(logging.INFO)
# create a logging format
formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(message)s')
handler.setFormatter(formatter)
# add the handlers to the logger
logger.addHandler(handler)

# Setup Serial port
import serial
port = serial.Serial("/dev/ttyAMA0", baudrate=9600, timeout=3.0)
while True:
	try:
		incoming_message = port.read(14) # Get the incoming message
		if incoming_message != '':
			handle_message(incoming_message) # Parse the incoming message			
	except:
		logger.info("Exception")
