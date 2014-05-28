'''
Created on May 24, 2014

@author: Sean O'Bryan, Ross Hendrickson  
'''

import logging

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
