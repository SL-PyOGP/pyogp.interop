#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

from helpers import Agent

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
                
        self.default_arguments={
            'agent_id' : self.agent_id,
            'first_name' : config.get(test_setup_config_name, 'first_name'),
            'last_name' : config.get(test_setup_config_name, 'last_name'),
            'age_verified' : config.get(test_setup_config_name, 'age_verified'),
            'agent_access' : config.get(test_setup_config_name, 'agent_access'),
            'god_level' :  config.get(test_setup_config_name, 'god_level'),
            'identified' :  config.get(test_setup_config_name, 'identified'),
            'transacted' : config.get(test_setup_config_name, 'transacted'),
            'limited_to_estate' : config.get(test_setup_config_name, 'limited_to_estate'),
            'sim_access' : config.get(test_setup_config_name, 'sim_access'),
            }

        # to get re_avatar/request, we need to authenticate and retrieve the place_avatar cap from the AD
        self.client = Agent()
        self.client.authenticate(self.firstname, self.lastname, self.password, self.login_uri)
        self.caps = self.client.agentdomain.seed_cap.get(['rez_avatar/request'])

        self.capability = Capability('rez_avatar/request', self.caps['rez_avatar/request'].public_url)

    def tearDown(self):
        pass

    def postToCap(self, arguments):
        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            print 'Exception: ' + e.message + ' ' + str(e.args)
            return
        
        return result

    def check_response_base(self, result):
        
        # check for existence of fields
        self.assert_(result.has_key('connect') and
                     result.has_key('rez_avatar/rez') and
                     result.has_key('sim_ip') and
                     result.has_key('sim_port') and
                     result.has_key('region_x') and
                     result.has_key('region_y') and
                     result.has_key('region_id') and
                     result.has_key('sim_access') and
                     result.has_key('seed_capability'))
    
    def check_failure_response(self, result):
        """ tests the failure response for the proper content """
        
        # { connect: False, message: string }
        
        self.assert_(result.has_key('connect') and
                     result.has_key('message'))
        self.assertEquals(result['connect'], False)

    '''
    write tests against the protocol as is defined at http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Request_Rez_Avatar_.28Resource_Class.29
    '''


    def test_rez_avatar_request_connect(self):
        """ Agent is allowed to connect """
        
        result = self.postToCap(self.default_arguments)
        
        self.check_response_base(result)
        self.assertEquals(result['connect'], True)

        
    def test_rez_avatar_request_nocontent(self):
        """ posting to rez_avatar/request with no args, parse for failure response """
        
        result = self.postToCap({})
        
        self.check_failure_response(result)
        
        print result
    
    # Tests to write include (among many others):
    #    post to the cap without having grabbed an agent domain seed cap
    #    additional parameters
    #    

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarRequestTests))
    return suite

if __name__ == '__main__':
    unittest.main()
