#!/usr/bin/python

import unittest, time
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

from helpers import Agent

'''
# in progress, tests are skipped

Tests for the rez_avatar/derez capability as run against simulators (acting as the agent domain)

write tests against the protocol as is defined at http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Derez_Avatar_.28Resource_Class.29
'''

class RezAvatarDerezTest(unittest.TestCase):
    """ test posting to rez_avatar/derez for a simulator, acting as the region domain """

    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        test_setup_config_name = 'test_rez_avatar_derez_setup'
        
        self.firstname = config.get('test_interop_account', 'firstname')
        self.lastname = config.get('test_interop_account', 'lastname')
        self.password = config.get('test_interop_account', 'password')
        self.login_uri = config.get('test_interop_account', 'login_uri')
        self.agent_id = config.get('test_interop_account', 'agent_id') # this can come from self.client.id once agent/info is working
        
        self.source_region_uri = config.get('test_interop_regions', 'start_region_uri')        
        self.target_region_uri = config.get('test_interop_regions', 'target_region_uri')
        
        self.position = config.get('test_rez_avatar_derez', 'position') 

        # agent has to rez on the sim before the derez cap can be called
        self.client = Agent()
        self.client.login(self.firstname, self.lastname, self.password, self.login_uri, self.region_uri)
        
        # we can't request these caps as a client, but we can craft them ourselves
        self.rez_avatar_url = self.target_region_uri + '/agent/' + self.agent_id + '/rez_avatar/rez'
        self.derez_avatar_url = self.source_region_uri + '/agent/' + self.agent_id + '/rez_avatar/derez'
        
        # Required parameters: { rez-avatar/rez: url string, position: [x real, y real, z real, ] }              
        self.required_parameters = {
            'rez_avatar' : self.rez_avatar_url,
            'position' : self.position
            }
        
        self.capability = Capability('rez_avatar/derez', self.derez_avatar_url)              

        if self.debug: print 'rez_avatar/derez url = ' + self.derez_avatar_url
        
    def tearDown(self):
        pass
        # uncomment once this test can be used
        # self.client.logout()


    def postToCap(self, arguments):

        if self.debug: print 'posting to cap = ' + str(arguments)
      
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

        print 'Until we can maintain presence, we have nothing to do here'
        '''
        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_successful_response(result)
        self.assertEquals(result['connect'], True)
        '''

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarDerezTest))
    return suite

