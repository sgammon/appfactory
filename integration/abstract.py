# -*- coding: utf-8 -*-

# Base Imports
import config
import webapp2


## CommandBus
# Abstract parent for integration classes.
class CommandBus(object):

    ''' Abstract parent for integration classes that add methods to trigger or respond to AppFactory-specific functionality. '''

    @webapp2.cached_property
    def _l9config(self):

        ''' Named config pipe to main Layer9 config. '''

        return config.config.get('layer9.appfactory')

    flags = frozenset((
        'OPT',   # Optimizations (On/Off)
        'SPDY',  # SPDY mode (On/Off)
        'PS',    # Pagespeed mode (On/Off)
        'PRI',   # Partial Response Hash (String)
        'OFR',   # Omit Frame (On/Off)
        'AP',    # Agent Privilege (On/Off)
        'INS',   # Instrumentation (On/Off)
        'WSP'    # Socket Push (On/Off)
    ))
