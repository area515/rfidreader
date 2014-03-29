rfidreader
==========

Goal: Use rfid reader with raspberry pi.

Description: 	
	1.	When presented with an appropriate rfid tag (uem4100), rfid reader gives raspberry pi a message through serial (uart pins).  
	2.	Raspberry pi (code below) parses key from valid message and checks the key against a text file (access control list).  
	3.	Raspberry pi opens door.

Links: 	rfid reader - http://www.seeedstudio.com/depot/Electronic-brick-125Khz-RFID-Card-Reader-p-702.html
	rfid wiki - http://www.seeedstudio.com/wiki/index.php?title=Electronic_brick_-_125Khz_RFID_Card_Reader
	raspberry pi model b revision 2.0


To Use:

The code is ready to be used on a raspberry pi connected to an rfid reader (through uart).  Open (or create) the text file named 'acl'.  Add an id and key, seperated by '|'.  For example

1|04023AF855 <-- '1' is the id associated with the key '04023AF855'

2|03003AA855 <-- '2' is the id associated with the key '03003AA855'

To Test (without a pi and/or rfid reader)
	Open reader.py and follow the instructions in the test section. 
