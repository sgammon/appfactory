import config
import webapp2

from apptools.util import debug
from apptools.util import datastructures

from appfactory.integration.abstract import CommandBus

## Headers - frozen set of possible frontline-provided headers
_FRONTLINE_HEADERS = frozenset(['Frontline',
								'Agent',
								'Hostname',
								'Broker',
								'Protocol',
								'Version',
								'Entrypoint',
								'Flags',
								'Client',
								'Hash',
								'Channel'])


## Flags - frozen set of reserved flags that can appear in the "Flags" header
_FRONTLINE_FLAGS = frozenset(['ap', 'opt', 'spdy', 'ps', 'pri', 'ofr',  'ins', 'wsp'])


## FrontlineBus
## Parses headers added by the AppFactory frontline, in order to facilitate triggering/changing behaviour in the codebase based on the hosting scheme being used.
class FrontlineBus(CommandBus):

	''' AppFactory Frontline management and integration code. '''

	## == Internal Methods == ##
	@webapp2.cached_property
	def config(self):

		''' Named config pipe. '''

		return config.config.get('layer9.appfactory.frontline')

	@webapp2.cached_property
	def logging(self):

		''' Named logging pipe. '''

		return debug.AppToolsLogger(path='appfactory.integration.frontline', name='FrontlineBus')._setcondition(self.config.get('debug', False))

	## == Meta Header Triggers == ##
	def __hash(self, handler, value):

		''' Set internal request hash. '''

		if isinstance(value, basestring) and len(value) > 0:
			handler.request_hash = value
		return

	def __channel(self, handler, value):

		''' Set internal push endpoint. '''

		if isinstance(value, basestring) and len(value) > 0:
			handler.push_channel = value
		return

	def __flags(self, handler, value):

		''' Set reserved flags. '''

		directive_i = value.split(',')
		if len(directive_i) > 0:
			for directive in directive_i:
				try:
					di_r = directive.split('=')
					if len(di_r) > 1:
						k, v = tuple(di_r)
					else:
						k, v = tuple(di_r, None)
					k = k.lower().lstrip().rstrip()
					if k in _FRONTLINE_FLAGS:
						handler.flags[k.upper()] = v
					else:
						self.logging.warning('Rogue frontline reserved option encountered, at key "%s". Register or meet your peril!' % k)
						continue
				except Exception, e:
					self.logging.error('Error encountered processing reserved flags at key "%s" with exception "%s". Continuing.' % (k, e))
					continue
		return

	def __agent(self, handler, value):

		''' Parse the user agent string, as provided by the Frontline in an alternate header. '''

		if isinstance(value, basestring) and len(value) > 0:
			try:

				# Pass through httpagentparser
				handler.uagent = handler.util.httpagentparser(value)
				handler.uagent['original'] = value

			except Exception, e:

				self.logging.warning('Unable to parse AppFactory UserAgent header with value "%s". Exception: "%s".' % (e ,uagent))
				return

	def __client(self, handler, value):

		''' Consider the true remote IP, not the frontline IP. '''

		if isinstance(value, basestring) and len(value) > 0:
			try:

				# Make sure it's something resembling an IP.
				ip_octets = [int(i) for i in value.split('.')]
				assert len(ip_octets) == 4

				# Make sure it's not a private or invalid IP.
				assert ip_octets[0] != 10
				assert 255 not in ip_octets
				assert (ip_octets[0] != 0 and ip_octets[-1] != 0)
				assert (ip_octets[0] != 172 and ip_octets[1] != 16)
				assert (ip_octets[0] != 192 and ip_octets[1] != 168)

			except ValueError, e:

				# If it could not be split or converted...
				self.logging.error('Invalid IP given for AppFactory remote client header. Value given: "%s"' % value)
				if config.debug:
					raise
				else:
					return

			except AssertionError, e:

				# If it's a private, broadcast or subnet mask IP...
				self.logging.error('Private, broadcast or subnet mask given as remote IP. Invalid value given was "%s". Discarding.' % value)
				if config.debug:
					raise
				else:
					return

			else:

				# If everything passed, set the overridden remote IP.
				handler.force_remoteip = '.'.join([str(octet) for octet in ip_octets])
				return

	def __broker(self, handler, value):

		''' Store the broker for this connection, which is the frontline instance handling the request/response cycle. '''

		if isinstance(value, basestring) and len(value) > 0:
			handler.broker = value
		return

	def __version(self, handler, value):

		''' Set the system version. '''

		if isinstance(value, basestring) and len(value) > 0:
			try:
				sv, pv = tuple([float(i.split('=')[1]) for i in value.split(',')])
			except ValueError, e:
				self.logging.warning('Invalid AppFactory system version provided ("%s") of type "%s".' % (value, type(value)))
				return
			else:
				if not isinstance(handler._appfactory_version, tuple):
					handler._appfactory_version = tuple([0, 0])
				handler._appfactory_version = sv, pv
		return

	def __protocol(self, handler, value):

		''' Set the protocol version. '''

		if isinstance(value, basestring) and len(value) > 0:
			if value.lower().lstrip().rstrip() == 'https':
				handler.force_https_assets = True
				handler.force_absolute_assets = True
		return

	def __hostname(self, handler, value):

		''' Set the proxied hostname, for redirection/assets/links. '''

		if isinstance(value, basestring) and len(value) > 0:
			handler.force_hostname = value
			handler.force_absoltue_assets = True
		return

	def __frontline(self, handler, value):

		''' Set the frontline cluster that this request entered Layer9 through. '''

		if isinstance(value, basestring) and len(value) > 0:
			handler.frontline = value
		return

	def __entrypoint(self, handler, value):

		''' Set the app/host that this request entered Layer9 through. '''

		if isinstance(value, basestring) and len(value) > 0:
			handler.entrypoint = value
		return

	trigger = datastructures.DictProxy({

		'hash': __hash,
		'flags': __flags,
		'agent': __agent,
		'client': __client,
		'broker': __broker,
		'channel': __channel,
		'version': __version,
		'protocol': __protocol,
		'hostname': __hostname,
		'frontline': __frontline,
		'entrypoint': __entrypoint

	})

	## == Dispatch + Exports == ##
	def _dispatch(self, handler, header, value):

		''' Dispatch internal functions to change aspects of the environment or request based on a sniffed header. '''

		handler._triggered = {}
		self.logging.info('Dispatching action for header "%s".' % (header))

		if hasattr(self.trigger, header.lower()):
			try:
				value = getattr(self.trigger, header.lower())(self, handler, value)
			except Exception, e:
				self.logging.error('Unhandled exception "%s" encountered when triggering functionality on AppFactory standard header "%s", set at value "%s".' % (e, header, value))
				if config.debug:
					raise
				else:
					return False
			else:
				self.logging.debug('Dispatched action completed with no issues.')
		return value

	def sniff(self, handler):

		''' Sniff a request for headers that were added by the AppFactory upstream servers. '''

		self.logging.info('Sniffing request for AppFactory frontline headers.')

		if self._l9config.get('headers', {}).get('use_compact', False):
			prefix = self._l9config.get('headers', {}).get('full_prefix', 'X-AppFactory')
		else:
			prefix = self._l9config.get('headers', {}).get('compact_prefix', 'XAF')

		sniffed = []
		for i in _FRONTLINE_HEADERS:
			header_i = '-'.join([prefix, i])
			self.logging.debug('--Looking for header "%s".' % header_i)

			if header_i in handler.request.headers:
				self.logging.debug('-----Found!')
				sniffed.append((i, handler.request.headers[header_i]))

		for header_s, value in sniffed:
			try:
				self._dispatch(handler, header_s, value)
			except:
				self.logging.error('Encountered an error dispatching detected AppFactory trigger header "%s".' % header_s)

		return sniffed

	def dump(self, handler, result):

		''' Dump the upstream state to memcache, so stats and realtime operations can be introspected and displayed. '''

		self.logging.info('Dumped AppFactory Frontline state.')


IntegrationBridge = FrontlineBus()
