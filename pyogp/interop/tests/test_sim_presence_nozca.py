"""
@file test_presence.py
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

from pyogp.lib.base.agent import Agent
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.circuit import Host
from pyogp.lib.base.message.types import MsgType

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
        self.login_uri = config.get(test_setup_config_name, 'login_uri')        
        self.start_region_uri = config.get('test_interop_regions', 'start_region_uri')        
        
        #don't need a port, not sure why we have it there yet
        self.messenger = UDPDispatcher()
        self.host = None

        self.agent = Agent()

        # establish agent credentials
        self.agent.firstname = self.firstname
        self.agent.lastname = self.lastname
        self.agent.password = self.password

        self.agent.login(self.login_uri, self.start_region_uri)

    def test_base_presence(self):
    
        self.agent_id = self.agent.region.details['agent_id']
        self.session_id = self.agent.region.details['session_id']
        
        #begin UDP communication
        self.host = Host((self.agent.region.details['sim_ip'],
                    self.agent.region.details['sim_port']))

        #SENDS UseCircuitCode
        msg = Message('UseCircuitCode',
                      Block('CircuitCode', Code=self.agent.region.details['circuit_code'],
                            SessionID=uuid.UUID(self.session_id),
                            ID=uuid.UUID(self.agent_id)))
        self.messenger.send_reliable(msg, self.host, 0)

        time.sleep(1)

        #SENDS CompleteAgentMovement
        msg = Message('CompleteAgentMovement',
                      Block('AgentData', AgentID=uuid.UUID(self.agent_id),
                            SessionID=uuid.UUID(self.session_id),
                            CircuitCode=self.agent.region.details['circuit_code']))
        self.messenger.send_reliable(msg, self.host, 0)

        #SENDS UUIDNameRequest
        msg = Message('UUIDNameRequest',
                      Block('UUIDNameBlock', ID=uuid.UUID(self.agent_id)
                            )
                      )
        self.messenger.send_message(msg, self.host)

        self.send_agent_update(self.agent_id, self.session_id)

        #print "Entering loop"
        last_ping = 0
        start = time.time()
        now = start
        packets = {}
        
        # run for 45 seonds
        while ((now - start) < 45):
            msg_buf, msg_size = self.messenger.udp_client.receive_packet(self.messenger.socket)
            packet = self.messenger.receive_check(self.messenger.udp_client.get_sender(),
                                            msg_buf, msg_size)
            if packet != None:
                #print 'Received: ' + packet.name + ' from  ' + self.messenger.udp_client.sender.ip + ":" + \
                                                  #str(self.messenger.udp_client.sender.port)

                #MESSAGE HANDLERS
                if packet.name == 'RegionHandshake':
                    self.send_region_handshake_reply(self.agent_id, self.session_id)
                elif packet.name == 'StartPingCheck':
                    self.send_complete_ping_check(last_ping)
                    last_ping += 1
                   
                if packet.name not in packets:
                    packets[packet.name] = 1
                else: 
                    packets[packet.name] += 1                   
                
            else:
                #print 'No message'
                pass
                
            now = time.time()
                
            if self.messenger.has_unacked():
                #print 'Acking'
                self.messenger.process_acks()
                self.send_agent_update(self.agent_id, self.session_id)

        # let's test something to prove presence on the sim

        assert self.agent.region.details['region_seed_capability'] != None or self.agent.region.details['region_seed_capability'] != {}, "Rez_avatar/place returned no seed cap"
        assert len(packets) > 0
        self.assertNotEqual(last_ping, 0)
        self.assert_("CoarseLocationUpdate" in packets)
        self.assert_("StartPingCheck" in packets) 
        self.assert_("AgentDataUpdate" in packets) 
       
    def tearDown(self):
        
        if self.agent.agentdomain.connectedStatus: # need a flag in the lib for when an agent has logged in         
            msg = Message('LogoutRequest',
                      Block('AgentData', AgentID=uuid.UUID(self.agent_id),
                            SessionID=uuid.UUID(self.session_id)
                            )
                      )
            self.messenger.send_message(msg, self.host)

    def send_agent_update(self, agent_id, session_id):
        msg = Message('AgentUpdate',
                      Block('AgentData', AgentID=uuid.UUID(agent_id),
                            SessionID=uuid.UUID(self.session_id),
                            BodyRotation=(0.0,0.0,0.0,0.0),
                            HeadRotation=(0.0,0.0,0.0,0.0),
                            State=0x00,
                            CameraCenter=(0.0,0.0,0.0),
                            CameraAtAxis=(0.0,0.0,0.0),
                            CameraLeftAxis=(0.0,0.0,0.0),
                            CameraUpAxis=(0.0,0.0,0.0),
                            Far=0,
                            ControlFlags=0x00,
                            Flags=0x00))

        self.messenger.send_message(msg, self.host)

    def send_region_handshake_reply(self, agent_id, session_id):
        msg = Message('RegionHandshakeReply',
                      [Block('AgentData', AgentID=uuid.UUID(agent_id),
                            SessionID=uuid.UUID(self.session_id)),
                       Block('RegionInfo', Flags=0x00)])

        self.messenger.send_message(msg, self.host)
    
    def send_complete_ping_check(self, ping):
        msg = Message('CompletePingCheck',
                      Block('PingID', PingID=ping))

        self.messenger.send_message(msg, self.host)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(OGPPresenceTest))
    return suite
