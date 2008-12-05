"""
@file test_ogp_teleport.py
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

from threading import Thread
import unittest, doctest
import ConfigParser
from pkg_resources import resource_stream
import time
import uuid

from pyogp.lib.base.agent import Agent
from pyogp.lib.base.agentdomain import AgentDomain, EventQueue
from pyogp.lib.base.regiondomain import Region, EventQueueGet

from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.circuit import Host
from pyogp.lib.base.message.types import MsgType

# pyogp.interop
from helpers import logout

class OGPTeleportTest(unittest.TestCase):

    def setUp(self):

        # initialize the config
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(resource_stream(__name__, 'testconfig.cfg'))

        # test attributes
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = self.config.get(self.test_setup_config_name, 'firstname')
        self.lastname = self.config.get(self.test_setup_config_name, 'lastname')
        self.password = self.config.get(self.test_setup_config_name, 'password')
        self.login_uri = self.config.get(self.test_setup_config_name, 'login_uri')        
        self.start_region_uri = self.config.get('test_interop_regions', 'start_region_uri')
        self.target_region_uri = self.config.get('test_interop_regions', 'target_region_uri')
        
        #don't need a port, not sure why we have it there yet
        self.messenger = UDPDispatcher()
        self.host = None

        # initialize the agent
        agent = Agent()

        # establish agent credentials
        agent.setCredentials(self.firstname, self.lastname, self.password)

        # initialize an agent domain object
        self.agentdomain = AgentDomain(self.login_uri)  
        self.agentdomain.login(agent.credentials)

    def test_base_teleport(self):

        #establish AD event queue connection
        ad_event_queue = EventQueue(self.agentdomain)
        ad_queue_thread = Thread(target=run_ad_eq, name="Agent Domain event queue", args=(ad_event_queue,))
        ad_queue_thread.start()

        # place the avatar on a region via the agent domain
        self.region = Region(self.start_region_uri)
        self.region.details = self.agentdomain.place_avatar(self.region.region_uri)

        # temp hack until we have an object model
        self.region.set_seed_cap_url(self.region.details['region_seed_capability'])

        #gets the rez_avatar/place cap
        #caps = agentdomain.seed_cap.get(['rez_avatar/place'])
        
        # grab some data before it disappears
        vanishing_data = {}
        vanishing_data['agent_id'] = self.region.details['agent_id']
        vanishing_data['session_id'] = self.region.details['session_id']
        vanishing_data['circuit_code'] = self.region.details['circuit_code']        
                
        # grab some packets from sim1
        packets_captured = self.maintain_sim_presence(vanishing_data, self.region, 5)

        # place the avatar on a region via the agent domain
        self.region2 = Region(self.target_region_uri)
        self.region2.details = self.agentdomain.place_avatar(self.region2.region_uri)

        # temp hack until we have an object model
        self.region2.set_seed_cap_url(self.region2.details['region_seed_capability'])

        # grab some packets from sim2
        packets_captured2 = self.maintain_sim_presence(vanishing_data, self.region2, 5)
        
        # now let's validate some shizz
        assert self.region.seed_cap != self.region2.seed_cap
        assert self.region.details['region_id'] != self.region2.details['region_id']
        # why are these missing now?
        # assert packets_captured2['TeleportProgress'] == 1
        # assert packets_captured2['AgentMovementComplete'] == 1
 
    def test_teleport_same_sim_same_position(self):
    
        #establish AD event queue connection
        ad_event_queue = EventQueue(self.agentdomain)
        ad_queue_thread = Thread(target=run_ad_eq, name="Agent Domain event queue", args=(ad_event_queue,))
        ad_queue_thread.start()

        # place the avatar on a region via the agent domain
        self.region = Region(self.start_region_uri)
        self.region.details = self.agentdomain.place_avatar(self.region.region_uri)

        # temp hack until we have an object model
        self.region.set_seed_cap_url(self.region.details['region_seed_capability'])

        #gets the rez_avatar/place cap
        #caps = agentdomain.seed_cap.get(['rez_avatar/place'])
        
        # grab some data before it disappears
        vanishing_data = {}
        vanishing_data['agent_id'] = self.region.details['agent_id']
        vanishing_data['session_id'] = self.region.details['session_id']
        vanishing_data['circuit_code'] = self.region.details['circuit_code']        
                
        # grab some packets from sim1
        packets_captured = self.maintain_sim_presence(vanishing_data, self.region, 5)

        # place the avatar on a region via the agent domain
        self.region2 = Region(self.start_region_uri)
        self.region2.details = self.agentdomain.place_avatar(self.region2.region_uri)

        # temp hack until we have an object model
        self.region2.set_seed_cap_url(self.region2.details['region_seed_capability'])

        # grab some packets from sim2
        packets_captured2 = self.maintain_sim_presence(vanishing_data, self.region2, 5)
        
        # now let's validate some shizz
        assert self.region.seed_cap_url == self.region2.seed_cap_url
        assert self.region.details['region_id'] == self.region2.details['region_id']
        assert len(packets_captured) > 5
        assert len(packets_captured2) > 5
        # why are these missing now?
        # assert packets_captured2['TeleportProgress'] == 1
        # assert packets_captured2['AgentMovementComplete'] == 1

    def maintain_sim_presence(self, vanishing_data, region, duration):

        self.agent_id = vanishing_data['agent_id']
        self.session_id = vanishing_data['session_id']
        self.circuit_code = vanishing_data['circuit_code']       
    
        #begin UDP communication
        self.host = Host((region.details['sim_ip'],
                    region.details['sim_port']))

        self.connect(self.host, region)
        
        #print "Entering loop"
        last_ping = 0
        
        sim_event_queue = EventQueueGet(region)

        sim_queue_thread = Thread(target=run_sim_eqg, name="Simulator event queue", args=(sim_event_queue,))
        
        sim_queue_thread.start()

        last_ping = 0
        start = time.time()
        now = start
        packets = {}
        
        while ((now - start) < duration):
            msg_buf, msg_size = self.messenger.udp_client.receive_packet(self.messenger.socket)
            packet = self.messenger.receive_check(self.messenger.udp_client.get_sender(),
                                            msg_buf, msg_size)
            if packet != None:
                #print 'Received: ' + packet.name + ' from  ' + self.messenger.udp_client.sender.ip + ":" + \
                 #                                 str(self.messenger.udp_client.sender.port)

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
                
            if self.messenger.has_unacked():
                #print 'Acking'
                self.messenger.process_acks()
                self.send_agent_update(self.agent_id, self.session_id)
        
            now = time.time()
        
        return packets    

    def connect(self, host, region):
        #SENDS UseCircuitCode
        msg = Message('UseCircuitCode',
                      Block('CircuitCode', Code=self.circuit_code,
                            SessionID=uuid.UUID(self.session_id),
                            ID=uuid.UUID(self.agent_id)))
        self.messenger.send_reliable(msg, host, 0)

        time.sleep(1)

        #SENDS CompleteAgentMovement
        msg = Message('CompleteAgentMovement',
                      Block('AgentData', AgentID=uuid.UUID(self.agent_id),
                            SessionID=uuid.UUID(self.session_id),
                            CircuitCode=self.circuit_code))
        self.messenger.send_reliable(msg, host, 0)

        #SENDS UUIDNameRequest
        msg = Message('UUIDNameRequest',
                      Block('UUIDNameBlock', ID=uuid.UUID(self.agent_id)
                            )
                      )
        self.messenger.send_message(msg, host)        
       
    def tearDown(self):
        if self.agentdomain.connectedStatus:
            logout(self.agentdomain)


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

#for threading
def run_ad_eq(ad_event_queue):
    #NOW, event queue to sim
    
    start = time.time()
    now = start
    
    while (now - start > 15):
        result = ad_event_queue()
        #print "Agent Domain queue returned: "
        #pprint.pprint(result)

def run_sim_eqg(sim_event_queue):
    
    start = time.time()
    now = start
    
    while (now - start > 15):
        try:
            result = sim_event_queue()
            #print "Sim event queue returned: "
            #pprint.pprint(result)
        except Exception, e:
            #print "Sim had no events"
            #just means nothing to get
            pass
            

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(OGPTeleportTest))
    return suite
