#!/bin/bash
#
# Run the certbot utility against the "renewals.txt" listed domains.
#   This is intended to be run by cron daily, with two params:
#   $1 = The keyword "AUTO". Really a placeholder at this time -- later this will be
#         changed to allow a script user to just pass a domain name individually.
#   $2 = The amount of days WITHIN EXPIRY of any certificate to attempt a renewal request.
#         For example, if this param is 20 days, the script will only attempt a
#         renewal if the target domain's cert expires within 20 days of RIGHT NOW.
#
# Required binaries: certbot, openssl
#
#

# Directory where the certbot DNS API utility resides.
CERTBOT_AUTO="/root/certbot_auto"
# Full path to the text file to parse for comma-delimited certifying domains.
DOMAINS_FILE="${CERTBOT_AUTO}/renewals.txt"

echo -e "\n\n========== $(date) =========="
if [[ "${1^^}" == "AUTO" ]]; then
    [[ $# -ne 2 ]] && echo "Two parameters only were expected. Quitting." && exit 1
    [[ -z "$(echo "$2" | grep -Po '^[0-9]+$')" ]] \
        && echo "Param 2 wasn't a number. Expected minimum days difference to start auto-renew. Quitting." \
        && exit 2
    MIN_SEC_DIFF=$(( $2 *24 *60 *60  ))   #minimum seconds of difference between now and the cert expiry at which renewals should trigger
    NOW_TIME=$(date -d'now' +%s)   #current unix timestamp
    IFS=','; for i in `cat $DOMAINS_FILE`; do
        #target cert's expiry unix timestamp
        THEN_TIME="$(date -d "$(openssl x509 -noout -in /etc/letsencrypt/live/$i/fullchain.pem -dates 2>/dev/null | grep notAfter | cut -d'=' -f2)" +%s)"
        # If the difference between now and then is less that the noted trigger difference, try renewing.
        if [[ $(( $THEN_TIME - $NOW_TIME )) -le $MIN_DAYS ]]; then
            echo -e "\n+ Renewal attempt for: ${i}"
            certbot certonly --manual --preferred-challenges=dns --manual-public-ip-logging-ok \
                --manual-auth-hook $CERTBOT_AUTO/cb-auth.sh \
                --manual-cleanup-hook $CERTBOT_AUTO/cb-cleanup.sh \
                -d "$i"
                echo -e "\n====================================\n"
        else
            echo "+ Domain '${i}' doesn't need to be renewed at this time."
        fi
    done
else
    echo "+ AUTO not supplied as param 1. Quitting."
    exit 1
fi

echo -e "\n=== COMPLETE ==="
exit 0

