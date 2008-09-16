import unittest, doctest
import ConfigParser
from pkg_resources import resource_stream
import time
import uuid

from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base.registration import init

from pyogp.lib.base.interfaces import IPlaceAvatar

from pyogp.lib.base.OGPLogin import OGPLogin
from pyogp.lib.base.message.udpdispatcher import UDPDispatcher
from pyogp.lib.base.message.message import Message, Block
from pyogp.lib.base.message.interfaces import IHost
from pyogp.lib.base.message.types import MsgType

from zope.component import provideUtility
from pyogp.lib.base.network.interfaces import IUDPClient
from pyogp.lib.base.network.net import NetUDPClient

import helpers

class OGPPresenceTest(unittest.TestCase):

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
                
        test_setup_config_name = 'test_interop_account'
        
        self.firstname = config.get(test_setup_config_name, 'firstname')
        self.lastname = config.get(test_setup_config_name, 'lastname')
        self.password = config.get(test_setup_config_name, 'password')
        self.login_uri = config.get(test_setup_config_name, 'login_uri')        
        self.start_region_uri = config.get('test_interop_regions', 'start_region_uri')        
        
        #don't need a port, not sure why we have it there yet
        self.messenger = UDPDispatcher()
        self.host = None

    def test_base_presence(self):
    
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)
        agentdomain = AgentDomain(self.login_uri)

        #gets seedcap, and an agent that can be placed in a region
        agent = agentdomain.login(credentials)
        assert agentdomain.seed_cap != None or agentdomain.seed_cap != {}, "Login to agent domain failed"

        #gets the rez_avatar/place cap
        caps = agentdomain.seed_cap.get(['rez_avatar/place'])
        
        # try and connect to a sim
        region = Region(self.start_region_uri)
        place = IPlaceAvatar(agentdomain)
        
        avatar = place(region)

        self.agent_id = avatar.region.details['agent_id']
        self.session_id = avatar.region.details['session_id']
        
        #begin UDP communication
        self.host = IHost((avatar.region.details['sim_ip'],
                    avatar.region.details['sim_port']))

        #SENDS UseCircuitCode
        msg = Message('UseCircuitCode',
                      Block('CircuitCode', Code=avatar.region.details['circuit_code'],
                            SessionID=uuid.UUID(self.session_id),
                            ID=uuid.UUID(self.agent_id)))
        self.messenger.send_reliable(msg, self.host, 0)

        time.sleep(1)

        #SENDS CompleteAgentMovement
        msg = Message('CompleteAgentMovement',
                      Block('AgentData', AgentID=uuid.UUID(self.agent_id),
                            SessionID=uuid.UUID(self.session_id),
                            CircuitCode=avatar.region.details['circuit_code']))
        self.messenger.send_reliable(msg, self.host, 0)

        #SENDS UUIDNameRequest
        msg = Message('UUIDNameRequest',
                      Block('UUIDNameBlock', ID=uuid.UUID(self.agent_id)
                            )
                      )
        self.messenger.send_message(msg, self.host)

        #print "Entering loop"
        last_ping = 0
        start = time.time()
        now = start
        packets = {}
        
        # run for 45 seonds
        while ((now - start) < 15):
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
                #print 'No message'
                pass
                
            now = time.time()
                
        if self.messenger.has_unacked():
                #print 'Acking'
                self.messenger.process_acks()
                self.send_agent_update(self.agent_id, self.session_id)

        # let's test something to prove presence on the sim

        assert avatar.region.details['seed_capability'] != None or avatar.region.details['seed_capability'] != {}, "Rez_avatar/place returned no seed cap"
        assert len(packets) > 0
        self.assertNotEqual(last_ping, 0)
        self.assert_("CoarseLocationUpdate" in packets)
        self.assert_("StartPingCheck" in packets) 
        self.assert_("AgentDataUpdate" in packets) 
        
        print str(packets)
       
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

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(OGPPresenceTest))
    return suite
