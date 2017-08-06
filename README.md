# Dynamic DNS for NameSilo.com

IN DEVELOPMENT.
Python API implementation for NameSilo.  Primarily used as a Dynamic DNS update, or DDNS tool, this can update your home's dynamic IP into a nice domain.  EVERYTHING AFTER THIS LINE IS OLD AND HASN'T BEEN TOUCHED... yet. ever. likely never.

# Requirements
[Python 3](https://www.python.org/downloads/)

[Requests Python Package](https://pypi.python.org/pypi/requests)

`pip install requests`

A [NameSilo.com](https://www.namesilo.com/) account with records that need DDNS support.

# How To

Generate and save an API key from NameSilo. See [NameSilo](https://www.namesilo.com/Support/Account-Options) for help.

Edit `dynamic_dns_updater_for_namesilo.com.py` file in the variables section, being sure not to modify the code.

```
# Variables
api_key = "xxxxxxxx" <- This is the API you generated from above.
domain = "r-ben.com" <- The domain that contains the record you want to update.
record = "freedom" <- The actual A record to be checked and updated.
```

Save the python file and run it using `python3 dynamic_dns_updater_for_namesilo.com.py`.

Add this as a scheduled task or cron job depending on your OS.

# Maintainer
Benjamin Rosner

# Bugs or Issues?
Please use the Issues button to submit bug reports or other issues.

If you've fixed the code please issue a pull request and indicate the issue number(s) resolved. (e.g. Resolves #1 by doing X Y and Z.)

# License
[GNU GENERAL PUBLIC LICENSE v3](LICENSE)

# Credits
[Concept and Inspiration](http://www.forkrobotics.com/2014/10/dynamic-dns-with-namesilo-and-powershell/)
