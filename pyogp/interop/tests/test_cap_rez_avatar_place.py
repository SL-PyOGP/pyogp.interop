"""
@file test_cap_rez_avatar_place.py
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

# std_lib
import unittest
import ConfigParser
from pkg_resources import resource_stream

# pygop
from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability
from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain

# pyogp.interop
from helpers import logout

'''
Tests for the rez_avatar/place capability as run against simulators (acting as the client)

http://wiki.secondlife.com/wiki/OGP_Teleport_Draft_3#POST_Interface
'''

class RezAvatarPlaceTests(unittest.TestCase):
    """ test posting to rez_avatar/place for a simulator, acting as the region domain """
    
    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = config.get(self.test_setup_config_name, 'firstname')
        self.lastname = config.get(self.test_setup_config_name, 'lastname')
        self.password = config.get(self.test_setup_config_name, 'password')
        self.login_uri = config.get(self.test_setup_config_name, 'login_uri')        
        self.region_uri = config.get('test_interop_regions', 'start_region_uri') 

        # first establish an AD connection and get seed_cap for mtg
        # <start>
        self.agentdomain = AgentDomain(self.login_uri)
        
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)

        #gets seedcap, and an agent that can be placed in a region
        self.agentdomain.login(credentials)
         
        # required_parameters: { region_url: url string, position: [x real, y real, z real, ] }
        self.required_parameters = {
            'region_url' : self.region_uri + "/public_seed",
            'position' : config.get('test_rez_avatar_place', 'position')
            }
            
        self.caps = self.agentdomain.seed_cap.get(['rez_avatar/place'])
        
        # initialize the cap object for use in postToCap
        self.capability = Capability('rez_avatar/place', self.caps['rez_avatar/place'].public_url)
              
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
        """ check for the existence of the correct parameters in the cap response """

        # Success response: { connect: bool , region_seed_capability: url string , look_at: [x real, y real, z real, ] , position: [x real, y real, z real, ]}
        self.assertNotEquals(result, None, 'empty response')
        self.assertNotEquals(result, "()", 'empty response')

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
        
        self.check_response(result)
        
        valid_keys = ['connect', 'look_at', 'position', 'public_region_seed_capability', 'sim_host', 'sim_port', 'region_id', 'region_x', 'region_y', 'sim_access', 'position']
        fail = 0 
        extra_keys = ''
        missing_keys = ''
        
        for key in result:
            try:
                valid_keys.index(key) # if the key is in our valid list, sweet
            except:
                fail_extra = 1
                extra_keys = extra_keys + ' ' + key

        for key in valid_keys:
            try:
                result.index(key) # if the key is in our valid list, sweet
            except:
                fail_missing = 1
                missing_keys = missing_keys + ' ' + key
       
        self.assertEquals(fail_extra, 0, 'response has additional keys: ' + extra_keys)
        self.assertEquals(fail_missing, 0, 'response is missing keys: ' + missing_keys)       
        
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
                     
        self.assert_(result['region_seed_capability'] != None)
        
        assert result['sim_access'] == 'PG' or result['sim_access'] == 'Mature'

    def test_rez_avatar_place_nocontent(self):
        """ agent is allowed to rez """

        result = self.postToCap({})
        
        self.check_response(result)
        #self.assertRaises(HTTPError, self.postToCap(self.required_parameters))

    def test_rez_avatar_place_invalid_region_uri(self):
        """ agent is allowed to rez """

        self.required_parameters['region_url'] = 'http://sim2.vaak.lindenlab.com:13009/imtotallyfake'
        result = self.postToCap(self.required_parameters)

        # the library is trapping the 400, perhaps it should be allowed to filter here for testing? 
        self.check_response(result)
        #self.assertRaises(HTTPError, self.postToCap(self.required_parameters))

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarPlaceTests))
    return suite

