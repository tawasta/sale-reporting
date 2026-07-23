.. image:: https://img.shields.io/badge/licence-AGPL--3-blue.svg
   :target: http://www.gnu.org/licenses/agpl-3.0-standalone.html
   :alt: License: AGPL-3

==================================
Sale Order Report Hide Lines
==================================

* Hide product lines or product line prices from sale order reports.
* Show only section/header lines and hide product lines.

Configuration
=============
* Install module
* Configure the report line mode in the sale order report wizard:
  * 'normal' (default) - show all lines and prices
  * 'no_lines' - hide all product lines and prices
  * 'no_line_prices' - show product lines but hide all price-related information
  * 'only_headers' - show section/header lines, hide product and combo lines

Usage
=====
* If you have a setting set to print no lines, but need to print 
a specific report WITH lines, you can adjust the sale order Other info settings 
to enable lines or line prices to show for that specific report.

Known issues / Roadmap
======================
\-

Credits
=======

Contributors
------------

* Joonas Lahtinen <joonas.lahtinen@futural.fi>

Maintainer
----------

.. image:: http://futural.fi/templates/tawastrap/images/logo.png
   :alt: Futural Oy
   :target: http://futural.fi/

This module is maintained by Futural Oy