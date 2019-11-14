# certbot-manual-dns-python-hooks
Some python-based hooks (auth and cleanup) for DNS-based manual LetsEncrypt certificates.

These hooks will allow you to set up a cron-job to automatically renew your LetsEncrypt certificates with the certbot tool.


# Special Notes (Important)
+ More support for other DNS providers will be added in the future, as the APIs are integrated.
+ _14 Nov. 2019_ : **CloudFlare** support is not yet functional.
+ When running the "cleanup" hook for the _GoDaddy_ API, it doesn't delete the record, but instead changes its content to `null`. This is frankly annoying, and I am hoping to find a fix soon to clean this up. It's not necessarily a _problem_ though because the API object can UPDATE records, and doesn't have to worry about whether or not the record already exists. :)


# Prerequisites
+ A Linux operating system.
+ Python3 installed.
+ DNS managed through either **GoDaddy** or **CloudFlare**, or both.
+ [Certbot](https://certbot.eff.org/) installed.
+ Install the [requests](https://github.com/psf/requests) package with pip: `pip install requests`
+ Keep the Shell scripts `*.sh` in the same directory as the `main.py` python script. **DO NOT SEPARATE THEM.**

# Getting API Keys
+ [GoDaddy](https://developer.godaddy.com/)
+ [CloudFlare](https://api.cloudflare.com/#getting-started-endpoints)


# How To Use
### Configuring the settings.py file
Navigate to your new `settings.py` file, and you will be presented with a fully-commented set of options to configure based on your scenario.
```
# Manual API access information. DO NOT SHARE THIS INFORMATION WITH ANYONE ELSE.
#  Each key in the below dictionary will have a comment stating which DNS API
#  fields are required for a certain service.
DNS_API_KEYCHAIN = {
    'API_KEY': 'MY-CLOUDFLARE-OR-GODADDY-API-KEY',   #CloudFlare & GoDaddy
    'API_SECRET': 'MY-GODADDY-API-SECRET',   #GoDaddy only
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
```
The _keychain_ contains all of the authentication-related information for the target provider's API.

In the above case, you'll see that the `API_KEY` and `API_SECRET` fields are the only ones populated, because the target API will be _GoDaddy_ in my example, as evidenced by the `DNS_API_TARGET` field. If I was instead targeting _CloudFlare_, then only `API_KEY` and `API_EMAIL` would be necessary.

**NOTE**: In future revisions, it is planned to somehow allow a mix of target APIs that would obsolete the `DNS_API_TARGET` so that parts of the keychain can be dynamically used. This will be addressed as it's developed.

### Certbot Certificates (using the hooks)
When obtaining new certificates with Certbot, you can use the hooks like so:
```
certbot certonly --manual --preferred-challenges=dns --manual-public-ip-logging-ok \
   --manual-auth-hook /path/to/cb-auth.sh --manual-cleanup-hook /path/to/cb-cleanup.sh -d [DOMAIN(S)]
```
The **DOMAINS** piece is important here: this is a _comma-delimited_ list of domains/Common-Names you'd like to get/renew a certificate for.

You can set this up as a monthly cron-job, or run it manually with a command-line alias, there are plenty of options.

In the end and with the right configuration, this is **automatic LetsEncrypt certificate deployment and renewal**, so please use this responsibly.


# TODOs
+ [ ] Add support for the _CloudFlare_ DNS API.
