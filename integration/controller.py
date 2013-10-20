# -*- coding: utf-8 -*-

'''

    appfactory integrations: controller

    :author: Sam Gammon <sam@momentum.io>
    :copyright: (c) momentum labs, 2013
    :license: The inspection, use, distribution, modification or implementation
              of this source code is governed by a private license - all rights
              are reserved by the Authors (collectively, "momentum labs, ltd")
              and held under relevant California and US Federal Copyright laws.
              For full details, see ``LICENSE.md`` at the root of this project.
              Continued inspection of this source code demands agreement with
              the included license and explicitly means acceptance to these terms.

'''


# Base Imports
import config
import webapp2

# AppTools Util
from apptools.util import debug

# Integration Primitives
from appfactory.integration.abstract import CommandBus


## ControllerBus
# Command integration class for connecting the L9 controller layer.
class ControllerBus(CommandBus):

    ''' Controller layer command bus. '''

    ## == Internal Methods == ##
    @webapp2.cached_property
    def config(self):

        ''' Named config pipe. '''

        return config.config.get('layer9.appfactory.controller')

    @webapp2.cached_property
    def logging(self):

        ''' Named logging pipe. '''

        return debug.AppToolsLogger(path='appfactory.integration.controller', name='ControllerBus')._setcondition(self.config.get('debug', False))

    ## == Exports == ##
    def dump(self, handler, result):

        ''' Dump controller state to memcache for later statistics generation. '''

        self.logging.info('Dumped AppFactory Controller state.')


IntegrationBridge = ControllerBus()
