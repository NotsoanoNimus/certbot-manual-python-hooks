#!/bin/python3
#
# cb-hook.py
#
#   Automatically set up Certbot authorizations for new and renewing SSL certificates from LetsEncrypt.
#   The only required parameters to be set are as follows:
#       API_KEY: The API access key given to you by your provider (if using DNS challenges)
#       API_SECRET: The API secret key given to you by your provider (again, if using DNS challenges)
#
import sys, os, re, requests, json, datetime, time
from dns_apis import DNS_API_CLIENT, GoDaddyAPIClient, CloudFlareAPIClient
from settings import *
#from worker import CertbotWorker


""" Constants, classes, helper methods, and other definitions. """

# Define a certbot class to hold methods and information about certbot validation attempts.
class CertbotWorker:
    # Define a constructor that initializes instance fields based on the information provided.
    def __init__(self, fqdn, validation_code, hook_type=None, auth_type=None, http_token=None):
        self.is_cleanup = (hook_type == 'cleanup')
        self.type = auth_type
        self.token = http_token
        self.api = DNS_API_CLIENT[DNS_API_TARGET](DNS_API_KEYCHAIN, fqdn, validation_code, self._write_to_log)
        self.log_file = open(LOGGING_DIR + ('/certbot-{}.log'.format(self.api.base_domain)), 'a+')
        # Take note of the request and worker object instantiation.
        self._write_to_log("CertbotWorker constructed [%s]: %s (%s): %s, %s, %s" %
            (hook_type, fqdn, self.api.base_domain, validation_code, auth_type, http_token if http_token is not None else '{no-http-token}'))

    # A wrapper/helper method to output information to the domain's logfile.
    def _write_to_log(self, message):
        if DEBUG == False:
            print("{} ::: {}".format(datetime.datetime.now(), message), file=self.log_file)
        else:
            print("[DEBUG] {} ::: {}".format(datetime.datetime.now(), message))

    # DNS validation calls (wrapper method for the worker).
    def dns_validation(self):
        # Create the record, or clean it up.
        self.api.add_or_update_record(set_null=self.is_cleanup)
        # Sleep/Wait at least 30 seconds for record propagation (when it's an AUTH hook type).
        if self.is_cleanup == False:
            if DEBUG == False:
                time.sleep(30)
            else:
                time.sleep(2)
        return None

    # HTTP validation calls (not yet implemented).
    def http_validation(self):
        return None




""" Define the main function used to run the auth/cleanup hooks. """
def main():
    # Check to ensure the provided command-line parameters include the self-referential ($0) and the Certbot info.
    if len(sys.argv) != 2:
        sys.exit("The manual hook didn't receive the appropriate parameters. Aborting.")

    certbot_info = sys.argv[1].strip()
    # The expected Certbot parameter should be in this format: "F.Q.D.N. acme-token [dns|http] [token]"
    if not bool(re.fullmatch(r'\s*(([-\w]+\.)*([a-z0-9\-]+)\.[a-z0-9]{2,})\s+([^\s]+\s+(auth|cleanup))\s*(\s+[^\s]+\s*)?', certbot_info, flags=re.IGNORECASE)):
        sys.exit("The manual hook didn't receive the appropriate parameters. Aborting.")

    # Split the params on the whitespace characters, and instantiate a CertbotWorker class based on the length of the new array.
    cb_pms = certbot_info.split()
    if len(cb_pms) == 0 or len(cb_pms) > 4:
        sys.exit("Could not parse the certbot worker parameters. Aborting.")
    try:
        cb_obj = CertbotWorker(cb_pms[0], cb_pms[1], hook_type=cb_pms[2], 
            auth_type='dns' if len(cb_pms) == 3 else 'http', http_token=None if len(cb_pms) == 3 else cb_pms[3])
    except:
        sys.exit("Could not construct the certbot worker: the given paramters are NOT valid!")

    # Perform the validation.
    print("Using python '%s' certbot hook for domain '%s'..." % (cb_pms[2], cb_obj.api.base_domain))
    if cb_obj.type == 'dns':
        cb_obj.dns_validation()
    else:
        cb_obj.http_validation()



""" The start of the actual script processing. """
""" Only call the main method if this script is being directly executed by the interpreter. """
if __name__ == '__main__':
    main()
