.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
    :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
    :alt: License: AGPL-3

======================================================
Sale Report: show line description instead of product
======================================================

* Extends ``sale_report_show_product_name``
* Shows the SO line description in bold on print lines, instead of the
  product name
* Orders imported from WooCommerce (``woo_commerce_ept``, order has a Woo
  instance) keep showing the product name. The WooCommerce integration is
  optional: without it, the line description is always shown

Configuration
=============
* None needed

Usage
=====
* Just print a quotation / order confirmation

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Valtteri Lattu <valtteri.lattu@futural.fi>

Maintainer
----------

.. image:: https://futural.fi/templates/tawastrap/images/logo.png
    :alt: Futural Oy
    :target: http://futural.fi/

This module is maintained by Futural Oy.
