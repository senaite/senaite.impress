# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

version = "2.1.0"

with open("docs/About.rst", "r") as fh:
    long_description = fh.read()

with open("docs/Changelog.rst", "r") as fh:
    long_description += "\n\n"
    long_description += "Changelog\n"
    long_description += "=========\n\n"
    long_description += fh.read()

setup(
    name="senaite.impress",
    version=version,
    description="Publication of HTML/PDF Reports in SENAITE",
    long_description=long_description,
    # long_description_content_type="text/markdown",
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
        "Framework :: Plone",
        "Framework :: Zope2",
        "Programming Language :: Python",
        "Development Status :: 5 - Production/Stable",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords="",
    author="RIDING BYTES & NARALABS",
    author_email="senaite@senaite.com",
    url="https://github.com/senaite/senaite.impress",
    license="GPLv2",
    packages=find_packages("src", exclude=["ez_setup"]),
    package_dir={"": "src"},
    namespace_packages=["senaite"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
        # The final version of Beautiful Soup to support Python 2 was 4.9.3.
        "beautifulsoup4==4.9.3",
        "CairoSVG==1.0.20",
        "cairocffi<1.0.0",
        # Python 2.x is not supported by WeasyPrint v43
        'WeasyPrint==0.42.3',
        # tinycss2 >= 1.0.0 does not support Python 2.x anymore
        "tinycss2<1.0.0",
        # cssselect2 0.3.0 does not support Python 2.x anymore
        "cssselect2<0.3.0",
        # pyphen 0.12.0 does not support Python 2.x anymore
        "pyphen==0.11.0",
    ],
    extras_require={
        "test": [
            "Products.PloneTestCase",
            "Products.SecureMailHost",
            "plone.app.testing",
            "unittest2",
        ]
    },
    entry_points="""
      # -*- Entry points: -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
)
