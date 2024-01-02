#!/usr/bin/env python

import os, sys
import requests
import json
from loguru import logger

API_URL = "dns.hetzner.com"
TOKEN = None
ZONE_ID = None

def print_help():
    print(
        f"""
        Configuration missing!
        All keys are mandatory.

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
  return cfg

cfg = load_config()
TOKEN = cfg["hetzner-dyndns"]["token"]
ZONE_ID = cfg["hetzner-dyndns"]["zone_id"]
RECORD_NAME = cfg["hetzner-dyndns"]["record_name"]

if TOKEN is None or ZONE_ID is None:
    print_help()

def ipinfo():
    URL = "http://ipinfo.io?token="
    response = requests.get(URL)
    data = json.loads(response.content)
    logger.debug(f"Got external IP: {data['ip']}")
    return data['ip']

def update_record(zone_id, name, type, value, token, record_id=None, name_new=None, ttl=3600, url=API_URL):
    """
    Update existing record

    :param zone: Name of the zone, eg. example.org
    :param name: Name of the record, eg. www
    :param value: New value of the record eg. 1.1.1.1
    :param type: Type of record eg. A, valid are A, AAAA, NS, MX, CNAME, RP, TXT, SOA, HINFO, SRV, DANE, TLSA, DS, CAA
    :param name_new: New name of the record, eg. www
    :param record_id: Record ID if record is not unique
    :param ttl: Time to live
    """
    try:
        if url is None:
            return

        if name_new is None:
            name_new = name

        if record_id is None:
            record_id = _get_record_id(zone_id, name, type, value)

        response = requests.put(
            url=f"https://{url}/api/v1/records/{record_id}",
            headers={
                "Content-Type": "application/json",
                "Auth-API-Token": token,
            },
            data=json.dumps({
                "value": value_new,
                "ttl": ttl,
                "type": type,
                "name": name_new,
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
            print("Error occured")
            print(content)

    except requests.exceptions.RequestException as e:
        logger.exception(e)

def main():
    update_record(ZONE_ID, RECORD_NAME, "A", ipinfo(), TOKEN)
