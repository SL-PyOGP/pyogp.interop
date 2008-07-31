#!/usr/bin/python

import unittest, time
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability


class RezAvatarDerezTest(unittest.TestCase):

    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))

        # grab the testdata from testconfig.cfg
        self.agent_id = config.get('test_rez_avatar_derez_setup', 'agent_id')
        self.source_region_uri = config.get('test_rez_avatar_derez_setup', 'source_region_uri')
        self.target_region_uri = config.get('test_rez_avatar_derez_setup', 'target_region_uri')
        self.rez_avatar_url = self.target_region_uri + '/agent/' + self.agent_id + '/rez_avatar/rez'
        self.derez_avatar_url = self.source_region_uri + '/agent/' + self.agent_id + '/rez_avatar/derez'
        self.position = [config.getint('test_rez_avatar_derez_setup', 'position_x'), config.getint('test_rez_avatar_derez_setup', 'position_y'), config.getint('test_rez_avatar_derez_setup', 'position_z')]
                
        self.default_arguments = {
        	'rez_avatar' : self.rez_avatar_url,
        	'position' : self.position
        	}
        		
        self.capability = Capability('rez_avatar/derez', self.derez_avatar_url)

    def tearDown(self):
        pass


    def postToCap(self, arguments):
        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            print 'Exception: ' + e.message + ' ' + str(e.args)
            return

        return result


    def check_response_base(self, results):
        """ check the the existence of the correct parameters in the cap response """
        
        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position'))

        self.assertEquals(result['connect'], True)
        self.assert_(result['position'][0] < 256)
        self.assert_(result['position'][1] < 256)
        self.assert_(result['position'][2] < 256)

    def test_rez_avatar_derez_connect(self):
        """ agent is allowed to derez """

        result = self.postToCap(self.default_arguments)

        self.check_response_base(result)
        self.assertEquals(result['connect'], True)

    def test_rez_avatar_derez_position(self):
        """ verify position values are within range """

        result = self.postToCap(self.default_arguments)

        self.check_response_base(result)

        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and
                     result['position'][2] < 256)

    def test_rez_avatar_derez_look_at(self):
        """ verify look_at values are within range """

        result = self.postToCap(self.default_arguments)

        self.check_response_base(result)
        
        self.assert_(result['look_at'][0] < 256 and
                     result['look_at'][1] < 256 and 
                     result['look_at'][2] < 256)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarDerezTest))
    return suite

