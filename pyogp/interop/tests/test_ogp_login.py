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

from pyogp.lib.base.agent import Agent
from pyogp.lib.base.agentdomain import AgentDomain


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


    def tearDown(self):
        
        if self.agentdomain.connectedStatus:
            logout(self.agentdomain)
        
    def test_base_login(self):
        """ login with an account which should just work """
        # in the case the of the OGP Beta, memdership in the gridnauts group is required

        # initialize the agent
        agent = Agent()

        # establish agent credentials
        agent.firstname = self.firstname
        agent.lastname = self.lastname
        agent.password = self.password
        #agent.credentials = PlainPasswordCredential(agent.firstname, agent.lastname, agent.password)

        # let's log in an agent to the agentdomain shall we
        agent.login(self.login_uri, self.region_uri)

        # silly hack for teardown until a more formal solution is introduced
        self.agentdomain = agent.agentdomain

        #gets seedcap, and an agent that can be placed in a region
        assert agent.agentdomain.seed_cap.public_url != None or agent.agentdomain.seed_cap.public_url != {}, "Login to agent domain failed"
        
        # test that rez_avatar/place contains the proper respose data
        assert agent.region.details['region_seed_capability'] != None or agent.region.details['region_seed_capability'] != {}, "Rez_avatar/place returned no seed cap"
        assert agent.region.details['look_at'] != None or agent.region.details['look_at'] != {}, "Rez_avatar/place returned no look_at"
        assert agent.region.details['sim_ip'] != None or agent.region.details['sim_ip'] != {}, "Rez_avatar/place returned no sim_ip"
        assert agent.region.details['sim_port'] != None or agent.region.details['sim_port'] != {}, "Rez_avatar/place returned no sim_port"
        assert agent.region.details['region_x'] != None or agent.region.details['region_x'] != {}, "Rez_avatar/place returned no region_x"
        assert agent.region.details['region_y'] != None or agent.region.details['region_y'] != {}, "Rez_avatar/place returned no region_y"
        assert agent.region.details['region_id'] != None or agent.region.details['region_id'] != {}, "Rez_avatar/place returned no region_id"
        assert agent.region.details['sim_access'] != None or agent.region.details['sim_access'] != {}, "Rez_avatar/place returned no sim_access"
        assert agent.region.details['connect'] != None or agent.region.details['connect'] != {}, "Rez_avatar/place returned no connect"
        assert agent.region.details['position'] != None or agent.region.details['position'] != {}, "Rez_avatar/place returned no position"
        assert agent.region.details['session_id'] != None or agent.region.details['session_id'] != {}, "Rez_avatar/place returned no session_id"
        assert agent.region.details['secure_session_id'] != None or agent.region.details['secure_session_id'] != {}, "Rez_avatar/place returned no secure_session_id"
        assert agent.region.details['circuit_code'] != None or agent.region.details['circuit_code'] != {}, "Rez_avatar/place returned no cicuit_code"
 
    def test_auth_base_account(self):
        """ auth with an account which should just work """

        # initialize the agent
        agent = Agent()

        # establish agent credentials
        agent.setCredentials(self.firstname, self.lastname, self.password)

        # initialize an agent domain object
        self.agentdomain = AgentDomain(self.login_uri)  
                
        response = self.agentdomain.post_to_loginuri(agent.credentials)
        data = self.agentdomain.parse_login_response(response)
        
        assert (data.has_key('authenticated') and
                data.has_key('agent_seed_capability'))
        
        assert data['authenticated'] == True
        # this is the AD seed cap
        assert data['agent_seed_capability'] != None
  
    def test_auth_unknown_account(self):
        """ auth with an account which should just never work """
   
        # initialize the agent
        agent = Agent()

        # establish agent credentials
        agent.setCredentials('foxinsox', 'greeneggsandham', 'tweetlebeetlebattle')

        # initialize an agent domain object
        self.agentdomain = AgentDomain(self.login_uri)  
                
        response = self.agentdomain.post_to_loginuri(agent.credentials)
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
