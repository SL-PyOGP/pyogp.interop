#!/usr/bin/python

import unittest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability

from helpers import Agent

'''
write tests against the protocol as is defined at http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Place_Avatar_.28Resource_Class.29
'''

class RezAvatarPlaceTests(unittest.TestCase):
    """ test posting to rez_avatar/place for a simulator, acting as the region domain """
    
    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.firstname = config.get('test_rez_avatar_place_setup', 'firstname')
        self.lastname = config.get('test_rez_avatar_place_setup', 'lastname')
        self.password = config.get('test_rez_avatar_place_setup', 'password')
        self.login_uri = config.get('test_rez_avatar_place_setup', 'login_uri')
        self.region_uri = config.get('test_rez_avatar_place_setup', 'region_uri')
        self.position = config.get('test_rez_avatar_place_setup', 'position')
        
        # required_parameters: { region_url: url string, position: [x real, y real, z real, ] }
        self.required_parameters = {
            'region_url' : self.region_uri,
            'position' : self.position
            }

        # to get place, we need to authenticate and retrieve the place_avatar cap from the AD
        self.client = Agent()
        self.client.authenticate(self.firstname, self.lastname, self.password, self.login_uri)
        self.caps = self.client.agentdomain.seed_cap.get(['rez_avatar/place'])
        
        # initialize the cap object for use in postToCap
        self.capability = Capability('rez_avatar/place', self.caps['rez_avatar/place'].public_url)
       
    def tearDown(self):
        
        self.client.logout()
        '''
        if self.client.agentdomain != None:
            self.client.logout()
        '''
        
    def postToCap(self, arguments):
        

        try:
            result = self.capability.POST(arguments)
        except Exception, e:
            #print 'Exception: ' + e.message + ' ' + str(e.args)
            result = str(e.args)

        return result

    
    def check_successful_response(self, result):
        """ check for the existence of the correct parameters in the cap response """

        # Success response: { connect: bool , seed_capability: url string , look_at: [x real, y real, z real, ] , position: [x real, y real, z real, ]}
        
        self.assert_(result.has_key('connect') and
                     result.has_key('look_at') and
                     result.has_key('position') and
                     result.has_key('seed_capability'))
        
        self.assert_(result['position'][0] < 256 and
                     result['position'][1] < 256 and 
                     result['position'][2] < 256)
        
        self.assert_(result['look_at'][0] < 256 and
                     result['look_at'][1] < 256 and 
                     result['look_at'][2] < 256)

    def check_failure_response(self, result):
        """ tests the failure response for the proper content """
        
        # docs are missing this detail
        
        print result 

###################################
#           Test Cases            #
###################################
                     
    def test_rez_avatar_place_required(self):
        """ agent is allowed to rez """

        result = self.postToCap(self.required_parameters)

        self.check_successful_response(result)
        self.assertEquals(result['connect'], True)
    
    '''   
    def test_rez_avatar_place_nocontent(self):
        """ agent is allowed to rez """

        result = self.postToCap({'region_url' : '', 'position' : ''})

        self.check_failure_response(result)
    '''

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(RezAvatarPlaceTests))
    return suite

