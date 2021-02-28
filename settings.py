#!/bin/python3
#
# settings.py
#
#   Contributors:
#       Notsoano Nimus <github@xmit.xyz>
#   Repo:
#       https://github.com/NotsoanoNimus/certbot-manual-python-hooks
#   Description:
#       Automatically set up Certbot authorizations for new and renewing SSL certificates from LetsEncrypt.
#       Parameters in the accompanying settings.py file are required to be set before running these hooks.
#
######################################################################################
# Copyright (C) 2021 @NotsoanoNimus on GitHub, as a free software project
#  licensed under GNU GPLv3.
#
# This program is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
#  this program. If not, see https://www.gnu.org/licenses/.
######################################################################################
#
#
#
""" SETTINGS.PY - Manual settings for the Certbot auth-hook API to work fluidly. """


# Manual API access information. DO NOT SHARE THIS INFORMATION WITH ANYONE ELSE.
#  This information is available from your DNS provider. Please see the README file.
DNS_API_KEYCHAIN = {
    'godaddy' : {
        'API_KEY': '',
        'API_SECRET': '',
    },
    'cloudflare' : {
        'API_EMAIL': '',
        'API_KEY': '',
    },
}


# The target DNS service for which an API client will be constructed and used.
# TODO: Find a way to automate this on a per-domain basis, or pass it in somehow.
#        An easy idea to toy with could be K:V pairs of DOMAIN:PROVIDER in the `renewals.txt` file.
# Options:
#   godaddy, cloudflare
DNS_API_TARGET = ''


# Where to store logs for the DNS API transactions.
LOGGING_DIR = '/tmp/'
# Enable debugging mode? Shortens timers and logs all information to STDOUT instead of a logfile.
DEBUG = False
# How long (in seconds) to wait for DNS records to update before handing control back to certbot.
#  This field has a maximum value of 600 seconds and a minimum value of 30.
DNS_UPDATE_TIMER = 30
