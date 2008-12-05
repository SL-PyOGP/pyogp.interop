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
from pyogp.lib.base.agentdomain import AgentDomain, EventQueue
from pyogp.lib.base.regiondomain import Region, EventQueueGet

from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.circuit import Host
from pyogp.lib.base.message.types import MsgType

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
        self.login_uri = "https://login.agni.lindenlab.com/cgi-bin/login.cgi"        
        self.region_uri = self.config.get('test_interop_regions', 'start_region_uri') 

        self.host = None

    def tearDown(self):
        
        pass
        
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
        agent.login(self.login_uri, regionname='uri:Hazzard County&128&128&128')

        assert agent.region.details['seed_capability'] != None or agent.region.details['seed_capability'] != {}, "No Sim seed cap returned in the login response"
        assert agent.region.details['look_at'] != None or agent.region.details['look_at'] != {}, "Login response returned no look_at"
        assert agent.region.details['sim_ip'] != None or agent.region.details['sim_ip'] != {}, "Login response returned no sim_ip"
        assert agent.region.details['sim_port'] != None or agent.region.details['sim_port'] != {}, "Login response returned no sim_port"
        assert agent.region.details['region_x'] != None or agent.region.details['region_x'] != {}, "Login response returned no region_x"
        assert agent.region.details['region_y'] != None or agent.region.details['region_y'] != {}, "Login response returned no region_y"
        assert agent.region.details['login'] != None or agent.region.details['login'] != {}, "Login response returned no connect"
        assert agent.region.details['session_id'] != None or agent.region.details['session_id'] != {}, "Login response returned no session_id"
        assert agent.region.details['secure_session_id'] != None or agent.region.details['secure_session_id'] != {}, "Login response returned no secure_session_id"
        assert agent.region.details['circuit_code'] != None or agent.region.details['circuit_code'] != {}, "Login response returned no cicuit_code"
        assert agent.region.details['first_name'] != None or agent.region.details['circuit_code'] != {}, "Login response returned no cicuit_code"
        assert agent.region.details['last_name'] != None or agent.region.details['last_name'] != {}, "Login response returned no cicuit_code"
        assert agent.region.details['agent_access'] != None or agent.region.details['agent_access'] != {}, "Login response returned no cicuit_code"

        # need to match up tests with the following attributes
        ''' Sample response:
        {'region_y': 248576, 'region_x': 260096, 'first_name': '"EnusBot17"', 'secure_session_id': '73e6a36a-0144-4eb2-97f7-7d5404367fa1', 'sim_ip': '64.154.221.57', 'agent_access': 'M', 'circuit_code': 492367610, 'look_at': '[r0,r1,r0]', 'session_id': '913ceb6b-0460-47d0-a3bc-a3554d2c36e7', 'last_name': 'LLQABot', 'agent_id': '2894a6f4-e565-42dd-8921-8d97bcbc26b2', 'seed_capability': 'https://sim371.agni.lindenlab.com:12043/cap/2344ce21-dfc3-aa8b-154b-1dfe4d71657f', 'inventory_host': 'inv15-mysql', 'start_location': 'url', 'sim_port': 13000, 'message': 'Looking for cool places to explore and fun things to do inworld? Check out the *Showcase* at Secondlife.com/Showcase', 'login': 'true', 'seconds_since_epoch': 1222243662}

OGP response:   
{'region_y': 256512, 'region_x': 255488, 'agent_id': '2894a6f4-e565-42dd-8921-8d97bcbc26b2', 'secure_session_id': 'dea1f833-8a11-11dd-9d78-005045bbaee2', 'region_id': 31b166cf-9339-04b8-e186-f357724daae3, 'position': [117.0, 73.0, 21.0], 'sim_ip': '8.4.131.62', 'look_at': [0.0, 0.0, 0.0], 'session_id': 'dea1f563-8a11-11dd-888e-005045bbaee2', 'rez_agent/rez': None, 'region_seed_capability': 'https://sim1.vaak.lindenlab.com:12043/cap/76285bf1-41ed-d373-c342-e195d912dd9f', 'sim_access': 'PG', 'connect': True, 'sim_host': '8.4.131.62', 'circuit_code': 406235137, 'sim_port': 13000, 'seed_capability': 'https://sim1.vaak.lindenlab.com:12043/cap/76285bf1-41ed-d373-c342-e195d912dd9f'}

        '''

        #self.host = None
        self.messenger = UDPDispatcher()
        self.agent_id = agent.region.details['agent_id']
        self.session_id = agent.region.details['session_id']
        
        #begin UDP communication
        self.host = Host((agent.region.details['sim_ip'],
                    int(agent.region.details['sim_port'])))

        #SENDS UseCircuitCode
        msg = Message('UseCircuitCode',
                      Block('CircuitCode', Code=agent.region.details['circuit_code'],
                            SessionID=uuid.UUID(self.session_id),
                            ID=uuid.UUID(self.agent_id)))
        self.messenger.send_reliable(msg, self.host, 0)

        time.sleep(1)

        #SENDS CompleteAgentMovement
        msg = Message('CompleteAgentMovement',
                      Block('AgentData', AgentID=uuid.UUID(self.agent_id),
                            SessionID=uuid.UUID(self.session_id),
                            CircuitCode=agent.region.details['circuit_code']))
        self.messenger.send_reliable(msg, self.host, 0)

        #SENDS UUIDNameRequest
        msg = Message('UUIDNameRequest',
                      Block('UUIDNameBlock', ID=uuid.UUID(self.agent_id)
                            )
                      )
        self.messenger.send_message(msg, self.host)

        last_ping_eq = 0
        start_eq = time.time()
        now_eq = start_eq
        packets_eq = {}

        sim_event_queue = EventQueueGet(agent.region)

        from threading import Thread
        sim_queue_thread = Thread(target=run_sim_eqg, name="sim event queue", args=(sim_event_queue,))
        sim_queue_thread.start()

        last_ping = 0
        start = time.time()
        now = start
        packets = {}
        
        while ((now - start) < 60):
            msg_buf, msg_size = self.messenger.udp_client.receive_packet(self.messenger.socket)
            packet = self.messenger.receive_check(self.messenger.udp_client.get_sender(),
                                            msg_buf, msg_size)
            if packet != None:
                print 'Received: ' + packet.name + ' from  ' + self.messenger.udp_client.sender.ip + ":" + \
                                                  str(self.messenger.udp_client.sender.port)

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
                print 'No message'
                
            if self.messenger.has_unacked():
                print 'Acking'
                self.messenger.process_acks()
                self.send_agent_update(self.agent_id, self.session_id)
        
            now = time.time()
       
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

# for threading
def run_sim_eqg(sim_event_queue):

    # run for 60 seconds
    start = time.time()
    now = start
    
    while ((now - start) < 60):
        try:
            result = sim_event_queue()
            #print 'SIM EQ: %s' % result
        except Exception, e:
            #print "Sim had no events"
            #just means nothing to get
            pass
               
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(AuthLegacyLoginTest))
    return suite
