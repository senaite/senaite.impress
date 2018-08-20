# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS
#
# Copyright 2018 by it's authors.

from senaite.impress import logger

PROFILE_ID = "profile-senaite.impress:default"


def to_1000(portal_setup):
    """Initial version to 1000

    :param portal_setup: The portal_setup tool
    """

    logger.info("Run all import steps from SENAITE IMPRESS ...")
    portal_setup.runAllImportStepsFromProfile(PROFILE_ID)
    logger.info("Run all import steps from SENAITE IMPRESS [DONE]")
