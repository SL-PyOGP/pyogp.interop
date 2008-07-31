#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

class RezAvatarRequestTests(unittest.TestCase):

    def setUp(self):
        init()

        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        # grab the testdata from testconfig.cfg
        self.agent_id = config.get('test_rez_avatar_request_setup', 'agent_id')
        self.region_uri = config.get('test_rez_avatar_request_setup', 'region_uri')
        self.rez_request_avatar_url = self.region_uri + '/agent/' + self.agent_id + '/rez_avatar/request'
        
        self.default_arguments={
            'agent_id' : self.agent_id,
            'first_name' : config.get('test_rez_avatar_request_setup', 'first_name'),
            'last_name' : config.get('test_rez_avatar_request_setup', 'last_name'),
            'age_verified' : config.getboolean('test_rez_avatar_request_setup', 'age_verified'),
            'agent_access' : config.getboolean('test_rez_avatar_request_setup', 'agent_access'),
            'god_level' :  config.getint('test_rez_avatar_request_setup', 'god_level'),
            'identified' :  config.getboolean('test_rez_avatar_request_setup', 'identified'),
            'transacted' : config.getboolean('test_rez_avatar_request_setup', 'transacted'),
            'limited_to_estate' : config.getint('test_rez_avatar_request_setup', 'limited_to_estate'),
            'sim_access' : config.get('test_rez_avatar_request_setup', 'sim_access'),
            }

        self.capability = Capability('rez_avatar/request', self.rez_request_avatar_url)

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
