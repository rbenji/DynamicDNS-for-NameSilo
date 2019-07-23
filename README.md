# NameSilo API Python3 Implementation - Specifically for DDNS support.

NameSilo Dynamic DNS IP Address Updater.
Email integration is provided by SendGrid (https://www.sendgrid.com).

DATE: 19 AUG 2017
VERSION: 1.088

# REQUIRES
 - Python >= 3.5.2,
 - Requests (http://docs.python-requests.org/)
  `pip install requests`
 - SendGrid (https://github.com/sendgrid/sendgrid-python) for basic email support if desired.
  `pip install sendgrid`

# Copyright (c) 2017 Benjamin Rosner

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


## Configuration
- Example configuration for a single domain with hosts (without email notification):
```
 record_ttl = '7207'
 domains_and_hosts = (
     ["namesilo.com", ["", "www", "mail"]],  # This will update namesilo.com, www.namesilo.com, and mail.namesilo.com.
 )
```
- Example configuration for multiple domains and hosts (without email notification):
```
 record_ttl = '7207'
 domains_and_hosts = (
     ["namesilo.com", ["www", "mail"]],  # This will update www.namesilo.com, and mail.namesilo.com.
     ["CNN.com", ["", "www"]],  # This will update CNN.com, and www.CNN.com.
     ["NPR.org", ["giving", "charity"]],  #  This will update giving.NPR.org, and charity.NPR.org.
     ["example.org", [""]]  #  This will update example.org.
 )
```
### Additional configuration lines for email using SendGrid.com
```
send_mail = True  # Either "True" or "False"
send_time = int(strftime('%I')) % 8 == 0  # Send an email at 8AM and 8PM.  Set to True to always send.
email_from_address = "someone@somedomain.tld"
email_from_name = "NameServer Systems"
email_to_addresses = ["jane.doe@company", "john.doe@company", "my.manager@somebusiness.com"]  # comma separated.
subject = "DNS update notification, timestamped: " + strftime('%x %H:%M:%S')  # Subject line.
```

# Usage Examples

## Update/Add IPv4/IPv6 record

The following 2 lines will update A record of www.xxx.com and test.xxx.com to 1.2.3.4, if any of them doesn't exist, it will be created automatically

```python
import ddns_manager
api = ddns_manager.NameSilo_APIv1("xxx.com", ["www", "test"])
api.dynamic_dns_update("1.2.3.4")
```

## Update/Add specific type record

The valid type will be:

- A - The IPV4 Address
- AAAA - The IPV6 Address
- CNAME - The Target Hostname
- MX - The Target Hostname
- TXT - The Text

The following 2 lines will update/create a TXT record of _acme-challenge.xxx.com and its value is utpEMa5B58CMdjTJCLnB5XxcmZ0CoCP6PFdmqE5bIpo.

```python
import ddns_manager
api = ddns_manager.NameSilo_APIv1("xxx.com", ["_acme-challenge"])
api.dynamic_dns_update("utpEMa5B58CMdjTJCLnB5XxcmZ0CoCP6PFdmqE5bIpo", "TXT")

# You may want to create a record without checking if it exists or not.
api.dynamic_dns_add("www", "2001::3", "AAAA")
```

## Delete record

This delete function will delete all the records which match the conditions user offered. User can offer host, value, type as delete function paramter, all the parameters are optional.
If no parameter given, means all the namesilo records belongs to this domain will be deleted.

```python
import ddns_manager

api = ddns_manager.NameSilo_APIv1("xxx.com")

# Delete _acme-challenge.xxx.com TXT record with value utpEMa5B58CMdjTJCLnB5XxcmZ0CoCP6PFdmqE5bIpo
api.dynamic_dns_delete("_acme-challenge", "utpEMa5B58CMdjTJCLnB5XxcmZ0CoCP6PFdmqE5bIpo", 'TXT')

# Delete all AAAA records
api.dynamic_dns_delete(type="AAAA")

# Delete all www records
api.dynamic_dns_delete(host_without_domain="www")

# Delete all records which value is "4.5.6.7"
api.dynamic_dns_delete(value="4.5.6.7")

# Delete any records belongs to this domain
api.dynamic_dns_delete()
```


# How To

1. Generate and save an API key from NameSilo. See [NameSilo](https://www.namesilo.com/Support/Account-Options) for help.
2. Generate and save an API key from SendGrid. See ...
3. Create copies of the script as needed and configure them.
4. Export required ENVIRONMENT VARIABLES: NAMESILO_API_KEY and SENDGRID_API_KEY
5. Save the python file and run it using `python <whateverYouNamedIt>.py`.  Some systems may run two versions of python: `python3 <whateverYouNamedIt>.py`
6. (optional) Add this command to cron or scheduler depending, ya know?

You can also use this as a class in your own programs, though it is a rather immature implementation as of writing.

# Questions or Bugs
Create an issue and I'm happy to help :)

# License
[MIT License](LICENSE)
