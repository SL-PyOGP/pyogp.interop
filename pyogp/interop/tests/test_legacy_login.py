"""
@file test_legacy_login.py
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

import unittest, doctest
import ConfigParser
from pkg_resources import resource_stream
import time
import uuid
import pprint

from pyogp.lib.base.agent import Agent
from pyogp.lib.base.datatypes import UUID
from pyogp.lib.base.exc import LoginError
from pyogp.lib.base.settings import Settings

import helpers

class AuthLegacyLoginTest(unittest.TestCase):
   
    def setUp(self):
        
        # initialize the config
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(resource_stream(__name__, 'testconfig.cfg'))
                
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = self.config.get(self.test_setup_config_name, 'firstname')
        self.lastname = self.config.get(self.test_setup_config_name, 'lastname')
        self.password = self.config.get(self.test_setup_config_name, 'password')
        self.agent_id = self.config.get(self.test_setup_config_name, 'agent_id')
        self.login_uri = self.config.get(self.test_setup_config_name, 'login_uri')
        self.region = self.config.get('test_interop_regions', 'start_region_uri') 

        self.successful_login_reponse_params = ['last_name', 'sim_ip', 'inventory-lib-root', 'start_location', 'inventory-lib-owner', 'udp_blacklist', 'home', 'message', 'agent_access_max', 'first_name', 'agent_region_access', 'circuit_code', 'sim_port', 'seconds_since_epoch', 'secure_session_id', 'look_at',  'ao_transition', 'agent_id', 'inventory_host', 'region_y', 'region_x', 'seed_capability', 'agent_access', 'session_id', 'login']

        self.settings = Settings()
        self.settings.MULTIPLE_SIM_CONNECTIONS = False

        self.client = Agent(self.settings, self.firstname, self.lastname, self.password)

    def tearDown(self):
        
        if self.client.connected:
            self.client.logout()
        
    def test_base_login(self):
        """ login with an account which should just work """

        self.client.settings.ENABLE_INVENTORY_MANAGEMENT = False

        self.client.login(loginuri = self.login_uri, start_location = self.region, connect_region = False)

        # make sure that the login response attributes propagate properly, and, make sure the login against a grid has worked
        self.assertEquals(self.client.grid_type, 'Legacy', 'Storing the wrong grid type based on a \'legacy\' login request')
        self.assertEquals(self.client.firstname, self.firstname)
        self.assertEquals(self.client.lastname, self.lastname)
        self.assertEquals(self.client.lastname, self.lastname)
        self.assertEquals(self.client.name, self.firstname + ' ' + self.lastname)
        self.assertEquals(self.client.connected, True)
        self.assertNotEquals(self.client.agent_id, None)
        self.assertEquals(str(self.client.agent_id), self.agent_id)
        self.assertNotEquals(self.client.session_id, None)
        self.assertNotEquals(self.client.secure_session_id, None)

        self.assertEquals(self.client.login_response['last_name'], self.lastname)
        self.assertEquals(self.client.login_response['first_name'], '"' + self.firstname + '"')
        self.assertEquals(self.client.login_response['login'], 'true')
        self.assertEquals(self.client.login_response['secure_session_id'], str(self.client.secure_session_id))
        self.assertEquals(self.client.login_response['session_id'], str(self.client.session_id))
        self.assertEquals(self.client.login_response['agent_id'], str(self.client.agent_id))
        self.assertNotEquals(self.client.login_response['seed_capability'], '')

        fail = 0
        fail_extra = 0
        fail_missing = 0
        extra_keys = ''
        missing_keys = ''
        
        for key in self.client.login_response:
            try:
                self.successful_login_reponse_params.index(key) # if the key is in our valid list, sweet
            except:
                fail_extra = 1
                extra_keys = extra_keys + ' ' + key

        for key in self.client.login_response:
            try:
                self.successful_login_reponse_params.index(key) # if the key is in our valid list, sweet
            except:
                fail_missing = 1
                missing_keys = missing_keys + ' ' + key
       
        self.assertEquals(fail_extra, 0, 'login response has additional keys: ' + extra_keys)
        self.assertEquals(fail_missing, 0, 'login response is missing keys: ' + missing_keys)

    def test_login_with_bad_password(self):

        self.client.settings.ENABLE_INVENTORY_MANAGEMENT = False

        self.assertRaises(LoginError, self.client.login, loginuri = self.login_uri, password = 'BadPassword', start_location = self.region, connect_region = False)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(AuthLegacyLoginTest))
    return suite
