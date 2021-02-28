#!/bin/bash
# Get the project's PWD, no matter where this is called from.
PROJDIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"
# Preliminary information.
echo -e "Running cleanup hook...\n"
echo "Domain: $CERTBOT_DOMAIN"
echo "Validation: $CERTBOT_VALIDATION"
echo "Token (http-only): $CERTBOT_TOKEN"


# Any tasks to run BEFORE the cleanup hook, do here...

##########


# Run the python 'cleanup' hook from "main.py" in the current directory.
python3 "${PROJDIR}/main.py" "$CERTBOT_DOMAIN $CERTBOT_VALIDATION cleanup $CERTBOT_TOKEN"


# Any tasks to run AFTER the cleanup hook, do here...

# Sample code, as an example of what can be scripted after the new certificates
#   have been pulled and go live.
#   The following code is specifically for a very hacky way to allow an IMAP server to use
#    a new LE certificate without needing to do much to the original file.
if [[ "${CERTBOT_DOMAIN^^}" == "IMAP.SAMPLEDOMAIN.NET" ]]; then
    sleep 2
    ln -s /etc/letsencrypt/live/IMAP.SAMPLEDOMAIN.NET/fullchain.pem /etc/dovecot/fullchain.pem
    ln -s /etc/letsencrypt/live/IMAP.SAMPLEDOMAIN.NET/privkey.pem /etc/dovecot/privkey.pem
    chown root.dovecot /etc/letsencrypt/live/IMAP.SAMPLEDOMAIN.NET/fullchain.pem
    chown root.dovecot /etc/letsencrypt/live/IMAP.SAMPLEDOMAIN.NET/privkey.pem
    chmod 640 /etc/letsencrypt/live/IMAP.SAMPLEDOMAIN.NET/privkey.pem
    systemctl restart dovecot postfix
fi

##########


# Output success.
echo "Updated LE certificates for ${CERTBOT_DOMAIN}."
exit 0
