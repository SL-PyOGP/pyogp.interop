#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

from helpers import Agent

'''
Tests for the rez_avatar/place capability as run against simulators (acting as the client)

write tests against the protocol as is defined at http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Place_Avatar_.28Resource_Class.29
'''

class RezAvatarPlaceTests(unittest.TestCase):
    """ test posting to rez_avatar/place for a simulator, acting as the region domain """
    
    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.firstname = config.get('test_interop_account', 'firstname')
        self.lastname = config.get('test_interop_account', 'lastname')
        self.password = config.get('test_interop_account', 'password')
        self.login_uri = config.get('test_interop_account', 'login_uri')
        self.agent_id = config.get('test_interop_account', 'agent_id') # this can come from self.client.id once agent/info is working
        
        self.region_uri = config.get('test_interop_regions', 'linden_start_region_uri') 
           
        self.position = config.get('test_rez_avatar_place', 'position')
        
        # required_parameters: { region_url: url string, position: [x real, y real, z real, ] }
        self.required_parameters = {
            'region_url' : self.region_uri,
            'position' : self.position
            }

        # to get place, we need to authenticate and retrieve the place_avatar cap from the AD
        self.client = Agent()
        self.client.authenticate(self.firstname, self.lastname, self.password, self.login_uri)
        self.caps = self.client.agentdomain.seed_cap.get(['rez_avatar/place'])
        
        # initialize the cap object for use in postToCap
        self.capability = Capability('rez_avatar/place', self.caps['rez_avatar/place'].public_url)

        if self.debug: print 'rez_avatar/place url = ' + self.caps['rez_avatar/place'].public_url
              
    def tearDown(self):
        
        self.client.logout()
        
        '''
        if self.client.agentdomain != None:
            self.client.logout()
        '''
        
    def postToCap(self, arguments):
        
        if self.debug: print 'posting to cap = ' + str(arguments)

        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            #print 'Exception: ' + e.message + ' ' + str(e.args)
            result = str(e.args)

        return result

    
    def check_response(self, result):
        """ check for the existence of the correct parameters in the cap response """

        # Success response: { connect: bool , seed_capability: url string , look_at: [x real, y real, z real, ] , position: [x real, y real, z real, ]}
        
        self.assertNotEquals(result, None, 'empty response')

    def check_failure_response(self, result):
        """ tests the failure response for the proper content """
        
        # docs are missing this detail
        
        print result 

###################################
#           Test Cases            #
###################################
# these these tests act as a client, they run more slowly. include as much validation as possible into one test function

                     
    def test_rez_avatar_place_required(self):
        """ agent is allowed to rez """

        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        self.assertEquals(result['connect'], True)
 
        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position') and
                     result.has_key('seed_capability'))
        
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)
        
        self.assert_(result['look_at'][0] < 256 and
                     result['look_at'][1] < 256 and 
                     result['look_at'][2] < 256)   
   
    def test_rez_avatar_place_nocontent(self):
        """ agent is allowed to rez """

        result = self.postToCap({})

        if self.debug: print 'result  = ' + str(result)
        
        # print result
        # the library is trapping the 400, perhaps it should be allowed to filter here for testing? 
        self.check_response(result)
        #self.assertRaises(HTTPError, self.postToCap(self.required_parameters))

    def test_rez_avatar_place_invalid_region_uri(self):
        """ agent is allowed to rez """

        self.required_parameters['region_url'] = 'http://imnotreal.net'
        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        # the library is trapping the 400, perhaps it should be allowed to filter here for testing? 
        self.check_response(result)
        #self.assertRaises(HTTPError, self.postToCap(self.required_parameters))

    def test_cap_rez_avatar_place_success_keys(self):
        """ test that a success response contains no additional keys """
        
        result = self.postToCap(self.required_parameters)
        
        self.check_response(result)

        if self.debug: print 'result  = ' + str(result)
                
        valid_keys = ['connect', 'look_at', 'position', 'seed_capability']
        fail = 0 
        extra_keys = ''
        
        for key in result:
            try:
                valid_keys.index(key) # if the key is in our valid list, sweet
            except:
                fail = 1
                extra_keys = extra_keys + ' ' + key
        
        self.assertEquals(fail, 0, 'response has additional keys: ' + extra_keys)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarPlaceTests))
    return suite

