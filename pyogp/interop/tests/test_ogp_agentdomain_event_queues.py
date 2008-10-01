"""
@file test_ogp_event_queue.py
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


from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.registration import init
from pyogp.lib.base.interfaces import IPlaceAvatar, IEventQueueGet
from zope.component import provideUtility
from pyogp.lib.base.network.interfaces import IUDPClient
from pyogp.lib.base.network.net import NetUDPClient

from helpers import logout

class OGPEventQueue(unittest.TestCase):

    login_uri = None
    start_region_uri = None
    target_region_uri = None

    def setUp(self):
        init() # initialize the framework        
        provideUtility(NetUDPClient(), IUDPClient)

        self.agent_id = ''
        self.session_id = ''

        # initialize the config
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))

        # initialize the config
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(resource_stream(__name__, 'testconfig.cfg'))

        # test attributes
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = config.get(self.test_setup_config_name, 'firstname')
        self.lastname = config.get(self.test_setup_config_name, 'lastname')
        self.password = config.get(self.test_setup_config_name, 'password')
        self.login_uri = config.get(self.test_setup_config_name, 'login_uri')        
        self.start_region_uri = config.get('test_interop_regions', 'start_region_uri')
        self.target_region_uri = config.get('test_interop_regions', 'target_region_uri')

        # set state
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)
        self.agentdomain = AgentDomain(self.login_uri)

        #gets seedcap, and an agent that can be placed in a region
        agent = self.agentdomain.login(credentials)

    def test_ogp_event_queues(self):
    
        ad_event_queue = IEventQueueGet(self.agentdomain)

        start = time.time()
        now = start
        
        # call the eq for 60 seconds
        while ((now - start) < 60):
            result = ad_event_queue()
            now = time.time()
        
        assert result != None
        
           
    def tearDown(self):
        
        if self.agentdomain.loginStatus: # need a flag in the lib for when an agent has logged in 
            logout(self.agentdomain)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(OGPEventQueue))
    return suite
