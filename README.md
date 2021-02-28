# Automatic CERTBOT Certificate Renewals
Some python-based hooks (auth and cleanup) for automating the acquisition or renewal of _Let's Encrypt_ certificates.


### Supported DNS APIs
+ [GoDaddy](https://developer.godaddy.com/)
+ [CloudFlare](https://api.cloudflare.com/#getting-started-endpoints)

The above links will take you to the "developer" page for each supported API.
You can get your **authentication tokens** there as needed.

***DISCLAIMER***: In the end and with the right configuration, this is *automatic LetsEncrypt certificate deployment and renewal*; please use it responsibly, and enjoy your free trusted SSL certificates thanks to the wonderful works of the [EFF](https://www.eff.org/). Please consider donating to their cause.


# Special Notes (Important)
+ At this time, the script is purely **DNS Validation** and does not support HTTP Validation, despite having a bit of scaffolding for it.
+ When running the "cleanup" hook for the _GoDaddy_ API, it doesn't delete the record, but instead changes its content to `null`. This is frankly annoying, and I am hoping to find a fix soon to clean this up. It's not necessarily a _problem_ though because the API object can UPDATE records, and doesn't have to worry about whether or not the record already exists.


# Prerequisites
+ A Linux operating system, with a knowledgeable operator.
+ Python version 3+ installed.
+ DNS managed through either **GoDaddy** or **CloudFlare**, or both.
+ [Certbot](https://certbot.eff.org/) installed and included in your system's `PATH`.
+ ~~Install the [requests](https://github.com/psf/requests) package with pip: `pip install requests`.~~
+ Keep the Shell scripts `*.sh` in the same directory _relative_ to the `main.py` python script. **DO NOT MOVE THEM SEPARATELY.**


# TODOs
+ [X] Add support for the _CloudFlare_ DNS API.
+ [ ] Add GoDaddy record _deletion_, and stop just inserting 'null' into the record.
+ [ ] Add HTTP automation.
+ More support for other DNS providers will be added in the future, as the APIs are integrated and tested. I don't have a list at this time.


# How To Use
### Configuring the settings.py file
Navigate to your new `settings.py` file, and you will be presented with a set of options to configure based on your scenario.
```
# Manual API access information. DO NOT SHARE THIS INFORMATION WITH ANYONE ELSE.
#  This information is available from your DNS provider.
DNS_API_KEYCHAIN = {
    'godaddy' : {
        'API_KEY': 'exampleKey',
        'API_SECRET': 'exampleSecretKey',
    },
    'cloudflare' : {
        'API_EMAIL': '',
        'API_KEY': '',
    },
}

[ . . . ]

DNS_API_TARGET = 'godaddy'
LOGGING_DIR = '/tmp/'
DEBUG = False
DNS_UPDATE_TIMER = 30
```

### Notes on the above
+ The `settings.py` file contains detailed comments for each field so you can read as you configure the module to your use-case.
+ The _DNS API keychain_ contains all of the authentication-related information for the target provider's API.
+ When you configure the **DNS_API_TARGET** in the _settings.py_ file, ensure that you've selected the proper API for the domains you're processing, or else it will not work.


### Applying the hooks
When obtaining new certificates (or renewing) with Certbot, you can use the hooks like so:
```
certbot certonly --manual --preferred-challenges=dns --manual-public-ip-logging-ok \
   --manual-auth-hook /path/to/cb-auth.sh --manual-cleanup-hook /path/to/cb-cleanup.sh \
   -d [COMMA-DELIMITED-DOMAIN(S)]
```
**PLEASE NOTE**: The above command automatically consents that you're okay with your public IP being logged with Let's Encrypt in the transaction!

### Alternative (Better) Method
For more automation, one could use the `renewals.txt` file with the `run.sh` wrapper script in combination to provide set-it-and-forget-it certificate renewals.

Here's a sample of that:

***renewals.txt***: `mydomain.com,sub.mydomain.com,woah.someotherdomain.net,mail.someother.org`

***[Your cron or other task scheduler]***:
```
# Automatically renew any domain in the RENEWALS.TXT file, if it's within 25 days of expiry.
00 08 * * *    /root/certbot_auto/run.sh "AUTO" 25
```
