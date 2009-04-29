"""
@file helpers.py
@date 2008-09-16
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# std lib
import time
#import urllib2 # for the redirect help, ToDo: need to refactor pyogp.lib.base.agentdomain to extract this out 
import ConfigParser
from pkg_resources import resource_stream
import logging

# prep config
config = ConfigParser.ConfigParser()
config.readfp(resource_stream(__name__, 'testconfig.cfg'))

debug = bool(int(config.get('testconfig', 'debug')))

#setup logging

if debug: 

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG) # seems to be a no op, set it for the logger
    formatter = logging.Formatter('%(asctime)-30s%(name)-30s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # setting the level for the handler above seems to be a no-op
    # it needs to be set for the logger, here the root logger
    # otherwise it is NOTSET(=0) which means to log nothing.
    logging.getLogger('').setLevel(logging.DEBUG)
    logger = logging.getLogger('pyogp.interop.helpers')

    logger.debug('setting debug to True')
