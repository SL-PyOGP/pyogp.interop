#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

from helpers import Agent

'''

write tests against agent/info, an agent domain cap
http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Region_Information_.28Resource_Class.29

'''

class testCapAgentInfo(unittest.TestCase):

    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.firstname = config.get('test_cap_agent_info_setup', 'firstname')
        self.lastname = config.get('test_cap_agent_info_setup', 'lastname')
        self.password = config.get('test_cap_agent_info_setup', 'password')
        self.login_uri = config.get('test_cap_agent_info_setup', 'login_uri')
        self.region_uri = config.get('test_cap_agent_info_setup', 'region_uri')
       
        self.client = Agent()
        # have to auth before being able to get the agent/info cap
        # incomplete until a method for retrieving the cap and calling the URL via GET is available
        
    def tearDown(self):
        
        # uncomment once tests can be run
        # self.client.logout()
        '''
        if {agent is logged in flag is set}
            self.client.logout()
        '''
    
    def getCap(self):
        """ sends a get to the cap """

        # create a helper to get the cap
    
    def check_response_base(self, result):
        """ check for the eistence of the correct parameters in the cap response """

        # successful response contains: 
        # { agent_id: uuid , circuit_code: int , session_id: uuid , secure_session_id: uuid , presence: { status: "online"|"offline" , region_url: url } }
        self.assert_(result.has_key('agent_id') and
                     result.has_key('circuit_code') and
                     result.has_key('session_id') and
                     result.has_key('secure_session_id') and
                     result.has_key('presence'))

###################################
#           Test Cases            #
###################################
    # Until a GET exists for caps (need to clear this up with LL and pyogp), no tests can be run

                     
    def test_cap_agent_info_online(self):
        """ agent/info cap returns the right response for an online agent """
        
        print 'Until we can request the url for agent/info, we cannot test this'
        pass
    
    def test_cap_agent_info_offline(self):
        """ agent/info cap returns the right response for an offline agent """
        
        print 'Until we can request the url for agent/info, we cannot test this'
        pass

    # etc etc


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCapAgentInfo))
    return suite

