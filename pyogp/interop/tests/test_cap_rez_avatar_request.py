#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

from helpers import Agent

'''
write tests against the protocol as is defined at http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Request_Rez_Avatar_.28Resource_Class.29
'''

class RezAvatarRequestTests(unittest.TestCase):
    """ test posting to rez_avatar/request for a simulator, acting as the region domain """
    
    def setUp(self):
        init()

        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        test_setup_config_name = 'test_rez_avatar_request_setup'
        
        # grab the testdata from testconfig.cfg
        self.agent_id = config.get(test_setup_config_name, 'agent_id')
        self.region_uri = config.get(test_setup_config_name, 'region_uri')
        self.firstname = config.get(test_setup_config_name, 'firstname')
        self.lastname = config.get(test_setup_config_name, 'lastname')
        self.password = config.get(test_setup_config_name, 'password')
        self.login_uri = config.get(test_setup_config_name, 'login_uri')
        
        # we can't request this cap, but we can craft it ourselves
        self.rez_request_avatar_url = self.region_uri + '/agent/' + self.agent_id + '/rez_avatar/request'
        
        # Required parameters: { agent_id: uuid, first_name: string , last_name: string }       
        
        self.required_parameters = {
            'agent_id' : self.agent_id,
            'first_name' : config.get(test_setup_config_name, 'first_name'),
            'last_name' : config.get(test_setup_config_name, 'last_name'),
        }
                
        # Optional parameters: { age_verified: bool , agent_access: bool , allow_redirect: bool , god_level: int , identified: bool , transacted: bool , limited_to_estate: int , sim_access: "PG"|"Mature" }
        self.full_parameters = {
            'agent_id' : self.agent_id,
            'first_name' : config.get(test_setup_config_name, 'first_name'),
            'last_name' : config.get(test_setup_config_name, 'last_name'),
            'age_verified' : config.get(test_setup_config_name, 'age_verified'),
            #'allow_redirect' : config.get(test_setup_config_name, 'allow_redirect'),
            'agent_access' : config.get(test_setup_config_name, 'agent_access'),
            'god_level' :  config.get(test_setup_config_name, 'god_level'),
            'identified' :  config.get(test_setup_config_name, 'identified'),
            'transacted' : config.get(test_setup_config_name, 'transacted'),
            'limited_to_estate' : config.get(test_setup_config_name, 'limited_to_estate'),
            'sim_access' : config.get(test_setup_config_name, 'sim_access'),
            }

        # to get re_avatar/request, we need to authenticate and retrieve the place_avatar cap from the AD
        #self.client = Agent()
        #self.client.authenticate(self.firstname, self.lastname, self.password, self.login_uri)
        

        self.capability = Capability('rez_avatar/request', self.rez_request_avatar_url)

    def tearDown(self):
        
        # we don't login, don't need to logout
        pass

    def postToCap(self, arguments):
        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            print 'Exception: ' + e.message + ' ' + str(e.args)
            return
        
        return result

    def check_successful_response(self, result):
        """ a successful response has certain components """
        
        # Success response: { connect: "True", rez_avatar/rez: url , seed_capability: url }
        self.assert_(result.has_key('connect') and
                     result.has_key('rez_avatar/rez') and
                     result.has_key('seed_capability'))
    
    def check_failure_response(self, result):
        """ tests the failure response for the proper content """
        
        # { connect: False, message: string }
        
        self.assert_(result.has_key('connect') and
                     result.has_key('message'))
        self.assertEquals(result['connect'], False)

###################################
#           Test Cases            #
###################################
    # Tests to write include (among many others):
    #    post to the cap without having grabbed an agent domain seed cap
    #    additional parameters
    #    mismatched inputs

    def test_rez_avatar_request_required(self):
        """ Agent is allowed to connect """
        
        result = self.postToCap(self.required_parameters)
        
        self.check_successful_response(result)
        self.assertEquals(result['connect'], True)

    def test_rez_avatar_request_full(self):
        """ Agent is allowed to connect """
        
        result = self.postToCap(self.full_parameters)
        
        self.check_successful_response(result)
        self.assertEquals(result['connect'], True)
        
    def test_rez_avatar_request_nocontent(self):
        """ posting to rez_avatar/request with no args, parse for failure response """
        
        result = self.postToCap({})
        
        self.check_failure_response(result)
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarRequestTests))
    return suite

if __name__ == '__main__':
    unittest.main()
