# Cloud Flare Dynamic DNS
Python script to create/update A record to cloudflare

Create cloudflare.conf file (a sample is included as cloudflare.conf.sample) as per your requirements.
If domain exists in your cloudflare account, script will create an A record based on your public ip.
If the record is already present, it will update it with current IP if it has changed lately.
