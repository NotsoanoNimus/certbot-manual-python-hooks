#!/bin/bash
echo -e "Running auth hook...\n"
echo "Domain: $CERTBOT_DOMAIN" >/tmp/certbotoutput.tmp
echo "Validation: $CERTBOT_VALIDATION" >>/tmp/certbotoutput.tmp
echo "Token (http-only): $CERTBOT_TOKEN" >>/tmp/certbotoutput.tmp

python3 "./main.py" "$CERTBOT_DOMAIN $CERTBOT_VALIDATION auth $CERTBOT_TOKEN"
