import unittest, doctest
import ConfigParser
from pkg_resources import resource_stream

from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base.registration import init
from pyogp.lib.base.interfaces import IPlaceAvatar
from pyogp.lib.base.OGPLogin import OGPLogin

class AuthOGPLoginTest(unittest.TestCase):

    auth_uri = None
    region_uri = None

    def setUp(self):
        init() # initialize the framework        

        # initialize the config
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
       
        # global test attributes
        self.auth_uri = config.get('test_ogplogin_setup', 'auth_uri')
        self.region_uri = config.get('test_ogplogin_setup', 'region_uri')
        
        # test_base_login attributes
        self.base_firstname = config.get('test_base_login', 'firstname')
        self.base_lastname = config.get('test_base_login', 'lastname')
        self.base_password = config.get('test_base_login', 'password')

        #todo: grab account info from a local file, the config for is is the only thing ever chcecked in to svn

    def test_base_login(self):
        credentials = PlainPasswordCredential(self.base_firstname, self.base_lastname, self.base_password)
        agentdomain = AgentDomain(self.auth_uri)

        #gets seedcap, and an agent that can be placed in a region
        agent = agentdomain.login(credentials)
        assert agentdomain.seed_cap != None or agentdomain.seed_cap != {}, "Login to agent domain failed"

        #gets the rez_avatar/place cap
        caps = agentdomain.seed_cap.get(['rez_avatar/place'])
        
        assert caps['rez_avatar/place'] != None or caps['rez_avatar/place'] != {}, "Failed to retrieve the rez_avatar/place capability"
       
        # try and connect to a sim
        region = Region(self.region_uri)
        place = IPlaceAvatar(agentdomain)
        
        avatar = place(region)

        # test that rez_avatar/place contains the proper respose data
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
        
    def tearDown(self):
        # essentially logout by deleting presence... etc.
	pass
        
def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(AuthOGPLoginTest))
    return suite
