#!/bin/python3
#
# certbot_worker.py
#
#   Contributors:
#       Notsoano Nimus <postmaster@thestraightpath.email>
#   Repo:
#       https://github.com/NotsoanoNimus/certbot-manual-python-hooks
#   Description:
#       Automatically set up Certbot authorizations for new and renewing SSL certificates from LetsEncrypt.
#       Parameters in the accompanying settings.py file are required to be set before running these hooks.
#
######################################################################################
# Copyright (C) 2019 "Notsoano Nimus", as a free software project
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
""" CERTBOT_WORKER.PY - Defines a class (and related methods) for interactions with certbot. """
import datetime, time
from dns_apis import DNS_API_CLIENT
from settings import *


# Define a certbot class to hold methods and information about certbot validation attempts.
class CertbotWorker:
    # Define a constructor that initializes instance fields based on the information provided.
    def __init__(self, fqdn, validation_code, hook_type=None, auth_type=None, http_token=None):
        self.is_cleanup = (hook_type == 'cleanup')
        self.hook_type = hook_type
        self.type = auth_type
        self.token = http_token
        self.api = DNS_API_CLIENT[DNS_API_TARGET](
            DNS_API_KEYCHAIN[DNS_API_TARGET],
            fqdn, validation_code, self._write_to_log
        )
        self.log_file = open(LOGGING_DIR + ('/certbot-{}.log'.format(self.api.base_domain)), 'a+')
        # Take note of the request and worker object instantiation.
        self._write_to_log("CertbotWorker constructed [%s]: %s (%s): %s, %s, %s" %
            (hook_type, fqdn, self.api.base_domain, validation_code, auth_type, http_token if http_token is not None else '{no-http-token}'))
    # A wrapper/helper method to output information to the domain's logfile.
    def _write_to_log(self, message, debug_only=False):
        if DEBUG is False and debug_only is False:
            print("{} ::: {}".format(datetime.datetime.now(), message), file=self.log_file)
        elif DEBUG is True:
            print("[DEBUG] {} ::: {}".format(datetime.datetime.now(), message))
    # DNS validation calls (wrapper method for the worker).
    def dns_validation(self):
        # Write the type of validation request (auth/cleanup).
        self._write_to_log("=== New validation request (type: {}) ===".format(self.hook_type))
        # Create the record, or clean it up.
        dns_success = self.api.add_or_update_record(set_null=self.is_cleanup)
        # Sleep/Wait at least 30 seconds for record propagation (when it's an AUTH hook type).
        if self.is_cleanup == False and dns_success == True:
            if DEBUG == False:
                # Set the wait time to 30 seconds if the settings.py configuration is out of range.
                wait_seconds = DNS_UPDATE_TIMER if DNS_UPDATE_TIMER >= 30 or DNS_UPDATE_TIMER <= 600 else 30
                print("Waiting {} seconds for the DNS changes to propagate. Please be patient.".format(wait_seconds))
                time.sleep(wait_seconds)
            else:
                time.sleep(2)
        elif dns_success == False:
            # If the DNS validation failed in any way, let the user know about it.
            failure_notification = "DNS validation has failed for domain '{}'".format(self.api.domain)
            self._write_to_log(failure_notification)
            # Also print it (no matter what) for the end-user to see. Under normal circumstances, the above should just log it,
            #  but the user running the certbot command needs to know what happened right away.
            print("[FAILURE] " + failure_notification)
        if dns_success is True:
            print("[SUCCESS] The DNS changes were made for domain '{}'".format(self.api.domain))
        return dns_success
    # HTTP validation calls (not yet implemented).
    def http_validation(self):
        return None
