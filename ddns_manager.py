import sys
from time import strftime
import xml.etree.ElementTree as ETree
import requests
import sendgrid

# NameSilo Dynamic DNS IP Address Updater.
#
# @DATE: 04 AUG 2017
# @VERSION: 1.084
# @Author: Benjamin Rosner
# Requires Python >= 3.5, the 'requests' lib and 'sendgrid' lib for email support. `pip3 install <lib name>`
# This script is not endorsed nor created by NameSilo, LLC. Read the Disclaimers of Use before proceeding.
#
# DISCLAIMERS OF USE: Use at your own risk.  You are liable for all uses implied explicit and implicit herein.
# Use of this script is at the users own discretion.  You are required to follow all applicable laws and rules.
# Neither the Author, nor NameSilo, LLC are liable for any use or misuse of this script.  Please be smart.
#
# Your ISP likely does not provide you a static IP address. We assume you understand why a dynamic ip can be annoying.
# One of this scripts purposes is to allow you to update your DYNAMIC IP to NameSilo's nameservers.  DDNS.
# NameSilo does not natively support DDNS service but has a robust API that we use.
#
# NameSilo is a a great DNS provider with simple pricing and free benefits where others charge (e.g., free WHOIS
# anonymity).  If you are interested in NameSilo please consider using my affiliate link - a small benefit is provided!
# https://www.namesilo.com/?rid=316d173ag
#
# Original inspiration and thanks: http://www.forkrobotics.com/2014/10/dynamic-dns-with-namesilo-and-powershell/
# Created using the python IDE PyCharm, and text editor Sublime Text 3.


#######################################################################################################################
#  USER VARIABLES
#
#  Edit this section only! Enter your API keys, domains and hosts, and email preferences.
#######################################################################################################################

# Your API keys.
namesilo_api_key = ""
sendgrid_api_key = ""

# Domains and hosts to update.
domains_and_hosts = (

)
"""
Example configuration for a single domain with hosts:
domains_and_hosts = (
    ["namesilo.com", ["", "www", "mail"]]  # This will update namesilo.com, www.namesilo.com, and mail.namesilo.com.
)

Example configuration for multiple domains and hosts:
domains_and_hosts = (
    ["namesilo.com", ["www", "mail"]],  # This will update www.namesilo.com, and mail.namesilo.com.
    ["CNN.com", ["", "www"]],  # This will update CNN.com, and www.CNN.com.
    ["NPR.org", ["giving", "charity"]],  #  This will update giving.NPR.org, and charity.NPR.org.
    ["example.org", [""]]  #  This will update example.org.
)
"""
record_ttl = "3600"

# Outgoing Email
send_mail = True
from_email = "email"
to_email = "email"
subject = "DNS update notification, timestamped: " + strftime('%x %H:%M:%S')

#######################################################################################################################
#######################################################################################################################
#  STOP EDITING!                 You're done!  Congratulations.  Now give us a whirl!                   STOP EDITING! #
#######################################################################################################################
#######################################################################################################################
NAMESILO_COM_API = 'https://www.namesilo.com/api'
NAMESILO_API_IMPLEMENTED_OPERATIONS = {'dnsListRecords', 'dnsUpdateRecord'}
#  Response keys from the API:
NAMESILO_API_RESPONSE_RECORD_KEYS = {'resource_record', 'record_id', 'type', 'host', 'value', 'ttl', 'distance'}
# Requests session instance:
_web_worker = requests.session()

current_ip = _web_worker.get('https://api.ipify.org/?format=json').json()['ip']  # GET our current IP.
do_email = False
email_body = []


class NameSilo_APIv1:
    def __init__(self, domain, hosts=None):
        self.domain = domain
        self.__namesilo_api_params = {'version': '1', 'type': 'xml', 'key': namesilo_api_key, 'domain': self.domain}
        self.hosts = hosts  # hosts to update, blank for working on the domain.
        self.current_records = []  # NameSilo's current resource records for self.domain retrieved from the API.

        self.retrieve_resource_records()  # poopulate.

        # Run DNS update! ...that is all there is to it, I guess.

    @property
    def domain(self) -> str:
        """The domain to be manipulated."""
        return self._domain

    @domain.setter
    def domain(self, value):
        if value is not None:  # @todo real validation of domain name.
            self._domain = value
        else:
            raise ValueError('Invalid domain name. Please specify a domain in normal syntax, e.g.: google.com')

    @property
    def hosts(self) -> list:
        """The hosts of this domain to be manipulated."""
        return self._hosts

    @hosts.setter
    def hosts(self, value):
        if value is not None:
            # I feeel preetty. Ohh soo pretty.
            self._hosts = [str.join('.', [host, self.domain]) if host != '' else self.domain for host in value]
        else:
            raise ValueError('Could not parse hosts.')

    @property
    def domain_resources_record_count(self) -> int:
        """Total Number of resource records returned by the API for this domain."""
        return len(self.current_records)

    def _api_connection(self, operation, **html_params) -> str:
        """Connection endpoint."""
        if operation is not None and operation in NAMESILO_API_IMPLEMENTED_OPERATIONS:
            __api_call = {**html_params, **self.__namesilo_api_params}  # Join request parameter dictionaries.
            __api_url = str.join('/', [NAMESILO_COM_API, operation])  # Build URL with operation.
            #  logger.append(__api_url, __api_call)
            ret = _web_worker.get(__api_url, params=__api_call)  # Make the request.
            ret.raise_for_status()  # Check for HTTP success.
            return ret.text
        else:
            raise ValueError('Invalid operation, currently unsupported or unavailable.')

    def retrieve_resource_records(self):
        """Retrieve current Resource Records from NameSilo for self.domain."""
        print('Retrieving records.')
        current_records = ETree.XML(self._api_connection('dnsListRecords'))
        for current_resource_record in current_records.iter('resource_record'):
            self.current_records.append(
                {
                    rr.tag: rr.text  # danger, thar be shadows in these depths.
                    for rr in current_resource_record.iter()
                    if rr.tag in NAMESILO_API_RESPONSE_RECORD_KEYS  # pseudo comprehension.
                }
            )
        print('Records retrieved.')

    def ddns_update(self):
        for host in self.hosts:
            # Do something impressive for the people.
            # key lookup, grab rrid, send update request with host and updated ip.


#  In development, too tired.
def update_records():
    for domain, hosts in domains_and_hosts:
        NameSilo_APIv1(domain, hosts).ddns_update()

update_records()
