.. image:: https://raw.githubusercontent.com/senaite/senaite.impress/master/static/logo_pypi.png
   :target: https://github.com/senaite/senaite.impress#readme
   :alt: senaite.impress
   :height: 128

*Publication of HTML/PDF Reports in SENAITE*
============================================

.. image:: https://img.shields.io/pypi/v/senaite.impress.svg?style=flat-square
   :target: https://pypi.python.org/pypi/senaite.impress

.. image:: https://img.shields.io/github/issues-pr/senaite/senaite.impress.svg?style=flat-square
   :target: https://github.com/senaite/senaite.impress/pulls

.. image:: https://img.shields.io/github/issues/senaite/senaite.impress.svg?style=flat-square
   :target: https://github.com/senaite/senaite.impress/issues

.. image:: https://img.shields.io/badge/README-GitHub-blue.svg?style=flat-square
   :target: https://github.com/senaite/senaite.impress#readme

.. image:: https://img.shields.io/badge/Built%20with-%E2%9D%A4-red.svg
   :target: https://github.com/senaite/senaite.impress

.. image:: https://img.shields.io/badge/Made%20for%20SENAITE-%E2%AC%A1-lightgrey.svg
   :target: https://www.senaite.com


About
=====

SENAITE IMPRESS is basically a rendering engine for HTML documents to PDF. It
supports any kind of international paperformat with their corresponding paper
dimensions, portrait and landscape orientation and merging of multiple PDFs to
one document.


Installation
============

Please follow the installations instructions for `Plone 4`_ and
`senaite.lims`_.

To install SENAITE IMPRESS, you have to add `senaite.impress` into the
`eggs` list inside the `[buildout]` section of your
`buildout.cfg`::

   [buildout]
   parts =
       instance
   extends =
       http://dist.plone.org/release/4.3.19/versions.cfg
   find-links =
       http://dist.plone.org/release/4.3.19
       http://dist.plone.org/thirdparty
   eggs =
       Plone
       Pillow
       senaite.lims
       senaite.impress
   zcml =

   [instance]
   recipe = plone.recipe.zope2instance
   user = admin:admin
   http-address = 127.0.0.1:8080
   eggs =
       ${buildout:eggs}
   zcml =
       ${buildout:zcml}

   [versions]
   setuptools =
   zc.buildout =


**Note**

The above example works for the buildout created by the unified
installer. If you however have a custom buildout you might need to add
the egg to the `eggs` list in the `[instance]` section rather than
adding it in the `[buildout]` section.

Also see this section of the Plone documentation for further details:
https://docs.plone.org/4/en/manage/installing/installing_addons.html

**Important**

For the changes to take effect you need to re-run buildout from your
console::

   bin/buildout


Installation Requirements
-------------------------

The following versions are required for SENAITE IMPRESS:

-  Plone 4.3.19
-  senaite.lims >= 1.3.0


.. _Plone 4: https://docs.plone.org/4/en/manage/installing/index.html
.. _senaite.lims: https://github.com/senaite/senaite.lims#installation
