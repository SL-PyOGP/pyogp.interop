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
from pyogp.lib.base.message.message_system import MessageSystem
from pyogp.lib.base.message.circuitdata import Host
from pyogp.lib.base.message.message_types import MsgType

from zope.component import provideUtility
from pyogp.lib.base.network.interfaces import IUDPClient
from pyogp.lib.base.network.net import NetUDPClient

provideUtility(NetUDPClient(), IUDPClient)

class OGPTeleportTest(unittest.TestCase):

    login_uri = None
    start_region_uri = None
    target_region_uri = None

    def setUp(self):
        init() # initialize the framework        

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
        self.messenger = MessageSystem(None)
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
        self.host = Host(avatar.region.details['sim_ip'],
                    avatar.region.details['sim_port'])

        #SENDS UseCircuitCode
        self.messenger.new_message("UseCircuitCode")
        self.messenger.next_block("CircuitCode")
        self.messenger.add_data('Code', avatar.region.details['circuit_code'], \
                                MsgType.MVT_U32)
        self.messenger.add_data('SessionID', \
                                uuid.UUID(self.session_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.add_data('ID', \
                                uuid.UUID(self.agent_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.send_reliable(self.host, 0)

        time.sleep(1)

        #SENDS CompleteAgentMovement
        self.messenger.new_message("CompleteAgentMovement")
        self.messenger.next_block("AgentData")
        self.messenger.add_data('AgentID', \
                                uuid.UUID(self.agent_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.add_data('SessionID', \
                                uuid.UUID(self.session_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.add_data('CircuitCode', avatar.region.details['circuit_code'], \
                                MsgType.MVT_U32)
        self.messenger.send_reliable(self.host, 0)

        #SENDS UUIDNameRequest
        self.messenger.new_message("UUIDNameRequest")
        self.messenger.next_block("UUIDNameBlock")
        self.messenger.add_data("ID", \
                                uuid.UUID(self.agent_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.send_message(self.host)

        #SENDS AgentDataUpdateRequest
        self.messenger.new_message("AgentDataUpdateRequest")
        self.messenger.next_block("AgentData")
        self.messenger.add_data('AgentID', \
                                uuid.UUID(self.agent_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.add_data('SessionID', \
                                uuid.UUID(self.session_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.send_message(self.host)

        print "Entering loop"
        last_ping = 0
        ad_event_queue = IEventQueueGet(agentdomain)
        sim_event_queue = IEventQueueGet(region)

        from threading import Thread
        ad_queue_thread = Thread(target=run_ad_eq, name="Agent Domain event queue", args=(ad_event_queue,))
        sim_queue_thread = Thread(target=run_sim_eqg, name="Agent Domain event queue", args=(sim_event_queue,))
        ad_queue_thread.start()
        sim_queue_thread.start()
        
        last_time = time.time()
        update_count = 0
        while True:
            recv_message = ''
            if self.messenger.receive_check() == True:
                recv_message = self.messenger.reader.current_msg
                """print 'Received: ' + recv_message.name + ' from  ' + self.messenger.udp_client.sender.ip + ":" + \
                                                  str(self.messenger.udp_client.sender.port)"""

                #MESSAGE HANDLERS
                if recv_message.name == 'RegionHandshake':
                    self.send_region_handshake_reply(self.agent_id, self.session_id)
                elif recv_message.name == 'StartPingCheck':
                    self.send_complete_ping_check(last_ping)
                    last_ping += 1                    
                
            else:
                print 'No message'

            if self.messenger.has_unacked():
                print 'Acking'
                self.messenger.process_acks()
    
            current_time = time.time()
            if current_time - last_time >= 1:
                update_count = 0
    
            #update 10 times a second max
            if update_count < 10: 
                update_count += 1
                self.send_agent_update(self.agent_id, self.session_id)
       
    def tearDown(self):
        # essentially logout by deleting presence... etc.
        self.messenger.new_message("LogoutRequest")
        self.messenger.next_block("AgentData")
        self.messenger.add_data('AgentID', \
                                uuid.UUID(self.agent_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.add_data('SessionID', \
                                uuid.UUID(self.session_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.send_message(self.host)

    def send_agent_update(self, agent_id, session_id):
        self.messenger.new_message("AgentUpdate")
        self.messenger.next_block("AgentData")
        self.messenger.add_data('AgentID', \
                                uuid.UUID(agent_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.add_data('SessionID', \
                                uuid.UUID(session_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.add_data('BodyRotation', \
                                (0.0,0.0,0.0,0.0), \
                                MsgType.MVT_LLQuaternion)
        self.messenger.add_data('HeadRotation', \
                                (0.0,0.0,0.0,0.0), \
                                MsgType.MVT_LLQuaternion)
        self.messenger.add_data('State', \
                                0x00, \
                                MsgType.MVT_U8)
        self.messenger.add_data('CameraCenter', \
                                (0.0,0.0,0.0), \
                                MsgType.MVT_LLVector3)
        self.messenger.add_data('CameraAtAxis', \
                                (0.0,0.0,0.0), \
                                MsgType.MVT_LLVector3)
        self.messenger.add_data('CameraLeftAxis', \
                                (0.0,0.0,0.0), \
                                MsgType.MVT_LLVector3)
        self.messenger.add_data('CameraUpAxis', \
                                (0.0,0.0,0.0), \
                                MsgType.MVT_LLVector3)
        self.messenger.add_data('Far', \
                                0.0, \
                                MsgType.MVT_F32)
        self.messenger.add_data('ControlFlags', \
                                0x00, \
                                MsgType.MVT_U32)
        self.messenger.add_data('Flags', \
                                0x00, \
                                MsgType.MVT_U8)
        self.messenger.send_message(self.host)

    def send_region_handshake_reply(self, agent_id, session_id):
        self.messenger.new_message("RegionHandshakeReply")
        self.messenger.next_block("AgentData")
        self.messenger.add_data('AgentID', \
                                uuid.UUID(agent_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.add_data('SessionID', \
                                uuid.UUID(session_id), \
                                MsgType.MVT_LLUUID)
        self.messenger.next_block("RegionInfo")
        self.messenger.add_data('Flags', \
                                0x00, \
                                MsgType.MVT_U32)
        self.messenger.send_message(self.host)
    
    def send_complete_ping_check(self, ping):
        self.messenger.new_message("CompletePingCheck")
        self.messenger.next_block("PingID")
        self.messenger.add_data('PingID', \
                                ping, \
                                MsgType.MVT_U8)
        self.messenger.send_message(self.host)

#for threading
def run_ad_eq(ad_event_queue):
    #NOW, event queue to sim
    while True:
        result = ad_event_queue()
        print "Agent Domain queue returned: "
        pprint.pprint(result)

def run_sim_eqg(sim_event_queue):
    while True:
        result = sim_event_queue()
        print "Sim event queue returned: "
        pprint.pprint(result)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(OGPTeleportTest))
    return suite
