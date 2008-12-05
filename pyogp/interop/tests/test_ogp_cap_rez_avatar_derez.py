"""
@file test_cap_rez_avatar_derez.py
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
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.agentdomain import AgentDomain, EventQueue
from pyogp.lib.base.caps import Capability
from pyogp.lib.base.regiondomain import Region

# pyogp.interop
import helpers

'''
# in progress, tests are skipped

Tests for the rez_avatar/derez capability as run against simulators (acting as the agent domain)

write tests against the protocol as is defined at 
http://wiki.secondlife.com/wiki/OGP_Teleport_Draft_3#POST_Inferface
'''

class RezAvatarDerezTest(unittest.TestCase):
    """ test posting to rez_avatar/derez for a simulator, acting as the region domain """

    def setUp(self):
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = config.get(self.test_setup_config_name, 'firstname')
        self.lastname = config.get(self.test_setup_config_name, 'lastname')
        self.password = config.get(self.test_setup_config_name, 'password')
        self.login_uri = config.get(self.test_setup_config_name, 'login_uri')        
        self.start_region_uri = config.get('test_interop_regions', 'start_region_uri') 
        self.target_region_uri = config.get('test_interop_regions', 'target_region_uri') 
        
        # first establish an AD connection and get seed_cap for mtg
        # <start>
        agent = Agent()

        # establish agent credentials
        agent.setCredentials(self.firstname, self.lastname, self.password)

        # initialize an agent domain object
        self.agentdomain = AgentDomain(self.login_uri)  
        self.agentdomain.login(agent.credentials)
 
        caps = self.agentdomain.seed_cap.get(['rez_avatar/place'])

        # place the avatar on a region via the agent domain
        self.region = Region(self.region_uri)
        self.region.details = self.agentdomain.place_avatar(self.region.region_uri)
        # </start>

        # this is the region we will test against
        self.region2 = Region(self.test_region_uri)        
        result = self.region2.get_region_public_seed()
        
        caps = result['capabilities']     
        
        # initialize a one off cap object
        self.request_capability = Capability('rez_avatar/request', caps['rez_avatar/request'])  
      
        # these are the required params for rez_avatar/request post 
        self.request_required_parameters = {
            'agent_id' : self.avatar.region.details['agent_id'],
            'circuit_code' : self.avatar.region.details['circuit_code'],
            'secure_session_id' :self.avatar.region.details['secure_session_id'],
            'session_id' : self.avatar.region.details['session_id'],
            'first_name' : self.firstname,
            'last_name' :self.lastname
        }


        self.request_full_parameters = self.request_required_parameters
        
        self.request_full_parameters['position'] = config.get('test_rez_avatar_request', 'position')
        self.request_full_parameters['age_verified'] = config.get('test_rez_avatar_request', 'age_verified_true')
        self.request_full_parameters['agent_access'] = config.get('test_rez_avatar_request', 'agent_access_true')
        self.request_full_parameters['allow_redirect'] = config.get('test_rez_avatar_request', 'allow_redirect_true')
        self.request_full_parameters['god_level'] = config.get('test_rez_avatar_request', 'god_level_0')
        self.request_full_parameters['identified'] = config.get('test_rez_avatar_request', 'identified_true')
        self.request_full_parameters['transacted'] = config.get('test_rez_avatar_request', 'transacted_true')
        self.request_full_parameters['limited_to_estate'] = config.get('test_rez_avatar_request', 'limited_to_estate_mainland')
        self.request_full_parameters['src_can_see_mainland'] = 'Y'
        self.request_full_parameters['src_estate_id'] = 1

        result = self.request_capability.POST(self.request_full_parameters)

        '''

        derez_capability = Capability('rez_avatar/rez', result['capabilities']['rez_avatar/rez'])

        # Required parameters: { rez-avatar/rez: url string, position: [x real, y real, z real, ] }              
        self.derez_required_parameters = {
            'rez_avatar/rez' : self.rez_avatar_url,
            'position' : self.position
            }
        
        self.capability = Capability('rez_avatar/derez', self.derez_avatar_url)              
        '''
        
    def tearDown(self):
        pass
        # uncomment once this test can be used
        # self.client.logout()


    def postToCap(self, arguments):
      
        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            print 'Exception: ' + e.message + ' ' + str(e.args)
            result = {}
            return
       
        return result

    def check_successful_response(self, results):
        """ check the the existence of the correct parameters in the cap response """
       
        # { connect: "True" , look_at: [x real ,y real, z real, ] , position: [x real ,y real, z real, ]}
        
        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position'))

        self.assertEquals(result['connect'], True)
        self.assert_(result['position'][0] < 256)
        self.assert_(result['position'][1] < 256)
        self.assert_(result['position'][2] < 256)

    def check_failure_response(self, results):
        """ check the the existence of the correct parameters in the cap response """
        
    def test_rez_avatar_derez_connect(self):
        """ agent is allowed to derez """
        pass
        '''
        result = self.postToCap(self.required_parameters)
        
        self.check_successful_response(result)
        self.assertEquals(result['connect'], True)
        '''

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarDerezTest))
    return suite

