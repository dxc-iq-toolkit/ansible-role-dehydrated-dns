#!/usr/bin/env python

# How to use:
#
# Ubuntu 16.04: apt install -y python-boto
#
# Specify the default profile on aws/boto profile files or use the optional AWS_PROFILE env var:
# AWS_PROFILE=example ./dehydrated -c -d example.com -t dns-01 -k /etc/dehydrated/hooks/route53.py
#
# Manually specify hosted zone:
# HOSTED_ZONE=example.com AWS_PROFILE=example ./dehydrated -c -d example.com -t dns-01 -k /etc/dehydrated/hooks/route53.py
#
# More info about dehaydrated and dns challenge: https://github.com/lukas2511/dehydrated/wiki/Examples-for-DNS-01-hooks
# Using AWS Profiles: http://docs.aws.amazon.com/cli/latest/userguide/cli-chap-getting-started.html#cli-multiple-profiles

import os
import sys
from boto.route53 import connection, record
from time import sleep

# After dehydrated receives a text challenge, dehydrated passes this function
# the text challenge received from LetsEncrypt, along with each domain and
# possibly subdomain outlined in domains.txt
def route53_dns(domain, txt_challenge, action='upsert'):
    #boto function -- creates a connection to route53.amazonaws.com
    conn = connection.Route53Connection()

    #we set this environment variable via ancible. The below if/else statement is
    #just trying to get the Hosted Zone ID of the given domain.

    if 'HOSTED_ZONE_ID' in os.environ:
      zone_id = os.environ['HOSTED_ZONE_ID']

      #returns data structure of info about domain (VPCs, ResourceRecordSet count, privacy etc)
      zone = conn.get_hosted_zone(zone_id)
      hosted_zone_name = zone['GetHostedZoneResponse']['HostedZone']['Name'].strip('.')

      #check if dehydrated response is correct one for this domain and/or subdomain
      if not domain.endswith(hosted_zone_name):
        raise Exception("Incorrect hosted zone for domain {0}".format(domain))

    else:
      zones = conn.get_all_hosted_zones()
      for zone in zones['ListHostedZonesResponse']['HostedZones']:
        if "{0}.".format(domain).endswith(zone['Name']):
          zone_id = zone['Id'].replace('/hostedzone/', '')
          break
      else:
        raise Exception("Hosted zone not found for domain {0}".format(domain))

    #creates a ResourceRecordSet object to store the given text challenge
    change_set = record.ResourceRecordSets(conn, zone_id)
    #adds a change request to DNS record with text challenge and commits it
    change = change_set.add_change("{0}".format(action.upper()), '_acme-challenge.{0}'.format(domain), type='TXT', ttl=90)
    change.add_value('"{0}"'.format(txt_challenge))
    change_set.commit()

    if action.upper() == 'UPSERT':
      # wait for DNS update
      sleep(45)

#ensures that script is running in top level environment
if __name__ == "__main__":
    #identifies the vars sent to this script by dehydrated
    hook = sys.argv[1]
    print("hook: {0}".format(hook))
    try:
      domain = sys.argv[2]
      txt_challenge = sys.argv[4]
      print("domain: {0}".format(domain))
      print("txt_challenge: {0}".format(txt_challenge))
    except:
      print("This hook script doesn't have any more relevant arguments.")


    if hook == "deploy_challenge":
        route53_dns(domain, txt_challenge, 'upsert')
    elif hook == "clean_challenge":
        route53_dns(domain, txt_challenge, 'delete')
