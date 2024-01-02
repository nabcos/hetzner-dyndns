#!/usr/bin/env python

import os, sys
import requests
import json
from loguru import logger

API_URL = "dns.hetzner.com"
TOKEN = None
ZONE_ID = None
IPINFO_TOKEN = ""

def print_help():
    print(
        f"""
        Configuration missing!
        ipinfo_token is optional, other keys are mandatory.

          [hetzner-dyndns]
          token=
          zone_id=
          record_name=
          ipinfo_token=

        Config locations:
        {"%s/.config/local-tooling/config.ini"%(os.environ.get("HOME"),)}
        {"/usr/local/etc/hetzner-dyndns.ini"}

        """
    )
    sys.exit(1)

def load_config():
  import configparser
  cfg = configparser.ConfigParser()
  cfg.read(
      ["%s/.config/local-tooling/config.ini"%(os.environ.get("HOME"),),
      "/usr/local/etc/hetzner-dyndns.ini"]
  )
  if not "hetzner-dyndns" in cfg:
    print_help()

  return cfg["hetzner-dyndns"]

cfg = load_config()
TOKEN = cfg["token"]
ZONE_ID = cfg["zone_id"]
RECORD_NAME = cfg["record_name"]

if "ipinfo_token" in cfg:
  IPINFO_TOKEN = cfg["ipinfo_token"]

if TOKEN is None or ZONE_ID is None or RECORD_NAME is None:
    print_help()

def ipinfo():
    response = requests.get(f"http://ipinfo.io?token={IPINFO_TOKEN}")
    data = json.loads(response.content)
    logger.debug(f"Got external IP: {data['ip']}")
    return data['ip']

def update_record(zone_id, name, type, value, token, record_id=None, ttl=3600, url=API_URL):
    """
    Update existing record

    zone: Name of the zone, e.g. example.org
    name: Name of the record, e.g. www
    type: Type of record. Valid values are A, AAAA, NS, MX, CNAME, RP, TXT, SOA, HINFO, SRV, DANE, TLSA, DS, CAA
    value: New value of the record, e.g. 127.0.0.1
    token: API token for the DNS API
    record_id: Record ID if record is not unique
    ttl: Time to live
    url: API URL to use
    """
    logger.debug(f"Updating record {name} for zone_id {zone_id}") 
    try:
        if url is None:
            return

        if record_id is None:
            record_id = _get_record_id(zone_id, name, type, token)

        response = requests.put(
            url=f"https://{url}/api/v1/records/{record_id}",
            headers={
                "Content-Type": "application/json",
                "Auth-API-Token": token,
            },
            data=json.dumps({
                "value": value,
                "ttl": ttl,
                "type": type,
                "name": name,
                "zone_id": zone_id
            })
        )

        status_code = response.status_code
        content = json.loads(response.content)

        if status_code == 200:
            print("record successful updated.")
        else:
            print(content['error']['message'])

    except requests.exceptions.RequestException as e:
        logger.exception(e)

def _get_record_id(zone_id, name, type, token):
    """ Get the record id if record is unique """
    logger.debug(f"Getting record id for {name}...")
    try:
        # get all records of domain
        response = requests.get(
            url=f"https://{API_URL}/api/v1/records",
            params={
                "zone_id": zone_id,
            },
            headers={
                "Auth-API-Token": token,
            },
        )

        status_code = response.status_code
        content = json.loads(response.content)

        if status_code == 200:
            records = content['records']
            matches = 0
            result = 0

            for rr in records:
                if rr['name'] == name and rr['type'] == type:
                    result = rr['id']
                    matches += 1

            if matches == 1:
                return result
            else:
                return False

        else:
            logger.error(f"Error occured : {content}")

    except requests.exceptions.RequestException as e:
        logger.exception(e)

def main():
    update_record(ZONE_ID, RECORD_NAME, "A", ipinfo(), TOKEN)
