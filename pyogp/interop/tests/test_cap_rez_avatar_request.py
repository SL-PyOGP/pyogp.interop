#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

from helpers import Agent

'''
Tests for the rez_avatar/request capability as run against simulators (acting as the agent domain)

write tests against the protocol as is defined at http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Request_Rez_Avatar_.28Resource_Class.29
'''

class RezAvatarRequestTests(unittest.TestCase):
    """ test posting to rez_avatar/request for a simulator, acting as the region domain """
    
    def setUp(self):
        init()

        self.config = ConfigParser.ConfigParser()
        self.config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.debug = self.config.get('testconfig', 'debug')
        
        self.test_setup_config_name = 'test_rez_avatar_request'
        
        # grab the testdata from testconfig.cfg
        self.firstname = self.config.get('test_interop_account', 'firstname')
        self.lastname = self.config.get('test_interop_account', 'lastname')
        self.password = self.config.get('test_interop_account', 'password')
        self.login_uri = self.config.get('test_interop_account', 'login_uri')
        self.agent_id = self.config.get('test_interop_account', 'agent_id') # this can come from self.client.id once agent/info is working
        
        self.region_uri = self.config.get('test_interop_regions', 'linden_start_region_uri') 
        
        # we can't request this cap, but we can craft it ourselves
        self.rez_avatar_request_url = self.region_uri + '/agent/' + self.agent_id + '/rez_avatar/request'
        
        # Required parameters: { agent_id: uuid, first_name: string , last_name: string }       
        
        self.required_parameters = {
            'agent_id' : self.agent_id,
            'first_name' : self.firstname,
            'last_name' : self.lastname
        }
                
        # Optional parameters: { age_verified: bool , agent_access: bool , allow_redirect: bool , god_level: int , identified: bool , transacted: bool , limited_to_estate: int , sim_access: "PG"|"Mature" }
        self.full_parameters = {
            'agent_id' : self.agent_id,
            'first_name' : self.firstname,
            'last_name' : self.lastname,
            'age_verified' : self.config.get(self.test_setup_config_name, 'age_verified_true'),
            'allow_redirect' : self.config.get(self.test_setup_config_name, 'allow_redirect_true'),
            'agent_access' : self.config.get(self.test_setup_config_name, 'agent_access_true'),
            'god_level' :  self.config.get(self.test_setup_config_name, 'god_level_0'),
            'identified' :  self.config.get(self.test_setup_config_name, 'identified_true'),
            'transacted' : self.config.get(self.test_setup_config_name, 'transacted_true'),
            'limited_to_estate' : self.config.get(self.test_setup_config_name, 'limited_to_estate_mainland'),
            'sim_access' : self.config.get(self.test_setup_config_name, 'sim_access_Mature'),
            }

        # were we to auth first...
        #self.client = Agent()
        #self.client.authenticate(self.firstname, self.lastname, self.password, self.login_uri)
        
        # but we can craft the url and manual test things, as we can just post to the sim the info without anoy other context
        self.capability = Capability('rez_avatar/request', self.rez_avatar_request_url)
        
        if self.debug: print 'rez_avatar/request url = ' + self.rez_avatar_request_url

    def tearDown(self):
        
        # we don't login, don't need to logout
        pass

    def postToCap(self, arguments):
    
        if self.debug: print 'posting to cap = ' + str(arguments)
        
        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            print 'Exception: ' + e.message + ' ' + str(e.args)
            return
        
        return result

    def check_response(self, result):
        """ check for the eistence of the correct parameters in the cap response """
        
        self.assertNotEquals(result, None, 'post to cap returned nothing')
    
    #############
        # Success response: { connect: "True", rez_avatar/rez: url , seed_capability: url }

    
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
        
        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')

    def test_cap_rez_avatar_request_success_keys(self):
        """ test that a success response contains no additional keys """
        
        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        
        valid_keys = ['connect', 'rez_avatar/rez', 'rez_avatar/rez']
        fail = 0 
        extra_keys = ''
        
        for key in result:
            try:
                valid_keys.index(key) # if the key is in our valid list, sweet
            except:
                fail = 1
                extra_keys = extra_keys + ' ' + key
        
        self.assertEquals(fail, 0, 'response has additional keys: ' + extra_keys)

    def test_rez_avatar_request_full(self):
        """ Agent is allowed to connect """
        
        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')

    def test_rez_avatar_request_seed_cap(self):
        """ Agent is allowed to connect """
        
        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        self.assert_(result.has_key('seed_capability')), 'response is missing seed_capability attribute'
        
    def test_rez_avatar_request_fail_connect(self):
        """ posting to rez_avatar/request with no args, parse for failure response """
        
        result = self.postToCap({})
        
        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        self.assertEquals(result['connect'], False)
    
    def test_rez_avatar_request_fail_connect(self):
        """ posting to rez_avatar/request with no args, parse for failure response """
        
        result = self.postToCap({})
        
        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        self.assertEquals(result['message'], 'You are not allowed into the destination.', 'improper failure message')    

    
    def test_rez_avatar_request_failure_message(self):
        """ check that the message attribute is properly populated in a failure response """

        result = self.postToCap({})
        
        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)               
        self.assertNotEquals(result['message'], None, 'no message text in failure response')

    def test_rez_avatar_request_missing_agent_id(self):
        """ checks for proper response when agent_id is missing """
        
        del self.required_parameters['agent_id']
        result = self.postToCap(self.required_parameters)
        
        if self.debug: print 'result  = ' + str(result)
                
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is not True')

    def test_rez_avatar_request_invalid_agent_id(self):
        """ checks for proper response when agent_id is invalid """
        
        self.required_parameters['agent_id'] = '00000000-0000-0000-0000-00000000000000'
        result = self.postToCap(self.required_parameters)
        
        if self.debug: print 'result  = ' + str(result)
               
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is not True')

    def test_rez_avatar_request_missing_first_name(self):
        """ checks for proper response when first_name is missing """
        
        del self.required_parameters['first_name']
        result = self.postToCap(self.required_parameters)
        
        if self.debug: print 'result  = ' + str(result)
                
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is not True')

    def test_rez_avatar_request_invalid_first_name(self):
        """ checks for proper response when first_name is invalid """
        
        self.required_parameters['first_name'] = None

        result = self.postToCap(self.required_parameters)
        
        if self.debug: print 'result  = ' + str(result)
               
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is not True')
        
    def test_rez_avatar_request_missing_last_name(self):
        """ checks for proper response when last_name is missing """
        
        del self.required_parameters['last_name']
        result = self.postToCap(self.required_parameters)
        
        if self.debug: print 'result  = ' + str(result)
               
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is not True')

    def test_rez_avatar_request_invalid_last_name(self):
        """ checks for proper response when last_name is invalid """
        
        self.required_parameters['last_name'] = None

        result = self.postToCap(self.required_parameters)
        
        if self.debug: print 'result  = ' + str(result)
                
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is not True')

    def test_rez_avatar_request_age_verified_T(self):
        """ checks for proper response when age_verified is True """
        
        self.full_parameters['age_verified'] = 'Y'

        result = self.postToCap(self.full_parameters)

        if self.debug: print 'result  = ' + str(result)
                        
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is True')

    def test_rez_avatar_request_allow_redirect_T(self):
        """ checks for proper response when age_verified is True """
        
        self.full_parameters['age_verified'] = True

        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')        

    def test_rez_avatar_request_agent_access_T(self):
        """ checks for proper response when agent_access is True """
        
        self.full_parameters['agent_access'] = True

        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')  

    def test_rez_avatar_request_god_level(self):
        """ checks for proper response when agent_access is 0 """
        
        self.full_parameters['god_level'] = self.config.get(self.test_setup_config_name, 'god_level_0')

        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
               
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')  

    def test_rez_avatar_request_identified_T(self):
        """ checks for proper response when identified is True """
        
        self.full_parameters['identified'] = self.config.get(self.test_setup_config_name, 'identified_true')

        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True') 

    def test_rez_avatar_request_transacted_T(self):
        """ checks for proper response when transacted is True """
        
        self.full_parameters['transacted'] = self.config.get(self.test_setup_config_name, 'transacted_true')

        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True') 

    def test_rez_avatar_request_limited_to_estate_9999(self):
        """ checks for proper response when limited_to_estate is limited to nonexistant estate """
        
        self.full_parameters['limited_to_estate'] = 99999999999

        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
               
        self.check_response(result)
        self.assertEquals(result['connect'], False, 'connect attribute is True')   

    def test_rez_avatar_request_sim_access_PG(self):
        """ checks for proper response when sim_access is set to PG """
        
        self.full_parameters['sim_access'] = self.config.get(self.test_setup_config_name, 'sim_access_PG')

        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True') 

    def test_rez_avatar_request_sim_access_PG(self):
        """ checks for proper response when sim_access is set to Mature """
        
        self.full_parameters['sim_access'] = self.config.get(self.test_setup_config_name, 'sim_access_Mature')

        result = self.postToCap(self.full_parameters)
        
        if self.debug: print 'result  = ' + str(result)
                
        self.check_response(result)
        self.assertEquals(result['connect'], True, 'connect attribute is not True')                                                              
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarRequestTests))
    return suite

if __name__ == '__main__':
    unittest.main()
