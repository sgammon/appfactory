# -*- coding: utf-8 -*-

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
