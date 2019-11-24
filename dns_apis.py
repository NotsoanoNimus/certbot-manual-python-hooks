#!/bin/python3
#
# dns_apis.py
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
""" DNS_APIS.PY - A 'library' file that defines all API clients used by the CertbotWorker in main.py. """
import json, requests, re


# These extra variables here are not intended to be configured as a "setting".
# The prefix prepended to all TXT records required by Certbot DNS validation.
CERTBOT_PREFIX = '_acme-challenge'
# An array of header keys to obscure in any script output, whether or not DEBUG is True.
OBSCURED_HEADERS = [
    'Authorization', 'X-Auth-Key',
]

""" A Base Class for all DNS API implementations. """
class BaseAPIClient:
    """ Construct a base class. This method should be called in all child classes via a super() call. """
    # Object instantiation.
    def __init__(self, base_url, base_headers, api_keychain, fqdn, certbot_token, logger):
        self.base_url = base_url
        self.base_headers = base_headers
        self.__api_keychain = api_keychain
        self.certbot_token = certbot_token
        self.domain = fqdn
        self.logger = logger
        try:
            # Get the base fqdn: the root domain without any subdomain information.
            self.base_domain = re.search(r'([^\.]+\.[a-zA-Z0-9]{2,})$', fqdn).groups()[0]
        except:
            self.base_domain = fqdn
        subdomains = re.match(r'^(([-\w]+\.)*)(?:[a-z0-9\-]+\.[a-z0-9]{2,})$', fqdn, flags=re.IGNORECASE)
        try:
            # If there is a subdomain captured, get the first item from the tuple, and cut off the trailing '.' character.
            self.subdomain = subdomains.groups()[0][:-1]
        except:
            self.subdomain = None

    # Check a requests object for things that might be awry, like a bad HTTP status code indicating error.
    def _check_request_response(self, response, api_response_table):
        # Log a message based on the status code.
        self._write_to_log("[REQUEST STATUS (CODE {})] ".format(response.status_code) +
            api_response_table.get(response.status_code, 0))
        # The Requests model for status code interpretation has a __bool__() override for this truthy which
        #  returns a True in a conditional, provided the HTTP status code in the response is between 200 and 400.
        if response:
            # All is well, nothing to do.
            return True
        else:
            # There's trouble afoot. Send back a notification that the status code indicates failure.
           return False

    # Dump the contents of the given response, if DEBUG is True (meaning it's never logged in the file; only STDOUT).
    def _dump_response_data(self, response):
        if response is not None:
            self._write_to_log("[RESPONSE DATA (plain-text)] " + response, debug_only=True)

    # Dump request data to STDOUT for logging and debugging.
    def _dump_request_data(self, action, url_path, req_data=None):
        self._write_to_log("{} at: {}".format(action, url_path))
        # Output the headers (but hide the key).
        self._write_to_log("HEADERS:")
        for key in self.base_headers.keys():
            if key in OBSCURED_HEADERS:
                self._write_to_log("-- " + key + ": *****************************")
            else:
                self._write_to_log("-- " + key + ": " + self.base_headers.get(key))
        # If defined, write out the payload information.
        if req_data is not None:
            self._write_to_log("PAYLOAD:" + req_data)


    """ SIMPLE WRAPPER METHODS """
    # Wrapper function to call back up the instruction stack, to write to the CertbotWorker's logfile.
    def _write_to_log(self, message, debug_only=False):
        self.logger(message, debug_only)

    """ GETTER METHODS """
    # Simple getter for self.base_url.
    def get_base_url(self):
        return self.base_url
    # Simple getter for self.base_headers.
    def get_base_headers(self):
        return self.base_headers

    """ OVERRIDDEN METHODS """
    # Update or create a DNS record based on the instance extension of the base API client. Requires override to use.
    def add_or_update_record(self, set_null=False):
        raise NotImplementedError




""" Define BaseAPIClient subclasses for specific DNS APIs. """
# GoDaddy: COMPLETE (deletion methods in progress, however)
# CloudFlare: COMPLETE
# NetworkSolutions: lol

# Define the GoDaddy API Client class as an extension of the base model.
class GoDaddyAPIClient(BaseAPIClient):
    # GoDaddy base settings, which remain consistent despite changing environments.
    __GODADDY_API_BASE = 'https://api.godaddy.com/'
    __GODADDY_AUTH_HEADERS_BASE = {
        'Authorization' : None, #'sso-key {}:{}'.format(API_KEY, API_SECRET),
        'Accept'        : 'application/json',
        'Content-Type'  : 'application/json',
    }
    # API response-parsing table. Indexes a response based on the HTTP status code.
    #  These are from the API docs for PUT requests of the type this class does in its add_or_update function.
    #  See: https://developer.godaddy.com/doc/endpoint/domains#/
    __GODADDY_RESPONSE_TABLE = {
        0   : 'The response to the request was not understood. Failure is assumed.',
        200 : 'The request was successful.',
        400 : 'The request was malformed.',
        401 : 'The authentication information provided with the request was not valid.',
        403 : 'The authenticated user does not have access to issue the request.',
        404 : 'The targeted resource could not be found.',
        422 : 'The request object does not fulfill the GoDaddy record schema for this type.',
        429 : 'Too many requests at this time. Please try again later.',
        500 : 'Internal server error: GoDaddy could not process the request.',
        504 : 'The gateway timed out.',
    }

    def __init__(self, api_keychain, fqdn, certbot_token, logger):
        # Flesh out the base class.
        super().__init__(self.__GODADDY_API_BASE, self.__GODADDY_AUTH_HEADERS_BASE,
            api_keychain, fqdn, certbot_token, logger)
        # Define GoDaddy-specific headers based on the given information.
        self.base_headers['Authorization'] = 'sso-key {}:{}'.format(api_keychain.get('API_KEY'), api_keychain.get('API_SECRET'))


    # OVERRIDE.
    # Updates (or creates) a DNS record with a request via the GoDaddy API.
    #  If the set_null variable is True, then for now this will update the ACME record to 'null' text.
    #  This is because a method to directly delete GoDaddy DNS records via the API has not yet been implemented in this script.
    def add_or_update_record(self, set_null=False):
        url_path = self.base_url + "v1/domains/{}/records/TXT/{}".format(self.base_domain, CERTBOT_PREFIX)
        if self.subdomain is not None:
            url_path += '.' + self.subdomain
        # Build it.
        payload = {
            'data': self.certbot_token if set_null == False else 'null',
            'ttl': 3600
        }
        request_data = json.dumps([payload])
        # Log it.
        self._dump_request_data("Writing DNS record", url_path, request_data)
        # Request it.
        r = requests.put(url=url_path, data=request_data, headers=self.base_headers)
        # Interpret it. Return the value of the request's success.
        return self._check_request_response(r, self.__GODADDY_RESPONSE_TABLE)



# Define the CloudFlare API Client class as an extension of the base model.
class CloudFlareAPIClient(BaseAPIClient):
    # CloudFlare base settings for API Client instantiation.
    __CLOUDFLARE_API_BASE = "https://api.cloudflare.com/client/v4/"
    __CLOUDFLARE_AUTH_HEADERS_BASE = {
        'X-Auth-Email' : None,   #filled in by the API Keychain from settings
        'X-Auth-Key'   : None,   #same as above
        'Content-Type' : 'application/json',
        'Accept'       : 'application/json',
    }
    # Index an appropriate response based on the HTTP status code in the response to the request.
    #  See: https://api.cloudflare.com/#getting-started-responses
    __CLOUDFLARE_RESPONSE_TABLE = {
        0   : 'The response to the request could not be understood. Assuming request failure.',
        200 : 'The request was successful.',
        304 : 'The request was successful, but nothing has been modified.',
        400 : 'The request was invalid or malformed.',
        401 : 'The authenticated user does not have permission to access or modify the requested resource.',
        403 : 'The request did not include information to authenticate a user.',
        405 : 'The request used an invalid HTTP method to access or modify the requested resource.',
        415 : 'The response is not a valid JSON object.',
        429 : 'Too many requests at this time. Please try again later.',
    }
    # Define base parameters for CloudFlare that are sent with GET requests.
    __CLOUDFLARE_BASE_REQUEST_PARAMS = "status=active&page=1&per_page=20&order=status&direction=desc&match=all"

    # Initialization.
    def __init__(self, api_keychain, fqdn, certbot_token, logger):
        # Flesh out the base class.
        super().__init__(self.__CLOUDFLARE_API_BASE, self.__CLOUDFLARE_AUTH_HEADERS_BASE,
            api_keychain, fqdn, certbot_token, logger)
        # Define CloudFlare-specific authentication headers based on the given information in SETTINGS.PY.
        self.base_headers['X-Auth-Email'] = api_keychain.get('API_EMAIL')
        self.base_headers['X-Auth-Key'] = api_keychain.get('API_KEY')


    # Generic method to run a query for CloudFlare-specific items (like zone or record IDs).
    def _get_object_id(self, message, url):
        # Log the requested URL.
        self._dump_request_data(message, url)
        # Run the request.
        r = requests.get(url=url, headers=self.base_headers)
        # Log the response (if DEBUG is enabled).
        self._dump_response_data(r.text)
        # Interpret the response. Return the first object's ID-key value from the response, if defined.
        if self._check_request_response(r, self.__CLOUDFLARE_RESPONSE_TABLE) is True:
            try:
                # Extract the ID from the response (r) and return it from the function.
                return json.loads(r.text)['result'][0]['id']
            except:
                # Something went wrong, return None.
                #  This usually means one of the accessors into the JSON object weren't defined (i.e. invalid request).
                return None
        else:
            return None


    # Get the record_id associated with the TXT record for the (sub)domain being targeted (if it's defined).
    def get_target_record_id(self):
        # Build the GET request.
        #  NOTE: Not including the base params. The ZoneID is already defined if this point is reached.
        url_path = self.base_url + 'zones/{}/dns_records?name={}&type=TXT'.format(
            self.zone_id, "{}.{}".format(CERTBOT_PREFIX, self.domain))
        return self._get_object_id("Requesting record ID for the target (sub)domain", url_path)


    # Get the CloudFlare ZoneID for the target domain.
    def get_zone_id(self):
        # Build the GET request.
        #  NOTE: Not including the base params to the GET request at this time. It was breaking many requests in testing.
        url_path = self.base_url + 'zones?name={}'.format(self.base_domain, "&" + self.__CLOUDFLARE_BASE_REQUEST_PARAMS)
        return self._get_object_id("Requesting zone data", url_path)


    # OVERRIDE.
    # Updates (or creates) a DNS record with the CloudFlare API.
    #  If the set_null variable is True, then the _acme-challenge TXT record for the (sub)domain will be targeted and removed.
    def add_or_update_record(self, set_null=False):
        # Firstly, get the ZoneID and check that it could be captured.
        self.zone_id = self.get_zone_id()
        if self.zone_id is None:
            # There was a problem retrieving the ZoneID from CloudFlare. Error out.
            self._write_to_log("There was an error retrieving the ZoneID for the target domain.")
            return False
        else:
            # Log the zone_id and continue.
            self._write_to_log("CloudFlare ZoneID for the target: " + self.zone_id)
        # Set the target record's ID within the client object.
        #  This is a requirement to delete the record for the given FQDN.
        #  BUT it's also a requirement to check if there's already one in the way for 'auth' hooks.
        self.record_id = self.get_target_record_id()
        # Take an add or delete route based on whether or not set_null is set to True.
        if set_null is False:
            ##### RECORD CREATION SECTION #####
            # Set up the request.
            target_url = self.base_url + "zones/{}/dns_records".format(self.zone_id)
            target_record = "{}.{}".format(CERTBOT_PREFIX, self.domain)
            # Build the payload.
            payload = {
                'type' : 'TXT',
                'name' : target_record,
                'content' : self.certbot_token,
                'ttl'  : 120,
            }
            request_data = json.dumps(payload)
            # Log it.
            self._dump_request_data("Writing DNS record", target_url, request_data)
            # Request it.
            # If a record ID is already defined for the (sub)domain, set the request type to UPDATE instead of POST.
            if self.record_id is None:
                r = requests.post(url=target_url, data=request_data, headers=self.base_headers)
            else:
                r = requests.put(url="{}/{}".format(target_url, self.record_id), data=request_data, headers=self.base_headers)
            # Interpret it.
            return self._check_request_response(r, self.__CLOUDFLARE_RESPONSE_TABLE)
        else:
            ##### RECORD DELETION SECTION #####
            # If the record_id isn't defined for the target domain, there's no way we can safely delete it.
            #  It's better to fail here than to try and find the record ID and deleting a bunch of the wrong records.
            if self.record_id is None:
                return False
            # Set up the request.
            target_url = self.base_url + "zones/{}/dns_records/{}".format(self.zone_id, self.record_id)
            # No need to configure a payload.
            # Log the request though.
            self._dump_request_data("Deleting DNS record", target_url)
            # Request it.
            r = requests.delete(url=target_url, headers=self.base_headers)
            # Interpret it.
            return self._check_request_response(r, self.__CLOUDFLARE_RESPONSE_TABLE)



# Instantiate client object structures based on a given keyword/dictionary-index.
DNS_API_CLIENT = {
    'godaddy': GoDaddyAPIClient,
    'cloudflare' : CloudFlareAPIClient,
}
