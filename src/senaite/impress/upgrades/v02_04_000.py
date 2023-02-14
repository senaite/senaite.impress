# -*- coding: utf-8 -*-

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
