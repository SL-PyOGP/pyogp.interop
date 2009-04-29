import unittest, doctest
import ConfigParser
import os
from urlparse import urlparse

from eventlet import api

from pyogp.lib.base.agent import Agent
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.utilities.helpers import Wait
from pyogp.lib.base.exc import *

import helpers

class TestRegionCapabilities(unittest.TestCase):

    def setUp(self):

        # initialize the config
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(os.path.join(os.path.dirname(__file__),'testconfig.cfg')))

        self.test_setup_config_name = 'test_interop_account'

        self.firstname = self.config.get(self.test_setup_config_name, 'firstname')
        self.lastname = self.config.get(self.test_setup_config_name, 'lastname')
        self.password = self.config.get(self.test_setup_config_name, 'password')
        self.agent_id = self.config.get(self.test_setup_config_name, 'agent_id')
        self.login_uri = self.config.get(self.test_setup_config_name, 'login_uri')
        self.region = self.config.get('test_interop_regions', 'start_region_uri') 

        self.settings = Settings()
        self.settings.MULTIPLE_SIM_CONNECTIONS = False
        self.settings.ENABLE_INVENTORY_MANAGEMENT = False
        self.settings.ENABLE_EQ_LOGGING = False
        self.settings.ENABLE_UDP_LOGGING = False

        self.client = Agent(self.settings, self.firstname, self.lastname, self.password)

        api.spawn(self.client.login, self.login_uri, self.firstname, self.lastname, self.password, start_location = self.region)

        # wait for the agent to connect to it's region
        while self.client.connected == False:
            api.sleep(0)

        while self.client.region.connected == False:
            api.sleep(0)

    def tearDown(self):
        
        if self.client.connected:
            self.client.logout()
        
    def test_cap_fetch(self):
        """ test various object perms """

        available_caps_aditi = ['RemoteParcelRequest', 'ParcelPropertiesUpdate', 'UpdateScriptAgent', 'ServerReleaseNotes', 'SendPostcard', 'DispatchRegionInfo', 'UpdateScriptTask', 'SearchStatTracking', 'EventQueueGet', 'UpdateNotecardAgentInventory', 'StartGroupProposal', 'SendUserReport', 'NewFileAgentInventory', 'GroupProposalBallot', 'ChatSessionRequest', 'SearchStatRequest', 'UntrustedSimulatorMessage', 'ParcelVoiceInfoRequest', 'UpdateGestureAgentInventory', 'MapLayerGod', 'UpdateGestureTaskInventory', 'CopyInventoryFromNotecard', 'ViewerStats', 'UpdateAgentLanguage', 'HomeLocation', 'MapLayer', 'SendUserReportWithScreenshot', 'ProvisionVoiceAccountRequest']

        # make sure the agent has retrieved all of the expected caps from the seed cap
        [self.assertEquals(self.client.region.capabilities.has_key(capname), True) for capname in available_caps_aditi]

        # etc etc etc


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestRegionCapabilities))
    return suite

    """
    Contributors can be viewed at:
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

    $LicenseInfo:firstyear=2008&license=apachev2$

    Copyright 2009, Linden Research, Inc.

    Licensed under the Apache License, Version 2.0 (the "License").
    You may obtain a copy of the License at:
        http://www.apache.org/licenses/LICENSE-2.0
    or in 
        http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

    $/LicenseInfo$
    """