.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================
Sale Report: Information Section Width Fix
==========================================

* Adds wrapping support for the "informations" section on SO print which
  can get squished together, if many modules add new elements to the
  section

Configuration
=============
* None needed

Usage
=====
* Just print a Sale Order

Known issues / Roadmap
======================
* Consider if this functionality could be applied to all prints with
  a single module. Simply targeting #informations would break the layout of
  the section at least PO and Invoice prints, which is why this module
  currently applies the style change to the Sale Order print only.
* Flexbox wrapping does not work with current wkhtmltopdf, which is the reason this
  workaround is used instead of a simple display: flex.

Credits
=======

Contributors
------------

* Timo Talvitie <timo.talvitie@futural.fi>

Maintainer
----------

.. image:: http://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: http://futural.fi/

This module is maintained by Futural Oy
