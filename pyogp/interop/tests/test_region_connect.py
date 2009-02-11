"""
@file test_sim_presence.py
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

import sys
sys.path.insert(0, '/Users/enus/svn/pyogp/trunk/src/lib')
from eventlet import api

from pyogp.lib.base.agent import Agent
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.circuit import Host
from pyogp.lib.base.message.types import MsgType
#from pyogp.lib.base.message.packet_handler import *

from pyogp.lib.base.network.net import NetUDPClient

import helpers


class OGPPresenceTest(unittest.TestCase):

    login_uri = None
    start_region_uri = None
    target_region_uri = None

    def setUp(self):

        self.agent_id = ''
        self.session_id = ''

        # initialize the config
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
                
        test_setup_config_name = 'test_interop_account'
        
        self.firstname = config.get(test_setup_config_name, 'firstname')
        self.lastname = config.get(test_setup_config_name, 'lastname')
        self.password = config.get(test_setup_config_name, 'password')
        #self.login_uri = config.get(test_setup_config_name, 'login_uri')        
        self.login_uri = "https://login.nandi.lindenlab.com/cgi-bin/login.cgi"
        #self.start_region_uri = config.get('test_interop_regions', 'start_region_uri')        
        self.start_region_uri = "uri:morris&128&128&128"

        #don't need a port, not sure why we have it there yet
        #self.messenger = UDPDispatcher()
        #self.host = None

        self.agent = Agent()

        # establish agent credentials
        self.agent.firstname = self.firstname
        self.agent.lastname = self.lastname
        self.agent.password = self.password

        self.agent.login(self.login_uri, self.start_region_uri)

    def test_base_presence(self):
    
        self.agent_id = self.agent.region.details['agent_id']
        self.session_id = self.agent.region.details['session_id']

        self.agent.region.connect()
        #self.agent.region.get_region_capabilities()

        watcher = self.agent.region.messenger.packet_handler._register_callback('PacketAck')
        watcher2 = self.agent.region.messenger.packet_handler._register_callback('PacketAck')
        watcher.event += idunbeenseen
        watcher2.event += idunbeenseen2
        '''
        from pyogp.lib.base.message.packets import *
        import uuid

        packet = ChatFromSimulatorPacket()
        packet.ChatData['FromName'] = 'None'    # MVT_VARIABLE
        packet.ChatData['SourceID'] = uuid.UUID(self.agent.region.details['agent_id'])    # MVT_LLUUID
        packet.ChatData['OwnerID'] = uuid.UUID(self.agent.region.details['agent_id'])    # MVT_LLUUID
        packet.ChatData['SourceType'] = 0    # MVT_U8
        packet.ChatData['ChatType'] = 1    # MVT_U8
        packet.ChatData['Audible'] = 1    # MVT_U8
        packet.ChatData['Position'] = (0.0, 0.1, 0.0)    # MVT_LLVector3
        packet.ChatData['Message'] = 'Hi, I am trying to talk'    # MVT_VARIABLE
        #self.agent.region.messenger.send_message(packet(), self.agent.region.host)
        '''
        while True:
            #print 'Back in main'
            api.sleep(0)

    def tearDown(self):
        
        if self.agent.agentdomain.connectedStatus: # need a flag in the lib for when an agent has logged in         
            msg = Message('LogoutRequest',
                      Block('AgentData', AgentID=uuid.UUID(self.agent_id),
                            SessionID=uuid.UUID(self.session_id)
                            )
                      )
            self.messenger.send_message(msg, self.host)

def idunbeenseen(packet):

    print "WOOT, packet callback gotrdun " + packet.name

def idunbeenseen2(packet):

    print "WOOT222222222, packet callback gotrdun " + packet.name

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(OGPPresenceTest))
    return suite
