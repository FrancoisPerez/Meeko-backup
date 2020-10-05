#Meeko Backup
[Meeko](http://www.meeko.pro) is a SaaS solution that allows the management of nurseries. This company also provides an iPhone/Android app for 
parents to review the day of their kids at the nursery.

This tool is a Python-based solution that creates a backup of all data stored on Meeko.

To use this script, you will need to find your (personal) Bearer Token. You can do this by using [Charles Proxy](
http://www.charlesproxy.com) on your smartphone. 

## CLI Usage
```bash
$ python main.py [-b BEARER_TOKEN] [-s START_TIMESTAMP] [-e END_TIMESTAMP]
```

##Output
This tool will output raw JSON from Meeko's API, each section in a specific folder.

##Upcoming features
- Invoice export
- Documents export
