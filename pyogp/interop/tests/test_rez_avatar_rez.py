#!/usr/bin/python

import unittest
from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability


## Globals to share with other tests
agent_id = '3d2b8256-12cd-40fd-abf8-6da4ad6739a2'
dest_regionuri = 'http://sim2.vaak.lindenlab.com:12035'
#  http://sim2.vaak.lindenlab.com:12035/agent/(uuid)/rez_avatar/rez
rez_avatar_url = dest_regionuri + '/agent/' + agent_id + '/rez_avatar/rez?agent_id=' + agent_id + '&allow_redirect=true&god_level=200&god_override&identified=&limited_to_estate=1&transacted='

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

class RezAvatarRezTests(unittest.TestCase):

    def setUp(self):
        init()
        self.default_arguments = default_rez_arguments
        self.capability = Capability('rez_avatar/rez', rez_avatar_url)

    def tearDown(self):
        pass
    
    def postToCap(self, arguments):
        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            print 'Exception: ' + e.message + ' ' + str(e.args)
            return

        return result

    
    def check_response_base(self, result):
        """ check for the eistence of the correct parameters in the cap response """

        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position'))

        self.assert_(result['position'][0] < 256)
        self.assert_(result['position'][1] < 256)
        self.assert_(result['position'][2] < 256)


    def test_rez_avatar_rez_connect(self):
        """ agent is allowed to rez """

        result = self.postToCap(self.default_arguments)

        self.check_response_base(result)
        self.assertEquals(result['connect'], True)

    def test_rez_avatar_rez_position(self):
        """ verify position values are within range """

        result = self.postToCap(self.default_arguments)

        self.check_response_base(result)
        
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarRezTests))
    return suite

