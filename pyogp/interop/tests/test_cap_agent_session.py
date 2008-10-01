"""
@file test_cap_agent_info.py
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

# pygop
from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability
from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region

# pyogp.interop
import helpers

'''

write tests against agent/info, an agent domain cap
http://wiki.secondlife.com/wiki/OGP_Teleport_Draft_3#GET_Interface_2

'''

class testCapAgentSession(unittest.TestCase):

    def setUp(self):
        init()
        
        '''
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = config.get(self.test_setup_config_name, 'firstname')
        self.lastname = config.get(self.test_setup_config_name, 'lastname')
        self.password = config.get(self.test_setup_config_name, 'password')
        self.login_uri = config.get(self.test_setup_config_name, 'login_uri')        
        self.region_uri = config.get('test_interop_regions', 'start_region_uri') 

        # first establish an AD connection and get seed_cap for mtg
        # <start>
        self.agentdomain = AgentDomain(self.login_uri)
        
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)

        #gets seedcap, and an agent that can be placed in a region
        self.agentdomain.login(credentials)
 
        '''
        
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
            result = self.caps['agent/info'].GET()
        except Exception, e:
            #print 'Exception: ' + e.message + ' ' + str(e.args)
            result = str(e.args)

        return result
    
    def check_response_base(self, result):
        """ check for the existence of the correct parameters in the cap response """

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
    # Add moar tests

                     
    def test_cap_agent_session(self):
        """ agent/info cap returns the right response for an online agent """

        print 'This resource is not available to test at this time...'
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCapAgentSession))
    return suite

