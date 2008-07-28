#!/usr/bin/python

import unittest, time
from indra.ipc import llsdhttp
from indra.base import lluuid
import test_rez_avatar

agent_id = test_rez_avatar.agent_id
rez_avatar_url = test_rez_avatar.rez_avatar_url

source_regionuri = 'http://sim2.vaak.lindenlab.com:12035'

#  http://sim2.vaak.lindenlab.com:12035/agent/(uuid)/rez_avatar/derez
## TODO: should be rez_avatar/derez
#derez_avatar_url = source_regionuri + '/agent/' + agent_id + '/rez_avatar/derez'
derez_avatar_url = source_regionuri + '/agent/' + agent_id + '/derez_avatar'
default_derez_arguments={
    'rez_avatar': rez_avatar_url,
    'position': [0,0,0]
}

def derez_avatar(url=derez_avatar_url, arguments=default_derez_arguments):
    return llsdhttp.post(derez_avatar_url, arguments)

class DerezAvatarTests(unittest.TestCase):
    def check_successful_response(self, arguments):
        print "ARGs", arguments
        result = derez_avatar(arguments=arguments)
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
            result = derez_avatar(arguments=arguments)
            print "RESULT", result
        except Exception, e:
            # supposed to be error
            return

        self.assertEquals(result['connect'], False)


    ### This test currently fails because the rez_avatar call isnt complete
    ### and depends on rest of UDP messages to finish before agent is created
    def test0_default_derez(self):
        print "rez_result", test_rez_avatar.rez_avatar()
        self.check_successful_response(default_derez_arguments)
        # Fails with 400 You cannot teleport at this time because no agent

if __name__ == '__main__':
    unittest.main()
