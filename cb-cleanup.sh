#!/bin/bash
echo -e "Running cleanup hook...\n"
echo "Domain: $CERTBOT_DOMAIN"
echo "Validation: $CERTBOT_VALIDATION"
echo "Token (http-only): $CERTBOT_TOKEN"


# Any tasks to run BEFORE the cleanup hook, do here...

##########


# Run the python 'cleanup' hook from "main.py" in the current directory.
python3 "./main.py" "$CERTBOT_DOMAIN $CERTBOT_VALIDATION cleanup $CERTBOT_TOKEN"


# Any tasks to run AFTER the cleanup hook, do here...

##########


# Output success.
echo "Updated LE certificates for ${CERTBOT_DOMAIN}."
