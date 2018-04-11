# -*- coding: utf-8 -*-

import logging
from zope.i18nmessageid import MessageFactory

# Defining a Message Factory for when this product is internationalized.
senaiteMessageFactory = MessageFactory('senaite.publisher')

logger = logging.getLogger("senaite.publisher")


def initialize(context):
    """Initializer called when used as a Zope 2 product."""
    logger.info("*** Initializing SENAITE.PUBLISHER ***")
