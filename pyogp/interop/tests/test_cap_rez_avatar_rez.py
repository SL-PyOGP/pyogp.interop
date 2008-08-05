#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

'''
write tests against the protocol as is defined at 
http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Rez_Avatar_.28Resource_Class.29
'''

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
        
        # we can't request this cap, but we can craft it ourselves        
        self.rez_avatar_url  = self.region_uri + '/agent/' + self.agent_id + '/rez_avatar/rez'
        
        # Required parameters: { circuit_code: int, position: [x real ,y real, z real, ], secure_session_id: uuid , session_id: uuid , avatar_data: TBD }
        self.required_parameters = { 
           'circuit_code' : config.get('test_rez_avatar_rez_setup', 'circuit_code'),
           'position' : self.position,
           'secure_session_id' : config.get('test_rez_avatar_rez_setup', 'secure_session_id'),
           'session_id' : config.get('test_rez_avatar_rez_setup', 'session_id')
           }
           
        self.full_parameters = {
           'circuit_code' : config.get('test_rez_avatar_rez_setup', 'circuit_code'),
           'position' : self.position,
           'secure_session_id' : config.get('test_rez_avatar_rez_setup', 'secure_session_id'),
           'session_id' : config.get('test_rez_avatar_rez_setup', 'session_id')#,
           #'avatar_data' : ''
           }
       
        self.capability = Capability('rez_avatar/rez', self.rez_avatar_url)

    def tearDown(self):
        
        # we don't login, don't need to logout :)
        pass
    
    def postToCap(self, arguments):
        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            #print 'Exception: ' + e.message + ' ' + str(e.args)
            result = str(e.args)
        return result

    
    def check_successful_response(self, result):
        """ check for the eistence of the correct parameters in the cap response """

        # Successful response: { connect: "True" look_at: [x real ,y real, z real, ] , position: [x real ,y real, z real, ], rez_avatar/derez: cap }
        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position') and
                     result.has_key('rez_avatar/derez'))
                     
    def check_failure_response(self, result):
        """ check for the eistence of the correct parameters in the cap response """

        # Failure response: { connect: False, redirect: False, resethome: False, message: string } 
        self.assert_(result.has_key('connect') and
                     result.has_key('redirect') and
                     result.has_key('resethome') and
                     result.has_key('message'))

    def test_rez_avatar_rez_required(self):
        """ agent is allowed to rez when passing the required params """

        result = self.postToCap(self.required_parameters)

        self.check_successful_response(result)
        self.assertEquals(result['connect'], True)

    def test_rez_avatar_rez_full(self):
        """ agent is allowed to rez when passing the required params """

        result = self.postToCap(self.full_parameters)

        self.check_successful_response(result)
        self.assertEquals(result['connect'], True)

    def test_rez_avatar_rez_position(self):
        """ verify position values are within range """

        result = self.postToCap(self.required_parameters)

        self.check_successful_response(result)
        
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)
                     
    def test_rez_avatar_rez_look_at(self):
        """ verify look_at values are within range """

        result = self.postToCap(self.required_parameters)

        self.check_successful_response(result)
        
        self.assert_(result['look_at'][0] < 256 and
                     result['look_at'][1] < 256 and 
                     result['look_at'][2] < 256)

    def test_rez_avatar_rez_nocontent(self):
        """ verify look_at values are within range """

           
        empty_parameters = {
           'circuit_code' : '',
           'position' : '',
           'secure_session_id' : '',
           'session_id' : ''
           }
           
        result = self.postToCap(empty_parameters)

        self.check_failure_response(result)
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarRezTests))
    return suite

