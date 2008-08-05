#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

from helpers import Agent

'''

write tests against region/info, a region domain cap
http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Region_Information_.28Resource_Class.29

'''

class testCapRegionInfo(unittest.TestCase):

    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.firstname = config.get('test_cap_region_info_setup', 'firstname')
        self.lastname = config.get('test_cap_region_info_setup', 'lastname')
        self.password = config.get('test_cap_region_info_setup', 'password')
        self.login_uri = config.get('test_cap_region_info_setup', 'login_uri')
        self.region_uri = config.get('test_cap_region_info_setup', 'region_uri')
       
        self.client = Agent()
        # incomplete until a method for retrieving the cap and calling the URL via GET is available
        # will want to post the request for the region/info cap from the sim, and GET it
        
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
        
        print 'Until we can request the url for region/info, we cannot test this'        
        pass

    def test_cap_region_info_online(self):
        """ agent/info cap returns the right response for an online agent """

        print 'Until we can request the url for region/info, we cannot test this' 
        pass
    
    def test_cap_region_info_offline(self):
        """ agent/info cap returns the right response for an offline agent """

        print 'Until we can request the url for region/info, we cannot test this' 
        pass

    # etc etc


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCapRegionInfo))
    return suite

