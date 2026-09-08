# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Author: Aktiv Software.
# mail: odoo@aktivsoftware.com
# Copyright (C) 2015-Present Aktiv Software PVT. LTD.
# Contributions:
# Aktiv Software
#       - Juhi Updadhyay
#       - Zahir kagdi
#       - Yuvrajsinh Rathod
#       - Shakib Sheikh
#       - Pravin prajapati
{
    "name": "Clarico Enhancement",
    "version": "18.0.1.3.3",
    "category": "Website",
    "author": "Aktiv Software",
    "company": "Aktiv Software",
    "website": "www.aktivsoftware.com",
    "summary": "Adds a new variable is_attributes containing the number of attribute "
               "values on the product.Replaces Odoo's default variant-display condition"
               "with a custom one.Shows variant selectors only when the product has at"
               "least one attribute value.",
    "depends": ["theme_clarico_vega"],
    "data": [
        "templates/product.xml",
        "templates/product_variant_template.xml",
    ],
    "license": "OPL-1",
    "installable": True,
    "application": True,
    "auto_install": False,
}
