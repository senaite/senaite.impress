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

import doctest
from os.path import join

import unittest2 as unittest
from pkg_resources import resource_listdir
from senaite.impress.tests.base import SimpleTestCase
from Testing import ZopeTestCase as ztc

PACKAGE_NAME = "senaite.impress"

flags = doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE | doctest.REPORT_NDIFF


def is_doctest_file(file_name):
    """Checks if the file name is a reStructuredText doctest
    """
    return file_name.endswith(".rst")


def get_doctest_files():
    """Returns the paths of the doctest files relative to this module
    """
    files = resource_listdir(PACKAGE_NAME, "tests/doctests")
    files = filter(is_doctest_file, files)
    return map(lambda file_name: join("doctests", file_name), sorted(files))


def get_doctest_suite(doctest_file):
    """Returns the test suite for a single doctest file
    """
    return ztc.ZopeDocFileSuite(
        doctest_file,
        test_class=SimpleTestCase,
        optionflags=flags)


def test_suite():
    suite = unittest.TestSuite()
    suite.addTests(map(get_doctest_suite, get_doctest_files()))
    return suite
