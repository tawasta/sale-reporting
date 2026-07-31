##############################################################################
#
#    Author: Futural Oy
#    Copyright 2026 Futural Oy (https://futural.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################

{
    'name': 'Null sales views',
    'summary': 'Module summary for public use. This is an important part to fill!',
    'version': '17.0.1.0.0',
    'category': 'Uncategorized',
    'website': 'https://tawasta.fi',
    'author': 'Futural',
    'license': 'AGPL-3',
    'application': False,
    'installable': True,
    'external_dependencies': {
        'python': [],
        'bin': [],
    },
    'depends': [
        'sale',
    ],
    'data': [
        'security/ir.model.access.csv',
        'models/sale_report_views.xml',
    ],
    'demo': [
    ],
}

##############################################################################
#
#    AVAILABLE CATEGORIES - PLEASE REMOVE THIS AFTER SELECTING CATEGORY
#
# Accounting
# Accounting & Finance
# Account
# Account Charts
# Administration
# Appraisals
# Association
# Attendance
# Authentication
# Base
# Blog
# Company Data
# Configuration
# Connector
# Contacts
# Contract
# Contract Management
# CRM
# Discuss
# Document Management
# Documentation
# eCommerce
# Education
# Employees
# Events
# Expenses
# Extra Rights
# Extra Tools
# Finance
# Financial Management
# Gamification
# Generic
# Hardware Drivers
# Health
# Holidays
# HR
# Human Resources
# Human Resources Survey
# Inventory
# Invoicing
# Invoicing & Payments
# Lead Automation
# Links
# Localization
# Mail
# Maintenance
# Manufacturing
# Marketing
# Mass Mailing
# Monitoring
# MRP
# Other
# Other Extra Rights
# Partner Management
# Payment Acquirer
# Payroll
# Personalization
# Planner
# Point of Sale
# Portal
# Procurements
# Product
# Productivity
# Project
# Projects & Services
# Purchase
# Purchase Workflow
# Purchases
# Recruitment
# Reporting
# Sale
# Sale Management
# Sale Workflow
# Sales
# Server Tools
# Social
# Social Network
# Specific Industry Applications
# Stock
# Survey
# Technical
# Technical Settings
# Tests
# Theme
# Timesheets
# Tools
# User roles
# Warehouse
# Web
# Website
#
##############################################################################
