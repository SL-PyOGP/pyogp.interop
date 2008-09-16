import unittest, doctest
import ConfigParser
from pkg_resources import resource_stream
import time
import uuid
import pprint

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
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))

        # global test attributes
        self.login_uri = config.get('test_ogpteleport_setup', 'login_uri')
        self.start_region_uri = config.get('test_ogpteleport_setup', 'start_region_uri')

        # test_base_login attributes
        self.target_region_uri = config.get('test_base_teleport', 'target_region_uri')
        self.base_firstname = config.get('test_base_teleport', 'firstname')
        self.base_lastname = config.get('test_base_teleport', 'lastname')
        self.base_password = config.get('test_base_teleport', 'password')
        #don't need a port, not sure why we have it there yet
        self.messenger = UDPDispatcher()
        self.host = None

    def test_base_teleport(self):
    
        credentials = PlainPasswordCredential(self.base_firstname, self.base_lastname, self.base_password)
        agentdomain = AgentDomain(self.login_uri)

        #gets seedcap, and an agent that can be placed in a region
        agent = agentdomain.login(credentials)
        assert agentdomain.seed_cap != None or agentdomain.seed_cap != {}, "Login to agent domain failed"

        #gets the rez_avatar/place cap
        caps = agentdomain.seed_cap.get(['rez_avatar/place'])
        
        assert caps['rez_avatar/place'] != None or caps['rez_avatar/place'] != {}, "Failed to retrieve the rez_avatar/place capability"
       
        # try and connect to a sim
        region = Region(self.start_region_uri)
        place = IPlaceAvatar(agentdomain)
        
        avatar = place(region)

        assert avatar.region.details['seed_capability'] != None or avatar.region.details['seed_capability'] != {}, "Rez_avatar/place returned no seed cap"
        assert avatar.region.details['look_at'] != None or avatar.region.details['look_at'] != {}, "Rez_avatar/place returned no look_at"
        assert avatar.region.details['sim_ip'] != None or avatar.region.details['sim_ip'] != {}, "Rez_avatar/place returned no sim_ip"
        assert avatar.region.details['sim_port'] != None or avatar.region.details['sim_port'] != {}, "Rez_avatar/place returned no sim_port"
        assert avatar.region.details['region_x'] != None or avatar.region.details['region_x'] != {}, "Rez_avatar/place returned no region_x"
        assert avatar.region.details['region_y'] != None or avatar.region.details['region_y'] != {}, "Rez_avatar/place returned no region_y"
        assert avatar.region.details['region_id'] != None or avatar.region.details['region_id'] != {}, "Rez_avatar/place returned no region_id"
        assert avatar.region.details['sim_access'] != None or avatar.region.details['sim_access'] != {}, "Rez_avatar/place returned no sim_access"
        assert avatar.region.details['connect'] != None or avatar.region.details['connect'] != {}, "Rez_avatar/place returned no connect"
        assert avatar.region.details['position'] != None or avatar.region.details['position'] != {}, "Rez_avatar/place returned no position"
        assert avatar.region.details['session_id'] != None or avatar.region.details['session_id'] != {}, "Rez_avatar/place returned no session_id"
        assert avatar.region.details['secure_session_id'] != None or avatar.region.details['secure_session_id'] != {}, "Rez_avatar/place returned no secure_session_id" 
        assert avatar.region.details['circuit_code'] != None or avatar.region.details['circuit_code'] != {}, "Rez_avatar/place returned no cicuit_code"

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
        self.messenger.send_reliable(IPacket(msg), self.host, 0)

        time.sleep(1)

        #SENDS CompleteAgentMovement
        msg = Message('CompleteAgentMovement',
                      Block('AgentData', AgentID=uuid.UUID(self.agent_id),
                            SessionID=uuid.UUID(self.session_id),
                            CircuitCode=avatar.region.details['circuit_code']))
        self.messenger.send_reliable(IPacket(msg), self.host, 0)

        #SENDS UUIDNameRequest
        msg = Message('UUIDNameRequest',
                      Block('UUIDNameBlock', ID=uuid.UUID(self.agent_id)
                            )
                      )
        self.messenger.send_message(IPacket(msg), self.host)

        print "Entering loop"
        last_ping = 0
        ad_event_queue = IEventQueueGet(agentdomain)
        sim_event_queue = IEventQueueGet(region)

        from threading import Thread
        ad_queue_thread = Thread(target=run_ad_eq, name="Agent Domain event queue", args=(ad_event_queue,))
        sim_queue_thread = Thread(target=run_sim_eqg, name="Agent Domain event queue", args=(sim_event_queue,))
        ad_queue_thread.start()
        sim_queue_thread.start()

        print "Entering loop"
        last_ping = 0
        while True:
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
                
            else:
                print 'No message'
                
        if self.messenger.has_unacked():
                print 'Acking'
                self.messenger.process_acks()
                self.send_agent_update(self.agent_id, self.session_id)
       
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
    while True:
        result = ad_event_queue()
        print "Agent Domain queue returned: "
        pprint.pprint(result)

def run_sim_eqg(sim_event_queue):
    while True:
        try:
            result = sim_event_queue()
            print "Sim event queue returned: "
            pprint.pprint(result)
        except Exception, e:
            print "Sim had no events"
            #just means nothing to get
            pass
            

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(OGPTeleportTest))
    return suite
