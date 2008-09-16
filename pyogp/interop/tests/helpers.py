# std lib
import time
#import urllib2 # for the redirect help, ToDo: need to refactor pyogp.lib.base.agentdomain to extract this out 
import ConfigParser
from pkg_resources import resource_stream
import logging

# zca
from zope.component import queryUtility, adapts, getUtility

# related
from indra.base import llsd

#pyogp.lib.base
from pyogp.lib.base.credentials import PlainPasswordCredential
from pyogp.lib.base.agentdomain import AgentDomain
from pyogp.lib.base.regiondomain import Region
from pyogp.lib.base.registration import init
from pyogp.lib.base.interfaces import IPlaceAvatar # ToDo: move to agentdomain.PlaceAvatar?
from pyogp.lib.base.OGPLogin import OGPLogin
from pyogp.lib.base.interfaces import ISerialization
from pyogp.lib.base.network import IRESTClient

from indra.base import llsd

# prep config
config = ConfigParser.ConfigParser()
config.readfp(resource_stream(__name__, 'testconfig.cfg'))

debug = bool(int(config.get('testconfig', 'debug')))

# prep pyogp
init()

#setup logging

if debug: 

    console = logging.StreamHandler()
    console.setLevel(logging.DEBUG) # seems to be a no op, set it for the logger
    formatter = logging.Formatter('%(asctime)-30s%(name)-30s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # setting the level for the handler above seems to be a no-op
    # it needs to be set for the logger, here the root logger
    # otherwise it is NOTSET(=0) which means to log nothing.
    logging.getLogger('').setLevel(logging.DEBUG)
    logger = logging.getLogger('pyogp.interop.helpers')

    logger.debug('setting debug to True')

def logout(me):
    """ logout a something from somewhere """

    time.sleep(30)