# -*- coding: utf-8 -*-

'''

    appfactory integrations: upstream

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


## UpstreamBus
# AppFactory upstream layer integration bus.
class UpstreamBus(CommandBus):

    ''' AppFactory upstream layer integration. '''

    ## == Internal Methods == ##
    @webapp2.cached_property
    def config(self):

        ''' Named config access. '''

        return config.config.get('layer9.appfactory.upstream')

    @webapp2.cached_property
    def logging(self):

        ''' Named logging pipe. '''

        return debug.AppToolsLogger(path='appfactory.integration.upstream', name='UpstreamBus')._setcondition(self.config.get('debug', False))

    ## == Exports == ##
    def hint(self, handler, result):

        ''' Add headers to a response indicating associated static content, to allow the browser to preload/the server to push via SPDY, if enabled. '''

        # Add generic stuff to the result...
        if 'REQUEST_ID_HASH' in handler.request.environ:
            handler.response.headers['X-Request-Hash'] = handler.request.environ.get('REQUEST_ID_HASH')

        # If hinted asset preloading is enabled...
        self.logging.info('Considering upstream preloader hinting...')
        if self.config.get('enabled', False) and self.config.get('preloading', {}).get('gather_assets', False):

            # If the handler knows what we're up to...
            if hasattr(handler, '_gathered_assets'):

                self.logging.info('Preloading enabled, handler compatible.')

                # If SPDY push is how we're preloading...
                if self.config.get('preloading', {}).get('enable_spdy_push', False) and handler.flags.SPDY:
                    self.logging.info('==== !! SPDY integration mode is enabled. !! ====')
                    enable_spdy = True
                    spdy_config = self.config.get('spdy')
                    header = 'X-Associated-Content'

                # Otherwise, Firefox understands the `Link` header I guess...
                else:
                    self.logging.debug('SPDY integration disabled.')
                    enable_spdy = False
                    header = 'Link'
                    spdy_config = {}

                # Gather and format headers, optionally with priorities
                hint_header_values = []
                for type, ref, priority in handler._gathered_assets:
                    if enable_spdy is True:
                        hint_header = "\"%s\"" % ref
                        if spdy_config.get('push', {}).get('assets', {}).get('force_priority', False):
                            priority = self.config.get('spdy', {}).get('push', {}).get('assets', {}).get('default_priority', 7)
                        if priority:
                            hint_header_values.append(':'.join([hint_header, str(priority)]))
                        else:
                            hint_header_values.append(hint_header)

                self.logging.info('Found %s values to preload.' % len(hint_header_values))

                # Combine and add to response
                if len(hint_header_values) > 0:
                    handler.response.headers[header] = ", ".join(hint_header_values)
                    if isinstance(result, webapp2.Response):
                        result.headers[header] = handler.response.headers[header]

        return result

    def sniff(self, handler):

        ''' Sniff a request for headers that were added by the AppFactory upstream servers, to pull partial content or perform other transforms. '''

        pass

    def dispatch(self, request):

        ''' Dispatch internal functions to change aspects of the environment or request based on a sniffed header. '''

        pass

    def dump(self, handler, result):

        ''' Dump the upstream state to memcache, so stats and realtime operations can be introspected and displayed. '''

        self.logging.info('Dumped AppFactory Upstream state.')
        self.logging.info('--SPDY Push: "X-Associated-Content: %s"' % handler.response.headers.get('X-Associated-Content', None))


IntegrationBridge = UpstreamBus()
