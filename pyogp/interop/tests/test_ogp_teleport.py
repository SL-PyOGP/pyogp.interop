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

from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base.registration import init

from pyogp.lib.base.interfaces import IPlaceAvatar, IEventQueueGet

from pyogp.lib.base.OGPLogin import OGPLogin
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.interfaces import IHost, IPacket
from pyogp.lib.base.message.types import MsgType

from zope.component import provideUtility
from pyogp.lib.base.network.interfaces import IUDPClient
from pyogp.lib.base.network.net import NetUDPClient

import helpers

class OGPTeleportTest(unittest.TestCase):

    login_uri = None
    start_region_uri = None
    target_region_uri = None

    def setUp(self):
        init() # initialize the framework        
        provideUtility(NetUDPClient(), IUDPClient)

        self.agent_id = ''
        self.session_id = ''

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

    def test_base_teleport(self):
    
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)
        agentdomain = AgentDomain(self.login_uri)

        #gets seedcap, and an agent that can be placed in a region
        agent = agentdomain.login(credentials)

        #establish AD event queue connection
        ad_event_queue = IEventQueueGet(agentdomain)
        ad_queue_thread = Thread(target=run_ad_eq, name="Agent Domain event queue", args=(ad_event_queue,))
        ad_queue_thread.start()
        
        #gets the rez_avatar/place cap
        caps = agentdomain.seed_cap.get(['rez_avatar/place'])
        
        # try and rez on a sim
        region = Region(self.start_region_uri)
        place = IPlaceAvatar(agentdomain)
        avatar = place(region)
        
        # grab some data before it disappears
        vanishing_data = {}
        vanishing_data['agent_id'] = avatar.region.details['agent_id']
        vanishing_data['session_id'] = avatar.region.details['session_id']
        vanishing_data['circuit_code'] = avatar.region.details['circuit_code']        
                
        # grab some packets from sim1
        packets_captured = self.maintain_sim_presence(vanishing_data, region, place, avatar, 5)

        # try and rez on sim2
        region2 = Region(self.target_region_uri)
        place2 = IPlaceAvatar(agentdomain)
        avatar2 = place(region2)

        # grab some packets from sim2
        packets_captured2 = self.maintain_sim_presence(vanishing_data, region2, place2, avatar2, 15)
        
        # now let's validate some shizz
        assert avatar.region.details['region_seed_capability'] != avatar2.region.details['region_seed_capability']
        assert packets_captured2['TeleportProgress'] == 1
        assert packets_captured2['AgentMovementComplete'] == 1
 
    def test_teleport_same_sim(self):
    
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)
        agentdomain = AgentDomain(self.login_uri)

        #gets seedcap, and an agent that can be placed in a region
        agent = agentdomain.login(credentials)

        #establish AD event queue connection
        ad_event_queue = IEventQueueGet(agentdomain)
        ad_queue_thread = Thread(target=run_ad_eq, name="Agent Domain event queue", args=(ad_event_queue,))
        ad_queue_thread.start()
        
        #gets the rez_avatar/place cap
        caps = agentdomain.seed_cap.get(['rez_avatar/place'])
        
        # try and rez on a sim
        region = Region(self.start_region_uri)
        place = IPlaceAvatar(agentdomain)
        avatar = place(region, [5,5,5])
        
        # grab some data before it disappears
        vanishing_data = {}
        vanishing_data['agent_id'] = avatar.region.details['agent_id']
        vanishing_data['session_id'] = avatar.region.details['session_id']
        vanishing_data['circuit_code'] = avatar.region.details['circuit_code']        
                
        # grab some packets from sim1
        packets_captured = self.maintain_sim_presence(vanishing_data, region, place, avatar, 5)

        # try and rez on sim2
        region2 = Region(self.target_region_uri)
        place2 = IPlaceAvatar(agentdomain)
        avatar2 = place(region2, [255,255,255])

        # grab some packets from sim2
        packets_captured2 = self.maintain_sim_presence(vanishing_data, region2, place2, avatar2, 5)
        
        # now let's validate some shizz
        # assert avatar.region.details['region_seed_capability'] != avatar2.region.details['region_seed_capability']
        assert packets_captured2['TeleportProgress'] == 1
        assert packets_captured2['AgentMovementComplete'] == 1       

    def test_teleport_same_sim_position(self):
    
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)
        agentdomain = AgentDomain(self.login_uri)

        #gets seedcap, and an agent that can be placed in a region
        agent = agentdomain.login(credentials)

        #establish AD event queue connection
        ad_event_queue = IEventQueueGet(agentdomain)
        ad_queue_thread = Thread(target=run_ad_eq, name="Agent Domain event queue", args=(ad_event_queue,))
        ad_queue_thread.start()
        
        #gets the rez_avatar/place cap
        caps = agentdomain.seed_cap.get(['rez_avatar/place'])
        
        # try and rez on a sim
        region = Region(self.start_region_uri)
        place = IPlaceAvatar(agentdomain)
        avatar = place(region, [5,5,5])
        
        # grab some data before it disappears
        vanishing_data = {}
        vanishing_data['agent_id'] = avatar.region.details['agent_id']
        vanishing_data['session_id'] = avatar.region.details['session_id']
        vanishing_data['circuit_code'] = avatar.region.details['circuit_code']        
                
        # grab some packets from sim1
        packets_captured = self.maintain_sim_presence(vanishing_data, region, place, avatar, 5)

        # try and rez on sim2
        region2 = Region(self.target_region_uri)
        place2 = IPlaceAvatar(agentdomain)
        avatar2 = place(region2, [5,5,5])

        # grab some packets from sim2
        packets_captured2 = self.maintain_sim_presence(vanishing_data, region2, place2, avatar2, 5)
        
        # now let's validate some shizz
        # assert avatar.region.details['region_seed_capability'] != avatar2.region.details['region_seed_capability']
        assert packets_captured2['TeleportProgress'] == 1
        assert packets_captured2['AgentMovementComplete'] == 1

    def maintain_sim_presence(self, vanishing_data, region, place, avatar, duration):

        self.agent_id = vanishing_data['agent_id']
        self.session_id = vanishing_data['session_id']
        self.circuit_code = vanishing_data['circuit_code']       
    
        #begin UDP communication
        self.host = IHost((avatar.region.details['sim_ip'],
                    avatar.region.details['sim_port']))

        self.connect(self.host, avatar.region)
        
        #print "Entering loop"
        last_ping = 0
        
        sim_event_queue = IEventQueueGet(region)

        sim_queue_thread = Thread(target=run_sim_eqg, name="Agent Domain event queue", args=(sim_event_queue,))
        
        sim_queue_thread.start()

        last_ping = 0
        start = time.time()
        now = start
        packets = {}
        
        while ((now - start) < 15):
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
