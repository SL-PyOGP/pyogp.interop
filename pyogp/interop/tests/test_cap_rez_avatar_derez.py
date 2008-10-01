"""
@file test_cap_rez_avatar_derez.py
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
import unittest, time
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
import helpers

'''
# in progress, tests are skipped

Tests for the rez_avatar/derez capability as run against simulators (acting as the agent domain)

write tests against the protocol as is defined at 
http://wiki.secondlife.com/wiki/OGP_Teleport_Draft_3#POST_Inferface
'''

class RezAvatarDerezTest(unittest.TestCase):
    """ test posting to rez_avatar/derez for a simulator, acting as the region domain """

    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = config.get(self.test_setup_config_name, 'firstname')
        self.lastname = config.get(self.test_setup_config_name, 'lastname')
        self.password = config.get(self.test_setup_config_name, 'password')
        self.login_uri = config.get(self.test_setup_config_name, 'login_uri')        
        self.start_region_uri = config.get('test_interop_regions', 'start_region_uri') 
        self.target_region_uri = config.get('test_interop_regions', 'target_region_uri') 
        
        # first establish an AD connection and get seed_cap for mtg
        # <start>
        self.agentdomain = AgentDomain(self.login_uri)
        
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)

        #gets seedcap, and an agent that can be placed in a region
        self.agentdomain.login(credentials)
 
        caps = self.agentdomain.seed_cap.get(['rez_avatar/place'])

        # try and connect to a sim
        self.region = Region(self.start_region_uri)
        place = IPlaceAvatar(self.agentdomain)

        self.avatar = place(self.region)
        # </start>
        
        self.position = config.get('test_rez_avatar_derez', 'position') 

        # we can't request these caps as a client, but we can craft them ourselves
        self.rez_avatar_url = self.start_region_uri + '/agent/' + self.avatar.region.details['agent_id'] + '/rez_avatar/rez'
        self.derez_avatar_url = self.target_region_uri + '/agent/' + self.avatar.region.details['agent_id'] + '/rez_avatar/derez'
        
        # Required parameters: { rez-avatar/rez: url string, position: [x real, y real, z real, ] }              
        self.required_parameters = {
            'rez_avatar/rez' : self.rez_avatar_url,
            'position' : self.position
            }
        
        self.capability = Capability('rez_avatar/derez', self.derez_avatar_url)              

        
    def tearDown(self):
        pass
        # uncomment once this test can be used
        # self.client.logout()


    def postToCap(self, arguments):
      
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

        result = self.postToCap(self.required_parameters)
        
        self.check_successful_response(result)
        self.assertEquals(result['connect'], True)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarDerezTest))
    return suite

