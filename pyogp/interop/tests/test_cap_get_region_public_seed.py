"""
@file test_cap_get_region_public_seed.py
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
import unittest, time
import ConfigParser
from pkg_resources import resource_stream

# pygop
from pyogp.lib.base.registration import init
from pyogp.lib.base.regiondomain import Region

# pyogp.interop
import helpers

'''
# in progress, tests are skipped

Tests for a get against the region public_seed:
* region_url given to rez_avatar/place is now a public_seed which when 
invoked with a get returns a map of public capabilities it has 
available, namely rez_avatar/request
i.e http://sim2.vaak.lindenlab.com:13001/public_seed  returns  
{'capabilities': {'rez_avatar/request': <url>}}


'''

class GetRegionPublicSeed(unittest.TestCase):
    """ test posting to rez_avatar/derez for a simulator, acting as the region domain """

    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
       
        self.start_region_uri = config.get('test_interop_regions', 'start_region_uri')  
        
        # set up a region
        self.region = Region(self.start_region_uri)   
        
    def tearDown(self):
        pass
        # uncomment once this test can be used
        # self.client.logout()

    def check_successful_response(self, results):
        """ check the the existence of the correct parameters in the cap response """
       
        pass

    def check_failure_response(self, results):
        """ check the the existence of the correct parameters in the cap response """
        
    def test_get_valid_region_public_seed(self):
        """ agent is allowed to derez """

        result = self.region.get_region_public_seed()
        
        print result

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(GetRegionPublicSeed))
    return suite

