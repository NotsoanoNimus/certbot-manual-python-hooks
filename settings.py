""" SETTINGS.PY - Manual settings for the Certbot auth-hook API to work fluidly. """


# Manual API access information. DO NOT SHARE THIS INFORMATION WITH ANYONE ELSE.
#  Each key in the below dictionary will have a comment stating which DNS API
#  fields are required for a certain service.
DNS_API_KEYCHAIN = {
    'API_KEY': '',   #CloudFlare & GoDaddy
    'API_SECRET': '',   #GoDaddy only
    'API_EMAIL': '',   #CloudFlare only
}


# The target DNS service for which an API client will be constructed and used..
# TODO: Find a way to automate this on a per-domain basis, or pass it in somehow.
# Options:
#   godaddy, cloudflare
DNS_API_TARGET = 'godaddy'


# Where to store logs for the DNS API transactions.
LOGGING_DIR = '/tmp/'
# Enable debugging mode? Shortens timers and logs all information to STDOUT instead of a logfile.
DEBUG = False
