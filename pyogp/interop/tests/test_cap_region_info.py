#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

from helpers import Agent

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
       
        self.clent = Agent()
        
    def tearDown(self):
        
        self.client.logout()
        '''
        if self.client.agentdomain != None:
            self.client.logout()
        '''
    
    def getCap(self):
        """ sends a get to the cap """

        # create a helper to get the cap

    '''
    def postToCap(self, arguments):
        try:
            result = self.capability.POST(arguments)
            print result
        except Exception, e:
            print 'Exception: ' + e.message + ' ' + str(e.args)
            return

        return result
    '''
    
    def check_response_base(self, result):
        """ check for the eistence of the correct parameters in the cap response """

        # {sim_ip: string , sim_port: int . region_x: int , region_y: int , region_z: int , region_id: uuid , access: 'PG' | 'Mature' }
        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position'))


    '''

    write tests against agent/info, an agent domain cap
    http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Region_Information_.28Resource_Class.29

    '''

    def test_cap_region_info_base(self):
        """ agent/info cap returns the right reponse with the right inputs params """
        pass

    def test_cap_region_info_online(self):
        """ agent/info cap returns the right response for an online agent """
        pass
    
    def test_cap_region_info_offline(self):
        """ agent/info cap returns the right response for an offline agent """
        pass

    # etc etc


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCapRegionInfo))
    return suite

