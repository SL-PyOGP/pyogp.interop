# std lib
import unittest
import ConfigParser
from pkg_resources import resource_stream

# pygop
from pyogp.lib.base.registration import init
from pyogp.lib.base.caps import Capability
from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region

# pyogp.interop
import helpers

'''

write tests against agent/info, an agent domain cap
http://wiki.secondlife.com/wiki/Open_Grid_Protocol#Region_Information_.28Resource_Class.29

'''

class testCapAgentInfo(unittest.TestCase):

    def setUp(self):
        init()
        
        config = ConfigParser.ConfigParser()
        config.readfp(resource_stream(__name__, 'testconfig.cfg'))
        
        self.test_setup_config_name = 'test_interop_account'
        
        self.firstname = config.get(self.test_setup_config_name, 'firstname')
        self.lastname = config.get(self.test_setup_config_name, 'lastname')
        self.password = config.get(self.test_setup_config_name, 'password')
        self.login_uri = config.get(self.test_setup_config_name, 'login_uri')        
        self.region_uri = config.get('test_interop_regions', 'start_region_uri') 

        # first establish an AD connection and get seed_cap for mtg
        # <start>
        self.agentdomain = AgentDomain(self.login_uri)
        
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)

        #gets seedcap, and an agent that can be placed in a region
        self.agentdomain.login(credentials)
 
        self.caps = self.agentdomain.seed_cap.get(['agent/info'])
        
        # initialize the cap object for use in postToCap
        self.capability = Capability('agent/info', self.caps['agent/info'].public_url)
        
    def tearDown(self):
        
        # uncomment once tests can be run
        # self.client.logout()
        '''
        if {agent is logged in flag is set}
            self.client.logout()
        '''
    
    def getCap(self):
        """ sends a get to the cap """

        try:
            result = self.capability.GET()
        except Exception, e:
            #print 'Exception: ' + e.message + ' ' + str(e.args)
            result = str(e.args)

        return result
    
    def check_response_base(self, result):
        """ check for the existence of the correct parameters in the cap response """

        # successful response contains: 
        # { agent_id: uuid , circuit_code: int , session_id: uuid , secure_session_id: uuid , presence: { status: "online"|"offline" , region_url: url } }
        self.assert_(result.has_key('agent_id') and
                     result.has_key('circuit_code') and
                     result.has_key('session_id') and
                     result.has_key('secure_session_id') and
                     result.has_key('presence'))

###################################
#           Test Cases            #
###################################
    # Add moar tests

                     
    def test_cap_agent_info_online(self):
        """ agent/info cap returns the right response for an online agent """
        
        response = self.getCap()
        
        self.check_response_base(response)
    



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(testCapAgentInfo))
    return suite

