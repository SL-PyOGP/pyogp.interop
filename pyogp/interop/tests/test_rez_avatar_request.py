#!/usr/bin/python

import unittest
#from indra.ipc import llsdhttp
# from indra.base import lluuid
# from pyogp.lib.base.network import IRESTClient, StdLibClient, HTTPError
# from zope.component import provideUtility, getUtility
# from pyogp.lib.base.tests.base import AgentDomain
from pyogp.lib.base.registration import init
# from pyogp.lib.base.interfaces import ISerialization, IDeserialization
from pyogp.lib.base.caps import Capability

class RezAvatarRequestTests(unittest.TestCase):

    def setUp(self):
        init()
        self.agent_id = '3d2b8256-12cd-40fd-abf8-6da4ad6739a2'
        self.regionuri = 'http://sim1.vaak.lindenlab.com:13000'
        #  http://sim2.vaak.lindenlab.com:12035/agent/(uuid)/rez_avatar/request
        self.request_rez_avatar_url = self.regionuri + '/agent/' + self.agent_id + '/rez_avatar/request'
        self.default_arguments={
            'agent_id' : self.agent_id,
            'first_name': 'Leyla',
            'last_name': 'Tester',
            'age_verified' : True,
            'agent_access' : True,
            'god_level':  200,
            'identified':  True,
            'transacted': True,
            'limited_to_estate': 1,
            'sim_access' : 'Mature'
            }
        #!?
        # provideUtility(StdLibClient(), IRESTClient)    
        # self.client = getUtility(IRESTClient)
        self.capability = Capability('rez_avatar/request', self.request_rez_avatar_url)

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
        
        # check for existence of fields
        self.assert_(result.has_key('connect') and
                     result.has_key('rez_avatar/rez') and
                     result.has_key('sim_ip') and
                     result.has_key('sim_port') and
                     result.has_key('region_x') and
                     result.has_key('region_y') and
                     result.has_key('region_id') and
                     result.has_key('sim_access') and
                     result.has_key('seed_capability'))

    def test_rez_avatar_request_connect(self):
        """ Agent is allowed to connect """
        result = self.postToCap(self.default_arguments)
        
        self.check_response_base(result)
        self.assertEquals(result['connect'], True)

        
    def test_rez_avatar_request_region_x(self):
        """ region_x is less than 256 """
        result = self.postToCap(self.default_arguments)
        
        self.check_successful_response(result)
        self.assert_(result['region_x'] < 256)

    def test_rez_avatar_request_region_y(self):
        """ region_y is less than 256 """
        result = self.postToCap(self.default_arguments)

        self.check_successful_response(result)
        self.assert_(result['region_y'] < 256)

    def test_rez_avatar_request_region_id_UUID(self):
        """ region_id is a UUID """
        
        #ToDo: find/implement a helper funtion for isUUID
        return
        """
        result = self.postToCap(self.default_arguments)

        self.check_successful_response(result)
        self.assert_(isUUID(result['region_id']))
        """                        

    def test_rez_avatar_request_unverified(self):
        """ Unverified agents should not be allowed """
        args = self.default_arguments
        args['age_verified'] = False

        result = self.postToCap(args)

        self.check_response_base(result)
        self.assertEquals(result['connect'], False)

    def test_rez_avatar_request_noaccess(self):
        """ Agents without access cannot be allowed """
        args = self.default_arguments
        args['agent_access'] = False

        result = self.postToCap(args)

        self.check_response_base(result)
        self.assertEquals(result['connect'], False)

    def test_rez_avatar_request_unidentified(self):
        """ Unidentified agents should not be allowed """
        args = self.default_arguments
        args['identified'] = False

        result = self.postToCap(args)

        self.check_response_base(result)
        self.assertEquals(result['connect'], False)

    def test_rez_avatar_request_godlevel(self):
        """ Gods are allowed in teen regions """
        args = self.default_arguments
        args['god_level'] = 0

        result = self.postToCap(args)

        self.check_response_base(result)
        self.assertEquals(result['connect'], False)

    def test_rez_avatar_request_untransacted(self):
        """ Agents not transacted are not allowed in ____ regions """
        args = self.default_arguments
        args['transacted'] = False

        result = self.postToCap(args)

        self.check_response_base(result)
        self.assertEquals(result['connect'], False)

    def test_rez_avatar_request_limited_estate(self):
        """ Teens limited to estate 5 cannot access adult regions """
        args = self.default_arguments
        args['limited_to_estate'] = 5

        result = self.postToCap(args)

        self.check_response_base(result)
        self.assertEquals(result['connect'], False)

    def test_rez_avatar_request_sim_access(self):
        """ Agents with PG access cannot access mature region """
        args = self.default_arguments
        args['sim_access'] = 'PG'

        result = self.postToCap(args)

        self.check_response_base(result)
        self.assertEquals(result['connect'], False)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarRequestTests))
    return suite

if __name__ == '__main__':
    unittest.main()
