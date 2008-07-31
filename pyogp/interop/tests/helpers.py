from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base.registration import init
from pyogp.lib.base.interfaces import IPlaceAvatar
from pyogp.lib.base.OGPLogin import OGPLogin

class Agent():
    """ partial implementation of agent activities to support OGP testcases  """
    init() # initialize the framework        

    def __init__(self):
        # uris
        self.login_uri = None
        self.region_uri = None
      
        # agent attributes
        self.firstname = None
        self.lastname = None
        self.password = None
        
        self.agentdomain = None
        self.agent = None
        self.avatar = None
        self.region = None

    def login(self, firstname, lastname, password, login_uri, region_uri):
        """ login an agent and rez them on a sim """    
        
        self.login_uri = login_uri
        self.region_uri = region_uri
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        
        # authenticate against the region domain
        self.authenticate(self.firstname, self.lastname, self.password, self.login_uri)
       
        # rez on a sim
        self.rezOnSim(self.region_uri)
       
        print self.region.details

    def authenticate(self, firstname, lastname, password, login_uri):
        """ authenticate against an agent domain """
        
        credentials = PlainPasswordCredential(firstname, lastname, password)
        self.agentdomain = AgentDomain(login_uri)

        #gets seedcap, and an agent that can be placed in a region
        self.agentdomain.login(credentials)

    def rezOnSim(self, region_uri):
        """ rez on a sim, aka teleport """
        
        caps = self.agentdomain.seed_cap.get(['rez_avatar/place'])

        # try and connect to a sim
        self.region = Region(self.region_uri)
        place = IPlaceAvatar(self.agentdomain)

        self.avatar  = place(self.region)

        # print dir(self.region)
  
      

