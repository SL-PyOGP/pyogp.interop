"""
@file test_cap_region_info.py
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
import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.caps import Capability

# pyogp.interop
import helpers

'''
NOT YET AVAILABLE (documented, not implemented)

write tests against region/info, a region domain cap
http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Region_Information_.28Resource_Class.29

'''

class testCapRegionInfo(unittest.TestCase):

    def setUp(self):
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.firstname = config.get('test_interop_account', 'firstname')
        self.lastname = config.get('test_interop_account', 'lastname')
        self.password = config.get('test_interop_account', 'password')
        self.login_uri = config.get('test_interop_account', 'login_uri')
        
        self.region_uri = config.get('test_interop_regions', 'start_region_uri')
       
        #self.client = Agent()
        # will want to post the request for the region/info cap to the sim seedcap, and GET it
        
    def tearDown(self):

        # uncomment once tests can be run        
        # self.client.logout()
        '''
        if {agent is logged in flag is set}
            self.client.logout()
        '''
    
    def getCap(self):
        """ sends a get to the cap """

        try:
            result = self.capability.GET()
        except Exception, e:
            #print 'Exception: ' + e.message + ' ' + str(e.args)
            result = str(e.args)

        return result
    
    def check_response_base(self, result):
        """ check for the eistence of the correct parameters in the cap response """

        # successful response contains: 
        # {sim_ip: string , sim_port: int . region_x: int , region_y: int , region_z: int , region_id: uuid , access: 'PG' | 'Mature' }
        self.assert_(result.has_key('sim_ip') and
                     result.has_key('sim_port') and
                     result.has_key('region_x') and
                     result.has_key('region_y') and
                     result.has_key('region_z') and
                     result.has_key('region_id') and
                     result.has_key('access'))

###################################
#           Test Cases            #
###################################
    # region/info is implemented, no reason to write tests for it


    def test_cap_region_info_base(self):
        """ agent/info cap returns the right reponse with the right inputs params """
        
        print 'This resource is not available to test at this time...'        
        pass

'''
    def test_cap_region_info_online(self):
        """ agent/info cap returns the right response for an online agent """

        print 'Until we can request the url for region/info, we cannot test this' 
        pass
    
    def test_cap_region_info_offline(self):
        """ agent/info cap returns the right response for an offline agent """

        print 'Until we can request the url for region/info, we cannot test this' 
        pass
'''
    # etc etc


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCapRegionInfo))
    return suite

