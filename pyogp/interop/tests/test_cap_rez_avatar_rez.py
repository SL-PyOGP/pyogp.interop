#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

'''
Tests for the rez_avatar/rez capability as run against simulators (acting as the agent domain)

write tests against the protocol as is defined at 
http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Rez_Avatar_.28Resource_Class.29
'''

class RezAvatarRezTests(unittest.TestCase):
    """ test posting to rez_avatar/rez for a simulator, acting as the region domain """
    
    def setUp(self):
        init()
        
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.test_setup_config_name = 'test_rez_avatar_rez'
        
        # grab the testdata from testconfig.cfg
        self.agent_id = self.config.get(self.test_setup_config_name, 'agent_id')
        self.region_uri = self.config.get('test_interop_regions', 'linden_start_region_uri')
        self.position = self.config.get(self.test_setup_config_name, 'position')
        
        # we can't request this cap, but we can craft it ourselves        
        self.rez_avatar_url  = self.region_uri + '/agent/' + self.agent_id + '/rez_avatar/rez'
        
        # Required parameters: { circuit_code: int, position: [x real ,y real, z real, ], secure_session_id: uuid , session_id: uuid , avatar_data: TBD }
        # Note the TBD on avatar data
        self.required_parameters = { 
           'circuit_code' : self.config.get(self.test_setup_config_name, 'circuit_code'),
           'position' : self.position,
           'secure_session_id' : self.config.get(self.test_setup_config_name, 'secure_session_id'),
           'session_id' : self.config.get(self.test_setup_config_name, 'session_id')
           }
           
        self.full_parameters = {
           'circuit_code' : self.config.get(self.test_setup_config_name, 'circuit_code'),
           'position' : self.position,
           'secure_session_id' : self.config.get(self.test_setup_config_name, 'secure_session_id'),
           'session_id' : self.config.get(self.test_setup_config_name, 'session_id'),
           'avatar_data' : None
           }
       
       
        # Set state for the test
        #     The sim doesn't care about the agent domain per se for rez_avatar/rez
        #     We can work jsut with a rez_avatar_url and post params
        self.capability = Capability('rez_avatar/rez', self.rez_avatar_url)

        if self.debug: print 'rez_avatar/rez url = ' + self.rez_avatar_url

    def tearDown(self):
        
        # we don't login, don't need to logout :)
        pass
    
    def postToCap(self, arguments):

        if self.debug: print 'posting to cap = ' + str(arguments)
        
        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            #print 'Exception: ' + e.message + ' ' + str(e.args)
            result = str(e.args)
        return result

    
    def check_response(self, result):
        """ check for the eistence of the correct parameters in the cap response """
        
        self.assertNotEquals(result, None, 'post to cap returned nothing')
                   
###################################
#           Test Cases            #
###################################
    # Tests to write include (among many others):
    #    additional parameters
    #    bad inputs
    
    def test_rez_avatar_rez_required(self):
        """ agent is allowed to rez when passing the required params """

        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)

        self.check_response(result)
        self.assertEquals(result['connect'], True)

    def test_rez_avatar_rez_full(self):
        """ agent is allowed to rez when passing the required params """

        result = self.postToCap(self.full_parameters)

        if self.debug: print 'result  = ' + str(result)

        self.check_response(result)
        self.assertEquals(result['connect'], True)
    
    def test_cap_rez_avatar_rez_success_params(self):
    
        result = self.postToCap(self.required_parameters)
        
        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        # Successful response: { connect: "True" look_at: [x real ,y real, z real, ] , position: [x real ,y real, z real, ], rez_avatar/derez: cap }
        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position') and
                     result.has_key('rez_avatar/derez'), 'successful cap post is missing parameters in the response')

    def test_cap_rez_avatar_rez_success_keys(self):
        """ test that a success response contains no additional keys """
        
        result = self.postToCap(self.required_parameters)
        
        self.check_response(result)

        if self.debug: print 'result  = ' + str(result)
        
        valid_keys = ['connect', 'look_at', 'position', 'rez_avatar/derez']
        fail = 0 
        extra_keys = ''
        
        for key in result:
            try:
                valid_keys.index(key) # if the key is in our valid list, sweet
            except:
                fail = 1
                extra_keys = extra_keys + ' ' + key
        
        self.assertEquals(fail, 0, 'response has additional keys: ' + extra_keys)        
                     
    def test_rez_avatar_rez_position(self):
        """ verify position values are within range """

        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        # LL convention. OpenSim too atm?
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)
    
    def test_rez_avatar_rez_connect(self):
        """ verify position values are within range """

        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)        
        self.assertEquals(result['connect'], True)
                     
    def test_rez_avatar_rez_derez_cap(self):
        """ verify look_at values are within range """

        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        self.assert_(result.has_key('rez_avatar/derez'))
        
    def test_rez_avatar_rez_nocontent(self):
        """ verify look_at values are within range """
          
        empty_parameters = {
           'circuit_code' : '',
           'position' : '',
           'secure_session_id' : '',
           'session_id' : ''
           }
           
        result = self.postToCap(empty_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)
        self.assertEquals(result['connect'], False)
    
    def test_rez_avatar_rez_failure_params(self):
        """ check for the eistence of the correct parameters in the cap response """

        empty_parameters = {
           'circuit_code' : '',
           'position' : '',
           'secure_session_id' : '',
           'session_id' : ''
           }

        result = self.postToCap(empty_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        # Failure response: { connect: False, redirect: False, resethome: False, message: string } 
        self.assert_(result.has_key('connect') and
                     result.has_key('redirect') and
                     result.has_key('resethome') and
                     result.has_key('message'), 'failure cap post is missing parameters')
 
    def test_rez_avatar_rez_missing_cc(self):
        """ verify response to missing circuit code """

        self.required_parameters['circuit_code'] = ''
        
        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)        
        self.assertEquals(result['connect'], False)
        self.assertEquals(result['message'], 'No valid circuit code.', 'invalid message value')

    def test_rez_avatar_rez_missing_position(self):
        """ verify response to missing position """

        self.required_parameters['position'] = ''
        
        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)        
        self.assertEquals(result['connect'], False)
        #self.assertEquals(result['message'], '', 'invalid message value') 

    def test_rez_avatar_rez_missing_ssid(self):
        """ verify response to missing secure session id """

        self.required_parameters['secure_session_id'] = ''
        
        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)        
        self.assertEquals(result['connect'], False)
        #self.assertEquals(result['message'], '', 'invalid message value')

    def test_rez_avatar_rez_missing_sid(self):
        """ verify response to missing session id """

        self.required_parameters['session_id'] = ''
        
        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)        
        self.assertEquals(result['connect'], False)
        self.assertEquals(result['message'], 'No valid session id.', 'invalid message value')

    def test_rez_avatar_rez_invalid_cc(self):
        """ verify response to invalid circuit code """

        self.required_parameters['circuit_code'] = 'invalid cc'
        
        result = self.postToCap(self.required_parameters)

        self.check_response(result)        
        self.assertEquals(result['connect'], False)
        self.assertEquals(result['message'], 'No valid circuit code.', 'invalid message value')

    def test_rez_avatar_rez_invalid_position(self):
        """ verify response to invalid position """

        self.required_parameters['position'] = 'lookoverthere'
        
        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)        
        self.assertEquals(result['connect'], False)
        #self.assertEquals(result['message'], '', 'invalid message value') 

    def test_rez_avatar_rez_invalid_ssid(self):
        """ verify response to invalid secure_session_id """

        self.required_parameters['secure_session_id'] = '00000000-000000-0000-0000-000000000000'
        
        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)        
        self.assertEquals(result['connect'], False)
        #self.assertEquals(result['message'], '', 'invalid message value')

    def test_rez_avatar_rez_invalid_sid(self):
        """ verify response to invalid session_id """

        self.required_parameters['session_id'] = '00000000-000000-0000-0000-000000000000'
        
        result = self.postToCap(self.required_parameters)

        if self.debug: print 'result  = ' + str(result)
        
        self.check_response(result)        
        self.assertEquals(result['connect'], False)
        self.assertEquals(result['message'], 'No valid session id.', 'invalid message value')         
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarRezTests))
    return suite

