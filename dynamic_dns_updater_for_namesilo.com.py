import sys
import time
import xml.etree.ElementTree as eltree

import requests
import sendgrid

# NameSilo API Dynamic DNS
# Original Concept and Credits go to:
# http://www.forkrobotics.com/2014/10/dynamic-dns-with-namesilo-and-powershell/

# Variables
api_key = "XXXXXXXXXXXXXXXXXXXXXX"
sendgrid_api_key = "XXXXXXXXXXXXXXXXXXXXXX"
domain = "r-ben.com"
records_fqdn = ["r-ben.com", "freedom.r-ben.com"]
record_type = "A"

######################################
# Code - Do not edit below this line #
######################################
namesilo_api = 'https://www.namesilo.com/api/'
version_param = '?version=1'
resp_type_param = '&type=xml'
api_key_param = '&key=' + api_key
domain_param = '&domain=' + domain
host_param = '&rrhost='
record_ttl = '&rrttl=3600'
email_list = []
do_email = False


def update_records():
    message_out('Record name: ' + record_fqdn + '\nRecord\'s IP: ' + record_ip)
    if callers_ip != record_ip:
        message_out('Update required.')
        record_id_param = '&rrid=' + record_id
        record_ip_param = '&rrvalue=' + callers_ip
        if record_fqdn == domain:
            record_host = ''
        else:
            record_host = record_fqdn.replace('.' + domain, '')
        update_record = ''.join(
            [namesilo_api, 'dnsUpdateRecord', version_param, resp_type_param, api_key_param, domain_param,
             host_param, record_host, record_id_param, record_ip_param, record_ttl])
        # Some validation should be done on response - I think they return 300 if success. Too lazy.
        response = webworker.get(update_record)
        message_out("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + response.text)
        return True
    else:
        message_out('No update was required.')


def message_out(message):
    print(message)
    email_list.append(message)


def send_email():
    if do_email:
        client = sendgrid.SendGridClient(sendgrid_api_key)
        message = sendgrid.Mail()

        message.add_to("benrosner@gmail.com")
        message.set_from("no-reply@freedom-mail.r-ben.com")
        message.set_subject("[DynDNS] " + time.strftime('%x %H:%M:%S') + " DNS update notification")
        message.set_html('<br>'.join(email_list))
        client.send(message)


# Setup webworker
webworker = requests.session()

# Gather data about the DNS entries in the domain
dns_list_records = ''.join(
    [namesilo_api, 'dnsListRecords', version_param, resp_type_param, api_key_param, domain_param])
records_list = webworker.get(dns_list_records)
# print(eltree.tostring(eltree.fromstring(records_list.text), encoding="unicode", method="html"))

if records_list.status_code != 200:
    message_out('Error fetching domain list.')
    message_out("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + records_list.text)
    do_email = True
    send_email()
    sys.exit(1)

parsed = eltree.fromstring(records_list.text)

# Set our IP address from the response.
callers_ip = parsed.find('.//ip').text
message_out('Current IP: ' + callers_ip)

# Gather all of our resource_records.
resource_records = parsed.findall('.//resource_record')

# This could be done plenty of other ways, but I like this for ease of readability.
# Find our FQDN's record_id.
for record in resource_records:
    if (record[2].text in records_fqdn) and (record[1].text == record_type):
        record_fqdn = record[2].text
        record_id = record[0].text
        record_ip = record[3].text
        do_email = update_records()

if int(time.strftime('%H')) % 6 == 0:
    do_email = True

send_email()
