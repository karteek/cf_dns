#!/usr/bin/env python

import json
import os
import requests

def get_cached_ip():
    if not os.path.exists("cached_ip.json"):
        return {}

    with open("cached_ip.json") as f:
        try:
            return json.load(f)
        except:
            return {}


def cache_ip(ip_json):
    with open("cached_ip.json", "w+") as f:
        json.dump(ip_json, f)


def get_current_ip():
    resp = requests.get("https://api.ipify.org?format=json")
    return resp.json()


def get_config():
    with open("cloudflare.conf") as f:
        try:
            return json.load(f)
        except:
            return {}

def main():
    config = get_config()
    if not config:
        raise Exception("Cannot continue without configuration. Look for cloudflare.conf.sample")
    headers = {
        "X-Auth-Email": config.get("email"),
        "X-Auth-Key": config.get("api_key")
    }

    cached_ip = get_cached_ip().get("ip")
    current_ip = get_current_ip().get("ip")

    if cached_ip == current_ip:
        print "IP didn't change. Nothing to update"
    else:
        # Cached IP is not same as current IP
        # Get the Zone ID from Cloudflare
        cache_ip({"ip": current_ip})
        zones_response = requests.get(
            "https://api.cloudflare.com/client/v4/zones?name={}".format(config.get("domain")),
            headers=headers
        )
        if zones_response.status_code == 200:
            zone_id = zones_response.json()["result"][0]["id"]
            dns_records = requests.get(
                "https://api.cloudflare.com/client/v4/zones/{}/dns_records".format(zone_id),
                headers=headers
            )
            put_records = {}
            for record in dns_records.json()["result"]:
                if record["name"] in config["records"] and record["type"] == "A":
                    put_records[record["name"]] = record["id"]

            for record in config["records"]:
                if record in put_records:
                    print "Updating A record for {} to point {}".format(record, current_ip)
                    put_url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records/{}".format(
                        zone_id, put_records[record])
                    put_dict = {
                        "type": "A",
                        "name": record,
                        "content": current_ip,
                        "ttl": 300
                    }
                    resp = requests.put(put_url, headers=headers, data=json.dumps(put_dict))
                    if resp.status_code == 200:
                        print "Success"
                else:
                    print "Creating A record for {} pointing to {}".format(record, current_ip)
                    post_url = "https://api.cloudflare.com/client/v4/zones/{}/dns_records".format(zone_id)
                    post_dict = {
                        "type": "A",
                        "name": record,
                        "content": current_ip,
                        "ttl": 300
                    }
                    resp = requests.post(post_url, headers=headers, data=json.dumps(post_dict))
                    if resp.status_code == 200:
                        print "Success"
        else:
            for e in zones_response.json().get("errors"):
                print e["message"]



if __name__ == "__main__":
    main()
