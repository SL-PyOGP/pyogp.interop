#!/usr/bin/python

import unittest
from indra.ipc import llsdhttp
from indra.base import lluuid

## Globals to share with other tests
agent_id = '3d2b8256-12cd-40fd-abf8-6da4ad6739a2'
dest_regionuri = 'http://sim2.vaak.lindenlab.com:12035'
#  http://sim2.vaak.lindenlab.com:12035/agent/(uuid)/rez_avatar/rez
rez_avatar_url = dest_regionuri + '/agent/' + agent_id + '/rez_avatar/rez?agent_id=' + agent_id + '&allow_redirect=true&god_level=200&god_override&identified=&limited_to_estate=1&transacted='

#    <llsd><map><key>agent_id</key><string>203ad6df-b522-491d-ba48-4e24eb57aeff</
#    string><key>allow_redirect</key><string>true</string><key>animations</key><undef /><key>attachment_data</key><undef /><key>baked_textrue_data</key><undef /><key
#    >circuit_code</key><integer>274880050</integer><key>god_level</key><string>200</string><key>god_override</key><boolean>0</boolean><key>identified</key><string /
#    ><key>inventory_host</key><string>inv4.mysql.agni.lindenlab.com</string><key>limited_to_estate</key><string>1</string><key>position</key><array><real>128</real>
#    <real>128</real><real>128</real></array><key>secure_session_id</key><string>4cf1176e-457c-11dd-8b4c-0050455c6ada</string><key>session_id</key><string>4cf1124f-4
#    57c-11dd-b037-0050455c6ada</string><key>texture_data</key><undef /><key>transacted</key><string /><key>voice_password</key><undef /></map></llsd>
default_rez_arguments={
    'circuit_code': 274880050,
    'god_overide': False,
    'position': [128, 128, 128],
    'secure_session_id': '4cf1176e-457c-11dd-8b4c-0050455c6ada',
    'session_id': '4cf1124f-457c-11dd-b037-0050455c6ada',
    'inventory_host': 'inv4.mysql.agni.lindenlab.com', # not really here!
    'voice_password': None,
    
    # The following are only sent from simulator a -> simulator b via derez_avatar
    'attachment_data': None, # [ {'attachment_point':<int>, 'item_id':<uuid>, 'asset_id':<uuid> | 'asset_data':<binary>}...]
    'baked_texture_data': None, #[ {'texture_id':<uuid>, 'asset_host_name':<host?????>}...]
    'texture_data': None, # [ <uuid>...]
    'animations': None #[{'state':<uuid>, 'source':<uuid>, 'sequence':<int>}...]
    }

def rez_avatar(url=rez_avatar_url, arguments=default_rez_arguments):
    return llsdhttp.post(rez_avatar_url, arguments)

class RezAvatarTests(unittest.TestCase):
    def check_successful_response(self, arguments):
        print "ARGs", arguments
        result = rez_avatar(arguments=arguments)
        print "RESULT", result
        # check for existence of fields
        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position'))

        self.assertEquals(result['connect'], True)
        self.assert_(result['position'][0] < 256)
        self.assert_(result['position'][1] < 256)
        self.assert_(result['position'][2] < 256)

    def check_failure_response(self, arguments):
        print "ARGs", arguments
        try:
            result = rez_avatar(arguments=arguments)
            print "RESULT", result
        except Exception, e:
            # supposed to be error
            return

        self.assertEquals(result['connect'], False)

    def test0_default_rez(self):
        self.check_successful_response(default_rez_arguments)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarTests))
    return suite

