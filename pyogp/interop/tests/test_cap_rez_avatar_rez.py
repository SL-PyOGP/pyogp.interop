#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

class RezAvatarRezTests(unittest.TestCase):
    """ test posting to rez_avatar/rez for a simulator, acting as the region domain """
    
    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        # grab the testdata from testconfig.cfg
        self.agent_id = config.get('test_rez_avatar_rez_setup', 'agent_id')
        self.region_uri = config.get('test_rez_avatar_rez_setup', 'region_uri')
        self.position = config.get('test_rez_avatar_rez_setup', 'position')        
        self.rez_avatar_url  = self.region_uri + '/agent/' + self.agent_id + '/rez_avatar/rez'
         
        self.default_arguments = { 
           'circuit_code' : config.get('test_rez_avatar_rez_setup', 'circuit_code'),
           'god_override' : config.get('test_rez_avatar_rez_setup', 'god_override'),
           'position' : self.position,
           'secure_session_id' : config.get('test_rez_avatar_rez_setup', 'secure_session_id'),
           'session_id' : config.get('test_rez_avatar_rez_setup', 'session_id'),
           'inventory_host' : config.get('test_rez_avatar_rez_setup', 'inventory_host'), # not really here!
           'voice_password' : None,    
           # The following are only sent from simulator a -> simulator b via derez_avatar
           'attachment_data' : None, 
           'baked_texture_data' : None, 
           'texture_data' : None, 
           'animations' : None
            }
        
        self.capability = Capability('rez_avatar/rez', self.rez_avatar_url)

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
        """ check for the eistence of the correct parameters in the cap response """

        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position'))

    def test_rez_avatar_rez_connect(self):
        """ agent is allowed to rez """

        result = self.postToCap(self.default_arguments)

        self.check_response_base(result)
        self.assertEquals(result['connect'], True)

    def test_rez_avatar_rez_position(self):
        """ verify position values are within range """

        result = self.postToCap(self.default_arguments)

        self.check_response_base(result)
        
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)
                     
    def test_rez_avatar_rez_look_at(self):
        """ verify look_at values are within range """

        result = self.postToCap(self.default_arguments)

        self.check_response_base(result)
        
        self.assert_(result['look_at'][0] < 256 and
                     result['look_at'][1] < 256 and 
                     result['look_at'][2] < 256)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarRezTests))
    return suite

