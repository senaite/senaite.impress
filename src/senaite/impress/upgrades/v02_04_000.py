# -*- coding: utf-8 -*-
#
# This file is part of SENAITE.IMPRESS.
#
# SENAITE.IMPRESS is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the Free
# Software Foundation, version 2.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program; if not, write to the Free Software Foundation, Inc., 51
# Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
# Copyright 2018-2024 by it's authors.
# Some rights reserved, see README and LICENSE.

from plone.browserlayer.utils import unregister_layer
from senaite.impress import logger

PROFILE_ID = "profile-senaite.impress:default"


def upgrade(portal_setup):
    """Update to version 2.4.0

    :param portal_setup: The portal_setup tool
    """

    logger.info("Run all import steps from SENAITE IMPRESS ...")
    portal_setup.runAllImportStepsFromProfile(PROFILE_ID)
    logger.info("Run all import steps from SENAITE IMPRESS [DONE]")


def import_registry(tool):
    """Import registry settings

    :param tool: portal_setup tool
    """
    logger.info("Import SENAITE IMPRESS registry ...")
    tool.runImportStepFromProfile(PROFILE_ID, "plone.app.registry")
    logger.info("Import SENAITE IMPRESS registry [DONE]")


def import_browserlayer(tool):
    """Import browser layer

    :param tool: portal_setup tool
    """
    logger.info("Import SENAITE IMPRESS browser layer ...")

    # ensure the old layer is removed first to make room for the new one
    try:
        unregister_layer("senaite.impress")
    except KeyError:
        # KeyError: 'No browser layer with name senaite.impress is registered
        pass

    # reimport browser layer to register ISenaiteImpressLayer
    tool.runImportStepFromProfile(PROFILE_ID, "browserlayer")

    logger.info("Import SENAITE IMPRESS browser layer [DONE]")
