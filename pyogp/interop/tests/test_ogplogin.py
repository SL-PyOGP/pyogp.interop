import unittest, doctest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base.registration import init
from pyogp.lib.base.interfaces import IPlaceAvatar
from pyogp.lib.base.OGPLogin import OGPLogin

from helpers import Agent

class AuthOGPLoginTest(unittest.TestCase):

    login_uri = None
    region_uri = None

    def setUp(self):
        init() # initialize the framework        

        # initialize the config
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
       
        # global test attributes
        self.login_uri = config.get('test_ogplogin_setup', 'login_uri')
        self.region_uri = config.get('test_ogplogin_setup', 'region_uri')
        
        # test_base_login attributes
        self.firstname = config.get('test_base_login', 'firstname')
        self.lastname = config.get('test_base_login', 'lastname')
        self.password = config.get('test_base_login', 'password')

        #todo: grab account info from a local file, the config for is is the only thing ever chcecked in to svn
        self.client = Agent()

    def tearDown(self):
        
        self.client.logout()
        '''
        if self.client.agentdomain != None:
            self.client.logout()
        '''
        
    def test_base_login(self):
 
        self.client.authenticate(self.firstname, self.lastname, self.password, self.login_uri)

        #gets seedcap, and an agent that can be placed in a region
        assert self.client.agentdomain.seed_cap.public_url != None or self.client.agentdomain.seed_cap.public_url != {}, "Login to agent domain failed"
 
        self.client.rezOnSim(self.region_uri)
        
        # test that rez_avatar/place contains the proper respose data
        assert self.client.avatar.region.details['seed_capability'] != None or client.avatar.region.details['seed_capability'] != {}, "Rez_avatar/place returned no seed cap"
        assert self.client.avatar.region.details['look_at'] != None or self.client.avatar.region.details['look_at'] != {}, "Rez_avatar/place returned no look_at"
        assert self.client.avatar.region.details['sim_ip'] != None or self.client.avatar.region.details['sim_ip'] != {}, "Rez_avatar/place returned no sim_ip"
        assert self.client.avatar.region.details['sim_port'] != None or self.client.avatar.region.details['sim_port'] != {}, "Rez_avatar/place returned no sim_port"
        assert self.client.avatar.region.details['region_x'] != None or self.client.avatar.region.details['region_x'] != {}, "Rez_avatar/place returned no region_x"
        assert self.client.avatar.region.details['region_y'] != None or self.client.avatar.region.details['region_y'] != {}, "Rez_avatar/place returned no region_y"
        assert self.client.avatar.region.details['region_id'] != None or self.client.avatar.region.details['region_id'] != {}, "Rez_avatar/place returned no region_id"
        assert self.client.avatar.region.details['sim_access'] != None or self.client.avatar.region.details['sim_access'] != {}, "Rez_avatar/place returned no sim_access"
        assert self.client.avatar.region.details['connect'] != None or self.client.avatar.region.details['connect'] != {}, "Rez_avatar/place returned no connect"
        assert self.client.avatar.region.details['position'] != None or self.client.avatar.region.details['position'] != {}, "Rez_avatar/place returned no position"
        assert self.client.avatar.region.details['session_id'] != None or self.client.avatar.region.details['session_id'] != {}, "Rez_avatar/place returned no session_id"
        assert self.client.avatar.region.details['secure_session_id'] != None or self.client.avatar.region.details['secure_session_id'] != {}, "Rez_avatar/place returned no secure_session_id"
        assert self.client.avatar.region.details['circuit_code'] != None or self.client.avatar.region.details['circuit_code'] != {}, "Rez_avatar/place returned no cicuit_code"
        
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(AuthOGPLoginTest))
    return suite
