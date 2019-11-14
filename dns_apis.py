import json, requests, re


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
            self.base_domain = re.search(r'([^\.]+\.[a-zA-Z0-9]{2,})$', fqdn).groups()[0]
        except:
            self.base_domain = fqdn
        subdomains = re.match(r'^(([-\w]+\.)*)(?:[a-z0-9\-]+\.[a-z0-9]{2,})$', fqdn, flags=re.IGNORECASE)
        try:
            # If there is a subdomain captured, get the first item from the tuple, and cut off the trailing '.' character.
            self.subdomain = subdomains.groups()[0][:-1]
        except:
            self.subdomain = None


    """ SIMPLE WRAPPER METHODS """
    # Wrapper function to call back up the instruction stack, to write to the CertbotWorker's logfile.
    def _write_to_log(self, message):
        self.logger(message)

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
# CloudFlare: TENTATIVE
# NetworkSolutions: lol

# Define the GoDaddy API Client class as an extension of the base model.
class GoDaddyAPIClient(BaseAPIClient):
    # GoDaddy base settings, which remain consistent despite changing environments.
    __GODADDY_API_BASE = 'https://api.godaddy.com/'
    __GODADDY_AUTH_HEADERS_BASE = {
        'Authorization': None, #'sso-key {}:{}'.format(API_KEY, API_SECRET),
        'Accept': 'application/json',
        'Content-Type': 'application/json',
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
        url_path = self.base_url + 'v1/domains/' + self.base_domain + '/records/TXT/_acme-challenge'
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
        # Interpret it.
        self._check_request_response(r)


    # OVERRIDE.
    # Dump request data to STDOUT for logging and debugging.
    def _dump_request_data(self, action, url, req_data):
        self._write_to_log(action + " at: " + url)
        self._write_to_log("HEADERS:")
        for key in self.base_headers.keys():
            if key == 'Authorization':
                self._write_to_log("-- " + key + ": *****************************")
            else:
                self._write_to_log("-- " + key + ": " + self.base_headers.get(key))
        self._write_to_log("DATA: " + req_data)


    # Check a requests object for things that might be awry, like a bad HTTP status code indicating error.
    def _check_request_response(self, request):
        if request.status_code == 200:
            # All is well, nothing to do.
            return None
        else:
            # There's trouble afoot. Log the problem based on the target API and action.
            return None


class CloudFlareAPIClient(BaseAPIClient):
    pass



# Instantiate client object structures based on a given keyword/dictionary-index.
DNS_API_CLIENT = {
    'godaddy': GoDaddyAPIClient,
}
