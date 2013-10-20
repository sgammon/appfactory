# -*- coding: utf-8 -*-

'''

    appfactory integrations

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

# AppTools Util
from apptools.util import debug
from apptools.util import datastructures

# Layer9 Command Busses
from appfactory.integration.abstract import CommandBus as CoreCommandBus
from appfactory.integration.upstream import IntegrationBridge as UpstreamIntegrationBus
from appfactory.integration.frontline import IntegrationBridge as FrontlineIntegrationBus
from appfactory.integration.controller import IntegrationBridge as ControllerIntegrationBus


## AppFactoryMixin
# Introduces properties and methods for integration with the Layer9/AppFactory Platform.
class AppFactoryMixin(object):

    ''' Mixes in AppFactory properties and functionality. '''

    _appfactory_version = (0, 0)  # This library's version.

    # AppFactory Integration
    flags = datastructures.DictProxy(dict([(i, False) for i in CoreCommandBus.flags]))

    broker = None  # Address of the frontline instance brokering this request/response cycle.
    frontline = None  # The frontline cluster string ID brokering this request/response cycle.
    entrypoint = None  # The VHost entrypoint string ID that Layer9 resolved during routing.
    force_https = False  # Whether to force HTTPS mode, given the appropriate signal from Layer9.
    request_hash = None  # Unique hash for this request, generated by Layer9, and kept for logging and audit purposes.
    push_channel = None  # Inter-platform communication channel, for pushing a response through Layer9's socket infrastructure.
    force_remoteip = False  # The client's true remote IP, as reported by the Layer9 frontline.
    force_hostname = False  # The proxied hostname that should be used for redirects, assets, cookies, etc.
    force_https_assets = False  # Whether to force HTTPS assets. This should be `True` in HTTPS mode to avoid browser warnings.
    force_absolute_assets = False  # Whether to force absolute assets. Always `True` in HTTPS mode.
