#!/bin/bash
echo -e "Running auth hook...\n"
echo "Domain: $CERTBOT_DOMAIN"
echo "Validation: $CERTBOT_VALIDATION"
echo "Token (http-only): $CERTBOT_TOKEN"


# Any tasks needed BEFORE running the validation, do here...

##########


# Call the "main.py" python module with the 'auth' hook parameters.
python3 "./main.py" "$CERTBOT_DOMAIN $CERTBOT_VALIDATION auth $CERTBOT_TOKEN"


# Any tasks needed AFTER running the validation, do here...

##########
