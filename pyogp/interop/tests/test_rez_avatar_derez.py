#!/usr/bin/python

import unittest, time
from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

## Globals to share with other tests
agent_id = '3d2b8256-12cd-40fd-abf8-6da4ad6739a2'
dest_regionuri = 'http://sim2.vaak.lindenlab.com:12035'
#  http://sim2.vaak.lindenlab.com:12035/agent/(uuid)/rez_avatar/rez
rez_avatar_url = dest_regionuri + '/agent/' + agent_id + '/rez_avatar/rez?agent_id=' + agent_id + '&allow_redirect=true&god_level=200&god_override&identified=&limited_to_estate=1&transacted='

source_regionuri = 'http://sim2.vaak.lindenlab.com:12035'

#  http://sim2.vaak.lindenlab.com:12035/agent/(uuid)/rez_avatar/derez
## TODO: should be rez_avatar/derez
derez_avatar_url = source_regionuri + '/agent/' + agent_id + '/rez_avatar/derez'
#derez_avatar_url = source_regionuri + '/agent/' + agent_id + '/derez_avatar'
default_derez_arguments={
    'rez_avatar': rez_avatar_url,
    'position': [0,0,0]
}

class RezAvatarDerezTest(unittest.TestCase):

    def setUp(self):
        init()
        self.default_arguments = default_derez_arguments
        self.capability = Capability('rez_avatar/derez', derez_avatar_url)

    def tearDown(self):
        pass


    def postToCap(self, arguments):
        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            print 'Exception: ' + e.message + ' ' + str(e.args)
            return

        return result


    def check_response_base(self, results):
        """ check the the existence of the correct parameters in the cap response """
        
        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position'))

        self.assertEquals(result['connect'], True)
        self.assert_(result['position'][0] < 256)
        self.assert_(result['position'][1] < 256)
        self.assert_(result['position'][2] < 256)

    def test_rez_avatar_derez_connect(self):
        """ agent is allowed to derez """

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
    suite.addTest(makeSuite(RezAvatarDerezTest))
    return suite

