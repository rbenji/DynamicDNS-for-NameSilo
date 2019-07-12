import os
import xml.etree.ElementTree as ETree
from time import strftime
import ipaddress

import requests
from sendgrid import *
from sendgrid.helpers.mail import *

# NameSilo API Python3 Implementation - Specifically for DDNS support.
# NameSilo Dynamic DNS IP Address Updater.
# Email integration is provided by SendGrid (https://www.sendgrid.com).
#
# DATE: 19 AUG 2017
# VERSION: 1.088
# REQUIRES:
# - Python >= 3.5.2,
# - Requests (http://docs.python-requests.org/) `pip install requests`
# - SendGrid (https://github.com/sendgrid/sendgrid-python) for basic email support if desired. `pip install sendgrid`
#
# Copyright (c) 2017 Benjamin Rosner
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all copies or substantial portions of
# the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO
# THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
#  TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
#
# Your ISP likely does not provide you a static IP address.
# One of this scripts purposes is to allow you to update your DYNAMIC IP to NameSilo's nameservers.  DDNS.
# NameSilo does not natively support DDNS service but has a robust API that we use.
#
# Original inspiration and thanks: http://www.forkrobotics.com/2014/10/dynamic-dns-with-namesilo-and-powershell/
# Created using PyCharm, and Sublime Text 3.
# This script is not endorsed nor created by NameSilo, LLC., nor  SendGrid, INC.
########################################################################################################################

# Domains and hosts to update.
domains_and_hosts = (
    ["arebenji.com", ["home"]],
    ["arebenji.online", ["home"]],
    ["benjaminrosner.com", [""]],
    ["r-ben.com", ["", "freedom"]]
)

record_ttl = "3600"

# Outgoing Email Settings
send_mail = True
send_time = int(strftime('%I')) % 8 == 0  # Send an email at 8AM and 8PM.  Set to True to always send.
email_from_address = "no-reply@freedom-mail.r-ben.com"
email_from_name = "Freedom-Systems Admin"
email_to_addresses = ["benrosner@gmail.com"]
subject = "DNS update notification, timestamped: " + strftime('%x %H:%M:%S')  # Subject line.

#######################################################################################################################
#######################################################################################################################
#  STOP EDITING!                 You're done!  Congratulations.  Now give us a whirl!                   STOP EDITING! #
#######################################################################################################################
#######################################################################################################################
namesilo_api_key = os.environ.get('NAMESILO_API_KEY')
NAMESILO_COM_API = 'https://www.namesilo.com/api'
NAMESILO_API_IMPLEMENTED_OPERATIONS = {'dnsListRecords', 'dnsUpdateRecord', 'dnsAddRecord', 'dnsDeleteRecord'}

_web_worker = requests.session()  # Requests session instance.


class NameSilo_APIv1:
    def __init__(self, domain, hosts=None):
        log('NameSilo connection called for {} at {}.'.format(domain, strftime('%x %H:%M:%S')))
        self.domain = domain
        self._namesilo_api_params = {
            'version': '1',
            'type': 'xml',
            'key': namesilo_api_key,
            'domain': self.domain
        }
        self.hosts = hosts  # Hosts to update, blank for working on the domain.
        self.current_records = []  # NameSilo's current resource records for self.domain retrieved from the API.

        self.retrieve_resource_records()  # populate.

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
    def hosts(self) -> dict:
        """The hosts of this domain to be manipulated. Keyed by FQDN."""
        return self._hosts

    @hosts.setter
    def hosts(self, value):
        """Take the host list and create a dictionary. The keys of this dictionary are the FQDN representation of
        the host (i.e., host.domain.tld)"""
        if value is not None:
            self._hosts = dict(
                (str.join('.', [host, self.domain]) if host != '' else self.domain, host)
                for host in value
            )
        else:
            raise ValueError('Could not parse hosts.')

    def _api_connection(self, operation, **html_params) -> ETree.ElementTree:
        """Connection endpoint. Returns operations in XML as Element"""
        if operation is not None and operation in NAMESILO_API_IMPLEMENTED_OPERATIONS:
            _api_call = {**html_params, **self._namesilo_api_params}  # Join request parameter dicts.
            _api_url = str.join('/', [NAMESILO_COM_API, operation])  # Build URL with operation.
            # print('API connection:', __api_url, __api_call)  # dev.
            _ret = _web_worker.get(_api_url, params=_api_call)  # Send the API request.
            _ret.raise_for_status()  # Builtin check for HTTP success.
            _ret = ETree.XML(_ret.text)  # The final form of our return response.
            """Response Validation"""
            try:
                success = _ret.find('.//reply/code').text
            except AttributeError:
                raise ValueError('Could not parse API response.')
            if success != '300':
                raise ValueError('API Operation failed with code {}.'.format(success))
            return _ret
        else:
            raise NotImplementedError('Invalid operation: {} is currently unsupported or undefined.'.format(operation))

    def retrieve_resource_records(self):
        """Retrieve current Resource Records from NameSilo for self.domain."""
        log('Retrieving records for {}'.format(self.domain))
        current_records = self._api_connection('dnsListRecords')
        self.current_records = []
        for current_resource_record in current_records.iter('resource_record'):
            self.current_records.append(
                dict(
                    (resource_record.tag, resource_record.text)
                    for resource_record
                    in current_resource_record.iter()
                )
            )
        log('{} records retrieved for {}'.format(len(self.current_records), self.domain))
        log(self.current_records)

    def dynamic_dns_update(self, value, type=None):
        """Dynamic DNS updater"""
        # If no type given, assume an IP value in, otherwise, type must be given
        # Because we don't know what kind of type user want
        if not type:
            try:
                ip_address = ipaddress.ip_address(value)
            except ValueError:
                log('{} is not a valid IPv4/IPv6 address, type must be given'.format(value))
                return
            if(ip_address.version == 4):
                type = 'A'
            else:
                type = 'AAAA'
        log('DDNS update starting for domain: {} and record type {}'.format(self.domain, type))
        # Generator for hosts that require an record update.
        hosts_requiring_updates = (
            record for record
            in self.current_records
            if record['host'] in self.hosts.keys()
               and (
                   record['type'] == type
                   and record['value'] != value
               )
        )

        # Now iterate and send requests to the endpoint to update those hosts.
        _count = 0
        _failed = 0
        for host in hosts_requiring_updates:
            log('DDNS update required for {}'.format(host['host']))
            __api_params = {
                'rrid': host['record_id'],
                'rrhost': self.hosts[host['host']],
                'rrvalue': value,
                'rrttl': record_ttl,
            }
            try:
                self._api_connection('dnsUpdateRecord', **__api_params)
            except ValueError:
                log('DDNS failed to update {}'.format(host['host']))
                _failed += 1
                pass
            except NotImplementedError:
                log('DDNS failed to update {}'.format(host['host']))
                _failed += 1
                pass
            _count += 1
            log('DDNS successfully updated {}'.format(host['host']))
        log('DDNS update complete for {}.  {} hosts required updates. {} errors.'.format(
            self.domain, _count, _failed))

        # List for hosts that reuire an record create.
        hosts_requiring_adds = [
            host for host
            in self.hosts.keys()
            if not any(record.get('host', None) == host for record in self.current_records)
        ]
        log('DDNS add required for {}'.format(hosts_requiring_adds))
        for host in hosts_requiring_adds:
            self.dynamic_dns_add(self.hosts[host], value, type)

    def dynamic_dns_add(self, host_without_domain, value, type):
        __api_params = {
            'rrtype': type,
            'rrhost': host_without_domain,
            'rrvalue': value,
            'rrttl': record_ttl,
        }
        try:
            self._api_connection('dnsAddRecord', **__api_params)
        except ValueError:
            log('DDNS failed to add {}, type {}, value {}'.format(host_without_domain, 
            type, value))
            return
        except NotImplementedError:
            log('DDNS failed to add {}, type {}, value {}'.format(host_without_domain, 
            type, value))
            return
        log('DDNS successfully add {}, type {}, value {}'.format(host_without_domain, 
            type, value))
        self.retrieve_resource_records()  # re-populate.

    # Any of the parameter can be None and if all of the parameters are None, 
    # means delete all records for this domain
    def dynamic_dns_delete(self, host_without_domain=None, value=None, type=None):
        log('DDNS delete starting for domain: {}, host {}, type {}, value {}'.format(
            self.domain, host_without_domain, type, value))
        hosts_requiring_deletes = []
        for record in self.current_records:
            flag = True
            if host_without_domain:
                flag = flag and (record['host'] == (str.join('.', 
                [host_without_domain, self.domain]) if host_without_domain != '' else self.domain))
            if value:
                flag = flag and (record['value'] == value)
            if type:
                flag = flag and (record['type'] == type)
            if flag:
                hosts_requiring_deletes.append(record)
        _count = 0
        _failed = 0
        for host in hosts_requiring_deletes:
            __api_params = {
                'rrid': host['record_id'],
            }
            try:
                self._api_connection('dnsDeleteRecord', **__api_params)
            except ValueError:
                log('DDNS failed to delete {}'.format(host_without_domain))
                _failed += 1
                pass
            except NotImplementedError:
                log('DDNS failed to delete {}'.format(host_without_domain))
                _failed += 1
                pass
            _count += 1
            log('DDNS successfully delete {}'.format(host_without_domain))
        log('DDNS delete complete for {}.  {} hosts required updates. {} errors.'.format(
            self.domain, _count, _failed))
        self.retrieve_resource_records()  # re-populate.

#######################################################################################################################
#######################################################################################################################
#  STOP EDITING!                 You're done!  Congratulations.  Now give us a whirl!                   STOP EDITING! #
#######################################################################################################################
#######################################################################################################################
# In development, too tired.
_log = []


def log(message):
    print(message)
    _log.append(message)


def update_records():
    log("DDNS operation started at {}".format(strftime('%x %H:%M:%S')))
    for domain, hosts in domains_and_hosts:
        NameSilo_APIv1(domain, hosts).dynamic_dns_update(_current_ip)
    if send_mail and send_time:
        send_message()


def build_message():
    """Builds an outgoing message."""
    outgoing_mail = Mail()
    outgoing_mail.from_email = Email(email_from_address, email_from_name)
    outgoing_mail.subject = subject
    personalization = Personalization()
    for recipient in email_to_addresses:
        personalization.add_to(Email(recipient))
    outgoing_mail.add_personalization(personalization)
    outgoing_mail.add_content(Content("text/plain", str.join('\n', _log)))
    outgoing_mail.add_content(Content("text/html", "<html><body> {} </body></html>".format(str.join(' <br /> ', _log))))
    return outgoing_mail.get()


def send_message():
    """Sends a built outgoing message."""
    # @todo validation & error handling.
    sg = SendGridAPIClient(apikey=os.environ.get('SENDGRID_API_KEY'))
    log("Message generated and sent at {}".format(strftime('%x %H:%M:%S')))
    sg.client.mail.send.post(request_body=build_message())


if __name__=="__main__":
    _current_ip = _web_worker.get('https://api.ipify.org/?format=json').json()['ip']  # GET our current IP.
    update_records()
