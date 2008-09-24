"""
@file test_ogp_login.py
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
import unittest, doctest
import ConfigParser
from pkg_resources import resource_stream

# zca
from zope.component import queryUtility, adapts, getUtility

# pyogp.lib.base
from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base.interfaces import IPlaceAvatar # ToDo: move to agentdomain.PlaceAvatar?
#from pyogp.lib.base.OGPLogin import OGPLogin
from pyogp.lib.base.interfaces import ISerialization
from pyogp.lib.base.network import IRESTClient

# pyogp.interop
from helpers import logout

class AuthOGPLoginTest(unittest.TestCase):
   
    def setUp(self):

        # initialize the config
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(resource_stream(__name__, 'testconfig.cfg'))
                
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = self.config.get(self.test_setup_config_name, 'firstname')
        self.lastname = self.config.get(self.test_setup_config_name, 'lastname')
        self.password = self.config.get(self.test_setup_config_name, 'password')
        self.login_uri = self.config.get(self.test_setup_config_name, 'login_uri')        
        self.region_uri = self.config.get('test_interop_regions', 'start_region_uri') 

        self.agentdomain = AgentDomain(self.login_uri)

    def tearDown(self):
        
        if self.agentdomain.loginStatus: # need a flag in the lib for when an agent has logged in 
            logout(self.agentdomain)
        
    def test_base_login(self):
        """ login with an account which should just work """
        # in the case the of the OGP Beta, memdership in the gridnauts group is required
 
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)

        #gets seedcap, and an agent that can be placed in a region
        self.agentdomain.login(credentials)

        #gets seedcap, and an agent that can be placed in a region
        assert self.agentdomain.seed_cap.public_url != None or self.agentdomain.seed_cap.public_url != {}, "Login to agent domain failed"
 
        caps = self.agentdomain.seed_cap.get(['rez_avatar/place'])

        # try and connect to a sim
        self.region = Region(self.region_uri)
        place = IPlaceAvatar(self.agentdomain)

        self.avatar  = place(self.region)
        
        #print self.client.region.details
        
        # test that rez_avatar/place contains the proper respose data
        assert self.avatar.region.details['region_seed_capability'] != None or self.avatar.region.details['region_seed_capability'] != {}, "Rez_avatar/place returned no seed cap"
        assert self.avatar.region.details['look_at'] != None or self.avatar.region.details['look_at'] != {}, "Rez_avatar/place returned no look_at"
        assert self.avatar.region.details['sim_ip'] != None or self.avatar.region.details['sim_ip'] != {}, "Rez_avatar/place returned no sim_ip"
        assert self.avatar.region.details['sim_port'] != None or self.avatar.region.details['sim_port'] != {}, "Rez_avatar/place returned no sim_port"
        assert self.avatar.region.details['region_x'] != None or self.avatar.region.details['region_x'] != {}, "Rez_avatar/place returned no region_x"
        assert self.avatar.region.details['region_y'] != None or self.avatar.region.details['region_y'] != {}, "Rez_avatar/place returned no region_y"
        assert self.avatar.region.details['region_id'] != None or self.avatar.region.details['region_id'] != {}, "Rez_avatar/place returned no region_id"
        assert self.avatar.region.details['sim_access'] != None or self.avatar.region.details['sim_access'] != {}, "Rez_avatar/place returned no sim_access"
        assert self.avatar.region.details['connect'] != None or self.avatar.region.details['connect'] != {}, "Rez_avatar/place returned no connect"
        assert self.avatar.region.details['position'] != None or self.avatar.region.details['position'] != {}, "Rez_avatar/place returned no position"
        assert self.avatar.region.details['session_id'] != None or self.avatar.region.details['session_id'] != {}, "Rez_avatar/place returned no session_id"
        assert self.avatar.region.details['secure_session_id'] != None or self.avatar.region.details['secure_session_id'] != {}, "Rez_avatar/place returned no secure_session_id"
        assert self.avatar.region.details['circuit_code'] != None or self.avatar.region.details['circuit_code'] != {}, "Rez_avatar/place returned no cicuit_code"

    def test_auth_base_account(self):
        """ auth with an account which should just work """

        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)        
                
        response = self.agentdomain.post_to_loginuri(credentials)
        data = self.agentdomain.parse_login_response(response)
        
        assert (data.has_key('authenticated') and
                data.has_key('agent_seed_capability'))
        
        assert data['authenticated'] == True
        # this is the AD seed cap
        assert data['agent_seed_capability'] != None
        
    def test_auth_unknown_account(self):
        """ auth with an account which should just never work """
        
        credentials = PlainPasswordCredential('foxinsox', 'greeneggsandham', 'tweetlebeetlebattle')        
                
        response = self.agentdomain.post_to_loginuri(credentials)
        data = self.agentdomain.parse_login_response(response)

        self.assert_(data.has_key('authenticated') and
                data.has_key('reason') and
                data.has_key('message'))
        
        assert data['authenticated'] == False
        assert data['message'] == 'Agent does not exist'
        assert data['reason'] == 'data'

                
    # Other tests to write:

    # test_auth_(good account with bad password)
    # test_auth_(new account that hasn't accepted ToS etc yet)
    # Infinity's tests will likely cover much of this
    # test invalid inputs: variations of no firstname, lastname, password/md5password
    # test including additional parameters
    # test bad region uri
    # etc
    
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(AuthOGPLoginTest))
    return suite
