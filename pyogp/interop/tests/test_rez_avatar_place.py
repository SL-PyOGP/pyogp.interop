#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

from helpers import Agent

class RezAvatarPlaceTests(unittest.TestCase):

    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.firstname = config.get('test_rez_avatar_place_setup', 'firstname')
        self.lastname = config.get('test_rez_avatar_place_setup', 'lastname')
        self.password = config.get('test_rez_avatar_place_setup', 'password')
        self.login_uri = config.get('test_rez_avatar_place_setup', 'login_uri')
        self.region_uri = config.get('test_rez_avatar_place_setup', 'region_uri')
        self.position = config.get('test_rez_avatar_place_setup', 'position')
        
        self.default_arguments = {
            'region_url' : self.region_uri,
            'position' : self.position
            }

        # to get place, we need to authenticate and retrieve the place_avatar cap from the AD
        client = Agent()
        client.authenticate(self.firstname, self.lastname, self.password, self.login_uri)
        self.caps = client.agentdomain.seed_cap.get(['rez_avatar/place'])
        
        # initialize the cap object for use in postToCap
        self.capability = Capability('rez_avatar/place', self.caps['rez_avatar/place'].public_url)
       
    def tearDown(self):
        pass
    
    def postToCap(self, arguments):
        print arguments
        try:
            result = self.capability.POST(arguments)
            print result
        except Exception, e:
            print 'Exception: ' + e.message + ' ' + str(e.args)
            return

        return result

    
    def check_response_base(self, result):
        """ check for the eistence of the correct parameters in the cap response """

        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position'))

    '''
    todo: validate this
    rez_avatar/place should return
    
    Response

    {
      'seed_capability': uri string
      'look_at' : [f32, f32, f32]
      'sim_ip': ip string
      'sim_port': int
      'region_x': int
      'region_y': int
      'region_id' : uuid
      'sim_access' : <PG/Mature>
      'connect': bool
      'position': [f32, f32, f32]
    // The above are the same as response to rez_avatar
    // The following are only returned on login, not over teleport
       'session_id':<uuid>
       'secure_session_id':<uuid>
       'circuit_code':<int>
    }
    '''

    def test_rez_avatar_place_connect(self):
        """ agent is allowed to rez """

        result = self.postToCap(self.default_arguments)

        self.check_response_base(result)
        self.assertEquals(result['connect'], True)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarPlaceTests))
    return suite

