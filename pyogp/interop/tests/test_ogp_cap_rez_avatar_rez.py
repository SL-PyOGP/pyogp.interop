"""
@file test_cap_rez_avatar_rez.py
@date 2008-09-16
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2008, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0
or in 
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""

# std lib
import unittest
import ConfigParser
from pkg_resources import resource_stream

# pygop
from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability
from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base.interfaces import IPlaceAvatar

# pyogp.interop
from helpers import logout

'''
Tests for the rez_avatar/rez capability as run against simulators (acting as the agent domain)

write tests against the protocol as is defined at 
http://wiki.secondlife.com/wiki/OGP_Teleport_Draft_3#POST_Interface_3
'''

class RezAvatarRezTests(unittest.TestCase):
    """ test posting to rez_avatar/rez for a simulator, acting as the region domain """
    
    def setUp(self):
        init()
        
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = self.config.get(self.test_setup_config_name, 'firstname')
        self.lastname = self.config.get(self.test_setup_config_name, 'lastname')
        self.password = self.config.get(self.test_setup_config_name, 'password')
        self.login_uri = self.config.get(self.test_setup_config_name, 'login_uri')        
        self.region_uri = self.config.get('test_interop_regions', 'start_region_uri') 

        # first establish an AD connection and get seed_cap for mtg
        # <start>
        self.agentdomain = AgentDomain(self.login_uri)
        
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)

        #gets seedcap, and an agent that can be placed in a region
        self.agentdomain.login(credentials)
 
        caps = self.agentdomain.seed_cap.get(['rez_avatar/place'])

        # try and connect to a sim
        self.region = Region(self.region_uri)
        place = IPlaceAvatar(self.agentdomain)

        self.avatar = place(self.region)
        # </start>
        
                # Required parameters: { circuit_code: int, position: [x real ,y real, z real, ], secure_session_id: uuid , session_id: uuid , avatar_data: TBD }
        # Note the TBD on avatar data
        self.required_parameters = { 
           'circuit_code' : self.avatar.region.details['circuit_code'],
           'position' : self.config.get('test_rez_avatar_rez', 'position'),
           'secure_session_id' : self.avatar.region.details['secure_session_id'],
           'session_id' : self.avatar.region.details['session_id']
           }
           
        # we can't request this cap, but we can craft it ourselves        
        self.rez_avatar_url  = self.region_uri + '/agent/' + self.avatar.region.details['agent_id'] + '/rez_avatar/rez'
               
        # Set state for the test
        #     The sim doesn't care about the agent domain per se for rez_avatar/rez
        #     We can work jsut with a rez_avatar_url and post params
        self.capability = Capability('rez_avatar/rez', self.rez_avatar_url)
        
    def tearDown(self):
        
        if self.agentdomain.loginStatus: # need a flag in the lib for when an agent has logged in 
            logout(self.agentdomain)
    
    def postToCap(self, arguments):

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

        self.check_response(result)

        self.assert_(result.has_key('connect') and
             result.has_key('look_at') and
             result.has_key('position'))
             # removed in OGP Draft 3 docs
             #result.has_key('rez_avatar/derez'), 'successful cap post is missing parameters in the response')
             
        self.assertEquals(result['connect'], True)

        self.assert_(result['look_at'][0] < 256 and
                     result['look_at'][1] < 256 and 
                     result['look_at'][2] < 256)

        self.assert_(result['look_at'][0] >= 0 and
                     result['look_at'][1] >= 0 and 
                     result['look_at'][2] >= 0)
                                          
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)

        self.assert_(result['position'][0] >= 0 and
                     result['position'][1] >= 0 and 
                     result['position'][2] >= 0)

        valid_keys = ['connect', 'look_at', 'position']
        fail = 0 
        extra_keys = ''
        
        for key in result:
            try:
                valid_keys.index(key) # if the key is in our valid list, sweet
            except:
                fail = 1
                extra_keys = extra_keys + ' ' + key
        
        self.assertEquals(fail, 0, 'response has additional keys: ' + extra_keys)       
    
    def test_rez_avatar_rez_nocontent(self):
        """ verify look_at values are within range """
          
        empty_parameters = {
           'circuit_code' : '',
           'position' : '',
           'secure_session_id' : '',
           'session_id' : ''
           }
           
        result = self.postToCap(empty_parameters)
        
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
        
        # Failure response: { connect: False, redirect: False, resethome: False, message: string } 
        self.assert_(result.has_key('connect') and
                     result.has_key('redirect') and
                     result.has_key('resethome') and
                     result.has_key('message'), 'failure cap post is missing parameters')
 
    def test_rez_avatar_rez_missing_cc(self):
        """ verify response to missing circuit code """

        self.required_parameters['circuit_code'] = ''
        
        result = self.postToCap(self.required_parameters)
        
        self.check_response(result)        
        self.assertEquals(result['connect'], False)
        self.assertEquals(result['message'], 'No valid circuit code.', 'invalid message value')

    def test_rez_avatar_rez_missing_position(self):
        """ verify response to missing position """

        self.required_parameters['position'] = ''
        
        result = self.postToCap(self.required_parameters)
        
        self.assertEquals(result['connect'], True)

        self.assert_(result['look_at'][0] < 256 and
                     result['look_at'][1] < 256 and 
                     result['look_at'][2] < 256)

        self.assert_(result['look_at'][0] >= 0 and
                     result['look_at'][1] >= 0 and 
                     result['look_at'][2] >= 0)
                                          
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)

        self.assert_(result['position'][0] >= 0 and
                     result['position'][1] >= 0 and 
                     result['position'][2] >= 0)

    def test_rez_avatar_rez_missing_ssid(self):
        """ verify response to missing secure session id """

        self.required_parameters['secure_session_id'] = ''
        
        result = self.postToCap(self.required_parameters)
        
        self.check_response(result)        

        self.assertEquals(result['connect'], True)

        self.assert_(result['look_at'][0] < 256 and
                     result['look_at'][1] < 256 and 
                     result['look_at'][2] < 256)

        self.assert_(result['look_at'][0] >= 0 and
                     result['look_at'][1] >= 0 and 
                     result['look_at'][2] >= 0)
                                          
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)

        self.assert_(result['position'][0] >= 0 and
                     result['position'][1] >= 0 and 
                     result['position'][2] >= 0)

    def test_rez_avatar_rez_missing_sid(self):
        """ verify response to missing session id """

        self.required_parameters['session_id'] = ''
        
        result = self.postToCap(self.required_parameters)
        
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
        
        self.check_response(result)   
             
        self.assertEquals(result['connect'], True)

        self.assert_(result['look_at'][0] < 256 and
                     result['look_at'][1] < 256 and 
                     result['look_at'][2] < 256)

        self.assert_(result['look_at'][0] >= 0 and
                     result['look_at'][1] >= 0 and 
                     result['look_at'][2] >= 0)
                                          
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)

        self.assert_(result['position'][0] >= 0 and
                     result['position'][1] >= 0 and 
                     result['position'][2] >= 0)

    def test_rez_avatar_rez_invalid_ssid(self):
        """ verify response to invalid secure_session_id """

        self.required_parameters['secure_session_id'] = '00000000-000000-0000-0000-000000000000'
        
        result = self.postToCap(self.required_parameters)
        
        self.check_response(result)        

        self.assertEquals(result['connect'], True)

        self.assert_(result['look_at'][0] < 256 and
                     result['look_at'][1] < 256 and 
                     result['look_at'][2] < 256)

        self.assert_(result['look_at'][0] >= 0 and
                     result['look_at'][1] >= 0 and 
                     result['look_at'][2] >= 0)
                                          
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)

        self.assert_(result['position'][0] >= 0 and
                     result['position'][1] >= 0 and 
                     result['position'][2] >= 0)

    def test_rez_avatar_rez_invalid_sid(self):
        """ verify response to invalid session_id """

        self.required_parameters['session_id'] = '00000000-000000-0000-0000-000000000000'
        
        result = self.postToCap(self.required_parameters)
        
        self.check_response(result)        
        self.assertEquals(result['connect'], False)
        self.assertEquals(result['message'], 'No valid session id.', 'invalid message value')         
        

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarRezTests))
    return suite

