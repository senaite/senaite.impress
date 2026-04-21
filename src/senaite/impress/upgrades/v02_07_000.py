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
# Copyright 2018-2025 by it's authors.
# Some rights reserved, see README and LICENSE.

from senaite.impress import logger

PROFILE_ID = "profile-senaite.impress:default"


def upgrade(portal_setup):
    """Update to version 2.7.0

    :param portal_setup: The portal_setup tool
    """
    logger.info("Run all import steps from SENAITE IMPRESS ...")
    portal_setup.runAllImportStepsFromProfile(PROFILE_ID)
    logger.info("Run all import steps from SENAITE IMPRESS [DONE]")


def import_report_logo_registry(portal_setup):
    """Import registry to register report_logo field
    """
    logger.info("Import registry from SENAITE IMPRESS ...")
    portal_setup.runImportStepFromProfile(
        PROFILE_ID, "plone.app.registry")
    logger.info("Import registry from SENAITE IMPRESS [DONE]")


def import_paperformats_registry(portal_setup):
    """Import registry for custom paper formats and template mapping
    """
    logger.info("Import registry from SENAITE IMPRESS ...")
    portal_setup.runImportStepFromProfile(
        PROFILE_ID, "plone.app.registry")
    logger.info("Import registry from SENAITE IMPRESS [DONE]")
