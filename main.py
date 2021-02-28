#!/bin/python3
#
# main.py
#
#   Contributors:
#       Notsoano Nimus <github@xmit.xyz>
#   Repo:
#       https://github.com/NotsoanoNimus/certbot-manual-python-hooks
#   Description:
#       Automatically set up Certbot authorizations for new and renewing SSL certificates from LetsEncrypt.
#       Parameters in the accompanying settings.py file are required to be set before running these hooks.
#
######################################################################################
# Copyright (C) 2021 @NotsoanoNimus on GitHub, as a free software project
#  licensed under GNU GPLv3.
#
# This program is free software: you can redistribute it and/or modify it under
#  the terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
#  ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
#  this program. If not, see https://www.gnu.org/licenses/.
######################################################################################
#
#
#
""" MAIN.PY - The main file to run directly from the python interpreter with the appropriate parameters. """
import sys, re
from certbot_worker import CertbotWorker


""" Define the main function used to run the auth/cleanup hooks. """
def main():
    # Check to ensure the provided command-line parameters include the self-referential ($0) and the Certbot info.
    if len(sys.argv) != 2:
        sys.exit("The manual hook didn't receive the appropriate parameters. Aborting.")

    certbot_info = sys.argv[1].strip()
    # The expected Certbot parameter should be in this format: "F.Q.D.N. acme-token {auth|cleanup} [token]"
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
        import logging, traceback
        logging.error(traceback.format_exc())
        sys.exit("Could not construct the certbot worker: the given paramters are NOT valid!")

    # Perform the validation.
    print("Using python '%s' certbot hook for domain '%s'..." % (cb_pms[2], cb_obj.api.base_domain))
    if cb_obj.type == 'dns':
        worker_result = cb_obj.dns_validation()
    else:
        cb_obj.http_validation()



""" The start of the actual script processing. """
""" Only call the main method if this script is being directly executed by the interpreter. """
if __name__ == '__main__':
    main()
