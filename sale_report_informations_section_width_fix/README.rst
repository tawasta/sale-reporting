.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==========================================
Sale Report: Information Section Width Fix
==========================================

* Fixes the wrapping of the "informations" section on SO print which
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

Credits
=======

Contributors
------------

* Timo Talvitie <timo.talvitie@tawasta.fi>

Maintainer
----------

.. image:: http://tawasta.fi/templates/tawastrap/images/logo.png
   :alt: Oy Tawasta OS Technologies Ltd.
   :target: http://tawasta.fi/

This module is maintained by Oy Tawasta OS Technologies Ltd.
