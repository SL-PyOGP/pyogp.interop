"""
@file test_chat.py
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
try:
    import msvcrt #WINDOWS ONLY!
    canInput = True
except:
    print "Trying to import a windows library"
    canInput = False

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
import teleport_region

#import Tkinter
#root = Tkinter.Tk()
import chat_window

globals()["controlFlags"] = 0x00000000
globals()["agentFlagSent"] = 0x00000000
#global controlFlags = 0x00000000
#global agentFlagSent = controlFlags

STOP_MOVING = 0x00004000

NUDGE_FORWARD = 0x00080000
NUDGE_BACKWARD = 0x00100000
NUDGE_LEFT = 0x00200000
NUDGE_RIGHT = 0x00400000

MOVE_FORWARD = 0x00000001 | 0x00000400
MOVE_BACKWARD = 0x00000002 | 0x00000400
MOVE_LEFT = 0x00000004 | 0x00000800
MOVE_RIGHT = 0x00000001 | 0x00000008

#globals()["chat_window"] = chat_window.ChatWindow()
globals()["message_list"] = []

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
        print 'Logging in'
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

        assert avatar.region.details['region_seed_capability'] != None or avatar.region.details['region_seed_capability'] != {}, "Rez_avatar/place returned no seed cap"
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
        self.circuit_code = avatar.region.details['circuit_code']
        
        #begin UDP communication
        self.host = IHost((avatar.region.details['sim_ip'],
                    avatar.region.details['sim_port']))

        print "CONNECTING"

        self.connect(self.host, avatar.region)
        last_ping = 0
        ad_event_queue = IEventQueueGet(agentdomain)
        sim_event_queue = IEventQueueGet(region)

        from threading import Thread
        ad_queue_thread = Thread(target=run_ad_eq, name="Agent Domain event queue", args=(ad_event_queue,))
        sim_queue_thread = Thread(target=run_sim_eqg, name="Agent Domain event queue", args=(sim_event_queue,))
        if canInput == True:
            input_thread = Thread(target=run_input_check, name="Thread to handle input", args=(self, agentdomain))
            input_thread.start()
        ad_queue_thread.start()
        sim_queue_thread.start()
        
        last_time = time.time()
        update_count = 0
        self.cw = chat_window.ChatWindow()
        self.cw.set_enter_hit(self.text_entered)
        self.cw.update()
        
        print "DONE MAIN LOOP"
        
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
                elif packet.name == 'ChatFromSimulator':
                    print 'CHAT: ' + repr(msg_buf)
                    self.handle_chat_message(packet)                    

            if self.messenger.has_unacked():
                self.messenger.process_acks()
    
            current_time = time.time()
            if current_time - last_time >= 1:
                update_count = 0
    
            #update 10 times a second max
            if update_count < 10: 
                update_count += 1
                self.send_agent_update(self.agent_id, self.session_id, globals()["controlFlags"])
                globals()["agentFlagSent"] = globals()["controlFlags"]

            if len(globals()["message_list"]) > 0:
                for message in globals()["message_list"]:
                    self.cw.write(message)
                globals()["message_list"] = []

            self.cw.update()

    def text_entered(self, event=None):
        chat_message = self.cw.hit_enter()
        self.send_chat_message(self.host,
                               self.agent_id,
                               self.session_id,
                               chat_message)

    def handle_chat_message(self, packet):
        print "--------------Chat type-----------: " + str(packet.message_data.blocks['ChatData'][0].vars['ChatType'].data)
        print "--------------Audible-----------: " + str(packet.message_data.blocks['ChatData'][0].vars['Audible'].data)
        print "FROM: " + str(packet.message_data.blocks['ChatData'][0].vars['FromName'].data)
        print "MESSAGE: " + str(packet.message_data.blocks['ChatData'][0].vars['Message'].data)
        from_user = packet.message_data.blocks['ChatData'][0].vars['FromName'].data
        chat_msg = packet.message_data.blocks['ChatData'][0].vars['Message'].data
        if not chat_msg.isspace() and chat_msg != '\n' and chat_msg != None and chat_msg != '' and chat_msg != ' ':
            message = from_user + ': ' + chat_msg + '\n'
            print "Chat message: " + repr(message)
            self.cw.write(message.replace("\x00", ""))

    def send_chat_message(self, host, agent_id, session_id, message):
        message = message + '\x00' #add null-terminator onto the end
        print 'Sending Message: ' + message
        msg = Message('ChatFromViewer',
                      Block('AgentData', AgentID=uuid.UUID(agent_id),
                            SessionID=uuid.UUID(self.session_id)),
                       Block('ChatData', Message=message, Type=1, Channel=0))

        self.messenger.send_message(msg, host)
        #globals()["message_list"].append('You: ' + message + '\n')
        
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
        self.host = host
       
    def tearDown(self):
        msg = Message('LogoutRequest',
                      Block('AgentData', AgentID=uuid.UUID(self.agent_id),
                            SessionID=uuid.UUID(self.session_id)
                            )
                      )
        self.messenger.send_message(msg, self.host)

    def send_agent_update(self, agent_id, session_id, control_flag):
        msg = Message('AgentUpdate',
                      Block('AgentData', AgentID=uuid.UUID(agent_id),
                            SessionID=uuid.UUID(self.session_id),
                            BodyRotation=(0.0,0.0,0.0),
                            HeadRotation=(0.0,0.0,0.0),
                            State=0x00,
                            CameraCenter=(0.0,0.0,0.0),
                            CameraAtAxis=(1.0,0.0,0.0),
                            CameraLeftAxis=(0.0,1.0,0.0),
                            CameraUpAxis=(0.0,0.0,1.0),
                            Far=1.0,
                            ControlFlags=control_flag,
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

def run_input_check(teleporter, agentdomain):
    host = teleporter.host
    
    while True:
        print "------------WAITINF FOR KEY PRESS---------------"
        #wait til press
        while not msvcrt.kbhit():
            pass

        print "------------GOT KEY PRESS---------------"

        c = msvcrt.getch()
        if c == '\xe0':
            kk = msvcrt.getch()
            if kk == 'H':
                if globals()["agentFlagSent"] != NUDGE_FORWARD:
                    print 'NUDGING FORWARD'
                    globals()["controlFlags"] = NUDGE_FORWARD
                else:
                    print 'MOVE UP'
                    globals()["controlFlags"] = MOVE_FORWARD
            elif kk == 'P':
                print 'MOVE DOWN'
                if globals()["agentFlagSent"] != NUDGE_BACKWARD:
                    globals()["controlFlags"] = NUDGE_BACKWARD
                else:
                    globals()["controlFlags"] = MOVE_BACKWARD
            elif kk == 'K':
                print 'MOVE LEFT'
                if globals()["agentFlagSent"] != NUDGE_LEFT:
                    globals()["controlFlags"] = NUDGE_LEFT
                else:
                    globals()["controlFlags"] = MOVE_LEFT
            elif kk == 'M':
                print 'MOVE RIGHT'
                if globals()["agentFlagSent"] != NUDGE_RIGHT:
                    globals()["controlFlags"] = NUDGE_RIGHT
                else:
                    globals()["controlFlags"] = MOVE_RIGHT
                
            print kk
        else:
            #SPACE HALTS THE AGENT
            if c == ' ':
                globals()["controlFlags"] = STOP_MOVING
            elif c == 't':
                print 'TELEPORTING'
                reload(teleport_region)
                #READ THE TARGET REGION URL from a file
                tp_region = Region(teleport_region.region)
                place = IPlaceAvatar(agentdomain)

                avatar = place(tp_region, teleport_region.position)        

                host = IHost((avatar.region.details['sim_ip'],
                            avatar.region.details['sim_port']))                

                teleporter.connect(host, avatar.region)
            elif c == 'u':
                pass
                #reload(teleport_region)
                #cw = globals()["chat_window"]
                """teleporter.send_chat_message(host,
                                             teleporter.agent_id,
                                             teleporter.session_id,
                                             teleport_region.chat)"""
            print repr(c)    
            

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(OGPTeleportTest))
    return suite
