from logging import getLogger, CRITICAL, ERROR, WARNING, INFO, DEBUG
import unittest, doctest
import ConfigParser
import os

from eventlet import api

from pyogp.lib.base.agent import Agent
from pyogp.lib.base.datatypes import UUID
from pyogp.lib.base.exc import LoginError
from pyogp.lib.base.settings import Settings
from pyogp.lib.base.utilities.helpers import Wait

import helpers

# initialize logging
logger = getLogger('test_object_perms')
log = logger.log

class TestObjectPerms(unittest.TestCase):

    def setUp(self):

        # initialize the config
        self.config = ConfigParser.ConfigParser()
        self.config.readfp(open(os.path.join(os.path.dirname(__file__),'testconfig.cfg')))

        self.test_setup_config_name = 'test_interop_account'

        self.firstname = self.config.get(self.test_setup_config_name, 'firstname')
        self.lastname = self.config.get(self.test_setup_config_name, 'lastname')
        self.password = self.config.get(self.test_setup_config_name, 'password')
        self.agent_id = self.config.get(self.test_setup_config_name, 'agent_id')
        self.login_uri = self.config.get(self.test_setup_config_name, 'login_uri')
        self.region = self.config.get('test_interop_regions', 'start_region_uri') 

        self.settings = Settings()
        self.settings.MULTIPLE_SIM_CONNECTIONS = False
        self.settings.ENABLE_INVENTORY_MANAGEMENT = False
        self.settings.ENABLE_EQ_LOGGING = False
        self.settings.ENABLE_CAPS_LOGGING = False
        #self.settings.ENABLE_UDP_LOGGING = False

        self.client = Agent(self.settings, self.firstname, self.lastname, self.password)

        api.spawn(self.client.login, self.login_uri, self.firstname, self.lastname, self.password, start_location = self.region)

        # wait for the agent to connect to it's region
        while self.client.connected == False:
            api.sleep(0)

        while self.client.region.connected == False:
            api.sleep(0)

        # wait a few seconds to let things settle down
        Wait(3)

    def tearDown(self):
        
        if self.client.connected:
            self.client.logout()
        
    def test_object_permissions(self):
        """ test various object perms """

        # ideally this would be done on a void region (makes things easier)

        # let the scene load a bit
        Wait(5)

        # assuming we've gotten eveything (we haven't, but for the sake of argument)
        # let's do a preliminary purge of our objects if there are any
        my_known_objects = [_object for _object in self.client.region.objects.my_objects()]

        for item in my_known_objects:
            log(INFO, "Derezzing object '%s' with id %s" % (item.Name, item.FullID))
            item.take(self.client)

        # create a new box on the region
        self.client.region.objects.create_default_box(GroupID = self.client.ActiveGroupID, relative_position = (1,0,0))

        Wait(10)

        # let's see what's nearby, pretty much within the range that we rezzed (1m away)
        objects_nearby = self.client.region.objects.find_objects_within_radius(2)

        # trigger ObjectProperties packets to be sent by selecting the objects so we know more about the objects
        for item in objects_nearby:
            item.select(self.client)

        Wait(5)

        # why not deselect them
        for item in objects_nearby:
            item.deselect(self.client)

        # find the objects i just rezzed
        # any items deleted from the sim earlier would have been removed from our store via the KillObject message handler
        my_objects = self.client.region.objects.my_objects()

        # let's manipulate the object(s) nearby
        for item in my_objects:

            # give it the name of it's id
            item.set_object_name(self.client, 'TestCase' + str(item.LocalID))

            item.set_object_transfer_only_permissions(self.client)

            # the sim acts strange if you spam it too crazy fast....
            waiter = Wait(2)
            #item.take(client)

        # wait a bit so things settle down
        Wait(5)

        # now, let's validate things a lil'
        #[self.assertEquals(self.client.region.objects.get_object_from_store(FullID = item.FullID).Name, 'TestCase' + str(item.LocalID)) for item in my_objects]

        for item in my_objects:

            self.assertEquals(item.NextOwnerMask, 532480)

        for item in my_objects:

            item.set_object_copy_mod_permissions(self.client)

        Wait(5)

        for item in my_objects:

            self.assertEquals(item.NextOwnerMask, 573440)

        # leave no trace!
        for item in my_objects:
            item.take(self.client)

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestObjectPerms))
    return suite

"""
Contributors can be viewed at:
http://svn.secondlife.com/svn/linden/projects/2008/pyogp/CONTRIBUTORS.txt 

$LicenseInfo:firstyear=2008&license=apachev2$

Copyright 2009, Linden Research, Inc.

Licensed under the Apache License, Version 2.0 (the "License").
You may obtain a copy of the License at:
    http://www.apache.org/licenses/LICENSE-2.0
or in 
    http://svn.secondlife.com/svn/linden/projects/2008/pyogp/LICENSE.txt

$/LicenseInfo$
"""