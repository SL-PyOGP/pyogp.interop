import time
import urllib2 # for the redirect help, ToDo: need to refactor pyogp.lib.base.agentdomain to extract this out 

from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base.registration import init
from pyogp.lib.base.interfaces import IPlaceAvatar # ToDo: move to agentdomain.PlaceAvatar?
from pyogp.lib.base.OGPLogin import OGPLogin
from pyogp.lib.base.interfaces import ISerialization

from indra.base import llsd

# ToDo: need to refactor pyogp.lib.base.agentdomain to extract this out 
USE_REDIRECT = True
if USE_REDIRECT: 
    # REMOVE THIS WHEN THE REDIRECT IS NOT NEEDED ANYMORE FOR LINDEN LAB!
    class RedirectHandler(urllib2.HTTPRedirectHandler):

        def http_error_302(self, req, fp, code, msg, headers):
            #ignore the redirect, grabbing the seed cap url from the headers
            # TODO: add logging and error handling
            return headers['location']


    # post to auth.cgi, ignoring the built in redirect
    AgentDomainLoginOpener = urllib2.build_opener(RedirectHandler())

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
       
    def authenticate(self, firstname, lastname, password, login_uri):
        """ authenticate against an agent domain """
        
        credentials = PlainPasswordCredential(firstname, lastname, password)
        self.agentdomain = AgentDomain(login_uri)

        #gets seedcap, and an agent that can be placed in a region
        self.agentdomain.login(credentials)
    
    def retrieveCap(self, capability_name):
        """ post to the seedcap to retrieve a capability url """
        
        caps = self.agentdomain.seed_cap.get([capability_name])
        
        return caps

    def rezOnSim(self, region_uri):
        """ rez on a sim, aka teleport """
        
        caps = self.agentdomain.seed_cap.get(['rez_avatar/place'])

        # try and connect to a sim
        self.region = Region(region_uri)
        place = IPlaceAvatar(self.agentdomain)

        self.avatar  = place(self.region)

        # print dir(self.region)
  
    def logout(self):
        """ logs the agent out of the grid """

        # currently, we don't disconnect from the sim, b/c we never really connect there, so let's just sleep for a mo or 10 so the AD timesout
        # another way to go about it would be to call derez?
        # would love to put a flag on the agent that indicates whether they logged in or not, so we could conditionally call logout in the tests
        time.sleep(15)
    
    
    def postToLoginUri(self, firstname, lastname, password, login_uri):
        """ posts to login_uri and returns the response"""
        
        self.firstname = firstname
        self.lastname = lastname
        self.password = password
        self.login_uri = login_uri
        
        credentials = PlainPasswordCredential(self.firstname, self.lastname, self.password)
        
        serializer = ISerialization(credentials) # convert to string via adapter
        payload = serializer.serialize()
        content_type = serializer.content_type
        headers = {'Content-Type': content_type}
        
        # now create the request. We assume for now that self.uri is the login uri
        # TODO: make this pluggable so we can use other transports like eventlet in the future
        # TODO: add logging and error handling
        if USE_REDIRECT:
            request = urllib2.Request(self.login_uri,payload,headers)        
            try:
                response = AgentDomainLoginOpener.open(request)       
            except urllib2.HTTPError,e:
                # is this weird to anyone but me, that the 403 returns the llsd in the e here?
                response = e.read()
                response = llsd.parse(response)
        else:
            pass
        '''
            restclient = getUtility(IRESTClient)
            try:
                response = restclient.POST(self.login_uri, payload, headers=headers)
            except HTTPError, error:
                pass
                print "error", error.code, error.msg
                print error.fp.read()
                
        
            result = llsd.parse(response)
         '''   
        return response
