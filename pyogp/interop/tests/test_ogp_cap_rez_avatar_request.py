"""
@file test_cap_rez_avatar_request.py
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
from pyogp.lib.base.agent import Agent
from pyogp.lib.base.agentdomain import AgentDomain, EventQueue
from pyogp.lib.base.caps import Capability
from pyogp.lib.base.regiondomain import Region

# pyogp.interop
from helpers import logout

'''
Tests for the rez_avatar/request capability as run against simulators (acting as the agent domain)

write tests against the protocol as is defined at http://wiki.secondlife.com/wiki/OGP_Teleport_Draft_3#POST_Interface_2
'''

class RezAvatarRequestTests(unittest.TestCase):
    """ test posting to rez_avatar/request for a simulator, acting as the region domain """
    
    def setUp(self):

        self.config = ConfigParser.ConfigParser()
        self.config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.debug = self.config.get('testconfig', 'debug')
        
        self.test_data_config_name = 'test_rez_avatar_request'
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = self.config.get(self.test_setup_config_name, 'firstname')
        self.lastname = self.config.get(self.test_setup_config_name, 'lastname')
        self.password = self.config.get(self.test_setup_config_name, 'password')
        self.login_uri = self.config.get(self.test_setup_config_name, 'login_uri')        
        self.region_uri = self.config.get('test_interop_regions', 'start_region_uri') 
        
        self.test_region_uri = self.config.get('test_interop_regions', 'target_region_uri') 

        # <start>
        # we need to get agent_id, session_id, secure_session_if and circuit code from somewhere. let's get it from region1, then test against region2
        
        # first establish an AD connection and get seed_cap for mtg
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
        
        self.required_parameters = {
            'agent_id' : self.region.details['agent_id'],
            'circuit_code' : self.region.details['circuit_code'],
            'secure_session_id' :self.region.details['secure_session_id'],
            'session_id' : self.region.details['session_id'],
            'first_name' : self.firstname,
            'last_name' :self.lastname
        }
                
        # Optional parameters: { age_verified: bool , agent_access: bool , allow_redirect: bool , god_level: int , identified: bool , transacted: bool , limited_to_estate: int , sim_access: "PG"|"Mature" }
        self.full_parameters = self.required_parameters
        
        self.full_parameters['position'] = self.config.get('test_rez_avatar_request', 'position')
        self.full_parameters['age_verified'] = self.config.get('test_rez_avatar_request', 'age_verified_true')
        self.full_parameters['agent_access'] = self.config.get('test_rez_avatar_request', 'agent_access_true')
        self.full_parameters['allow_redirect'] = self.config.get('test_rez_avatar_request', 'allow_redirect_true')
        self.full_parameters['god_level'] = self.config.get('test_rez_avatar_request', 'god_level_0')
        self.full_parameters['identified'] = self.config.get('test_rez_avatar_request', 'identified_true')
        self.full_parameters['transacted'] = self.config.get('test_rez_avatar_request', 'transacted_true')
        self.full_parameters['limited_to_estate'] = self.config.get('test_rez_avatar_request', 'limited_to_estate_mainland')
        self.full_parameters['src_can_see_mainland'] = 'Y'
        self.full_parameters['src_estate_id'] = 1
        
        # but we can craft the url and manual test things, as we can just post to the sim the info without anoy other context
        self.capability = Capability('rez_avatar/request', caps['rez_avatar/request'])
        
    def tearDown(self):
        
        if self.agentdomain.connectedStatus: # need a flag in the lib for when an agent has logged in 
            logout(self.agentdomain)
            
    def postToCap(self, arguments):
    
        result = self.capability.POST(arguments)
            
        return result

    def check_response(self, result):
        """ check for the eistence of the correct parameters in the cap response """
        
        self.assertNotEquals(result, None, 'post to cap returned nothing')
    
    #############
        # Success response: { connect: "True", rez_avatar/rez: url , region_seed_capability: url }

    
    def check_failure_response(self, result):
        """ tests the failure response for the proper content """
        

        self.assertEquals(result['connect'], False)

###################################
#           Test Cases            #
###################################
    # Tests to write include (among many others):
    #    post to the cap without having grabbed an agent domain seed cap
    #    additional parameters
    #    bad inputs

    def test_rez_avatar_request_required(self):
        """ Agent is allowed to connect """
        
        result = self.postToCap(self.required_parameters)
        
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')

    def test_cap_rez_avatar_request_success_keys(self):
        """ test that a success response contains no additional keys """
        
        result = self.postToCap(self.full_parameters)
        
        self.check_response(result)
        
        valid_keys = ['connect', 'rez_avatar/rez', 'region_seed_capability', 'sim_host', 'sim_port', 'sim_ip', 'region_id', 'region_x', 'region_y', 'sim_access']
        # sim_ip is currently coming back ~e 9/15/08
        fail = 0 
        extra_keys = ''
        missing_keys = ''
        
        for key in result:
            try:
                valid_keys.index(key) # if the key is in our valid list, sweet
            except:
                fail_extra = 1
                extra_keys = extra_keys + ' ' + key

        for key in valid_keys:
            try:
                result.index(key) # if the key is in our valid list, sweet
            except:
                fail_missing = 1
                missing_keys = missing_keys + ' ' + key
       
        self.assertEquals(fail_extra, 0, 'response has additional keys: ' + extra_keys)
        self.assertEquals(fail_missing, 0, 'response is missing keys: ' + missing_keys)     

    def test_rez_avatar_request_full(self):
        """ Agent is allowed to connect """
        
        result = self.postToCap(self.full_parameters)
        
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')

    def test_rez_avatar_request_seed_cap(self):
        """ Agent is allowed to connect """
        
        result = self.postToCap(self.full_parameters)
        
        self.check_response(result)
        self.assert_(result.has_key('region_seed_capability')), 'response is missing seed_capability attribute'
        
    def test_rez_avatar_request_fail_connect(self):
        """ posting to rez_avatar/request with no args, parse for failure response """
        
        result = self.postToCap({})
        
        self.check_response(result)
        self.assertEquals(result['connect'], False)
    
    def test_rez_avatar_request_fail_connect(self):
        """ posting to rez_avatar/request with no args, parse for failure response """
        
        result = self.postToCap({})
        
        self.check_response(result)
        self.assertEquals(result['message'], 'You are not allowed into the destination.', 'improper failure message')    

    
    def test_rez_avatar_request_failure_message(self):
        """ check that the message attribute is properly populated in a failure response """

        result = self.postToCap({})
        
        self.check_response(result)               
        self.assertNotEquals(result['message'], None, 'no message text in failure response')

    def test_rez_avatar_request_missing_agent_id(self):
        """ checks for proper response when agent_id is missing """
        
        del self.required_parameters['agent_id']
        result = self.postToCap(self.required_parameters)
                
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is not True')
        self.assertEquals(result['message'], 'No valid agent id.', 'Invalid message in response')

    def test_rez_avatar_request_invalid_agent_id(self):
        """ checks for proper response when agent_id is invalid """
        
        self.required_parameters['agent_id'] = '00000000-0000-0000-0000-00000000000000'
        result = self.postToCap(self.required_parameters)
               
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is not False')

    def test_rez_avatar_request_missing_first_name(self):
        """ checks for proper response when first_name is missing """
        
        del self.required_parameters['first_name']
        result = self.postToCap(self.required_parameters)
                
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is not False')

    def test_rez_avatar_request_invalid_first_name(self):
        """ checks for proper response when first_name is invalid """
        
        self.required_parameters['first_name'] = None

        result = self.postToCap(self.required_parameters)
               
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')
        
    def test_rez_avatar_request_missing_last_name(self):
        """ checks for proper response when last_name is missing """
        
        del self.required_parameters['last_name']
        result = self.postToCap(self.required_parameters)
               
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is not False')

    def test_rez_avatar_request_invalid_last_name(self):
        """ checks for proper response when last_name is invalid """
        
        self.required_parameters['last_name'] = None

        result = self.postToCap(self.required_parameters)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')

    def test_rez_avatar_request_age_verified_T(self):
        """ checks for proper response when age_verified is True """
        
        self.full_parameters['age_verified'] = 'Y'
                        
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is True')

    def test_rez_avatar_request_allow_redirect_T(self):
        """ checks for proper response when age_verified is True """
        
        self.full_parameters['age_verified'] = True

        result = self.postToCap(self.full_parameters)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')        

    def test_rez_avatar_request_agent_access_T(self):
        """ checks for proper response when agent_access is True """
        
        self.full_parameters['agent_access'] = True

        result = self.postToCap(self.full_parameters)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')  

    def test_rez_avatar_request_god_level(self):
        """ checks for proper response when agent_access is 0 """
        
        self.full_parameters['god_level'] = self.config.get(self.test_data_config_name, 'god_level_0')

        result = self.postToCap(self.full_parameters)
               
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')  

    def test_rez_avatar_request_identified_T(self):
        """ checks for proper response when identified is True """
        
        self.full_parameters['identified'] = self.config.get(self.test_data_config_name, 'identified_true')

        result = self.postToCap(self.full_parameters)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True') 

    def test_rez_avatar_request_transacted_T(self):
        """ checks for proper response when transacted is True """
        
        self.full_parameters['transacted'] = self.config.get(self.test_data_config_name, 'transacted_true')

        result = self.postToCap(self.full_parameters)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True') 

    def test_rez_avatar_request_limited_to_estate_9999(self):
        """ checks for proper response when limited_to_estate is limited to nonexistant estate """
        
        self.full_parameters['limited_to_estate'] = 99999999999

        result = self.postToCap(self.full_parameters)
               
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is True')   

    def test_rez_avatar_request_sim_access_Mature(self):
        """ checks for proper response when sim_access is set to PG """
        
        self.full_parameters['sim_access'] = self.config.get(self.test_data_config_name, 'sim_access_Mature')

        result = self.postToCap(self.full_parameters)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True') 

    def test_rez_avatar_request_sim_access_PG(self):
        """ checks for proper response when sim_access is set to Mature """
        
        self.full_parameters['sim_access'] = self.config.get(self.test_data_config_name, 'sim_access_Mature')

        result = self.postToCap(self.full_parameters)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')                                                              
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarRequestTests))
    return suite

if __name__ == '__main__':
    unittest.main()
