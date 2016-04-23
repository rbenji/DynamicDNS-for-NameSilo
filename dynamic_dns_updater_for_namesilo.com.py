import requests
import sys
import xml.etree.ElementTree as eltree

# NameSilo API Dynamic DNS
# Original Concept and Credits go to:
# http://www.forkrobotics.com/2014/10/dynamic-dns-with-namesilo-and-powershell/

# Variables
api_key = "xxxxxxxx"
domain = "r-ben.com"
record = "freedom"

## Code - Do not edit below this line
namesilo_api = 'https://www.namesilo.com/api/'
version_param = '?version=1'
resp_type_param = '&type=xml'
api_key_param = '&key=' + api_key
domain_param = '&domain=' + domain
record_param = '&rrhost=' + record
record_fqdn = record + '.' + domain
record_ttl = '&rrttl=3600'

# Setup webworker
webworker = requests.session()

# Gather data about the DNS entries in the domain
dns_list_records = ''.join(
    [namesilo_api, 'dnsListRecords', version_param, resp_type_param, api_key_param, domain_param])
records_list = webworker.get(dns_list_records)

if records_list.status_code != 200:
    print('Error fetching domain list.')
    sys.exit(1)

parsed = eltree.fromstring(records_list.text)

# Set our IP address from the response.
callers_ip = parsed.find('.//ip').text

# Gather all of our resource_records
resource_records = parsed.findall('.//resource_record')

# This could be done plenty of other ways, but I like this for ease of readability.
# Find our FQDN's record_id.
for record in resource_records:
    if (record[2].text == record_fqdn):
        record_id = record[0].text
        record_ip = record[3].text
        continue

print('Current IP: ' + callers_ip + '\nRecord\'s IP: ' + record_ip)
if (callers_ip != record_ip):
    print('Update required.')
    record_id_param = '&rrid=' + record_id
    record_ip_param = '&rrvalue=' + callers_ip
    update_record = ''.join(
        [namesilo_api, 'dnsUpdateRecord', version_param, resp_type_param, api_key_param, domain_param, record_param,
         record_id_param, record_ip_param, record_ttl])
    response = webworker.get(update_record)
    # Some validation should be done on response - I think they return 300 if success. Too lazy.
else:
    print('No update was required.')
