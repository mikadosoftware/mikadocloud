"""change = changes.add_change("DELETE", "test.example.com", "A")
change.add_value("10.1.1.1")
result = changes.commit()

We want to CREATE, DELETE, UPDATE records

unit Testing is a bugger...


Keeping DNS records uptodate has always been a bit of a bugger.

Someone always forgets to update the spreadsheet mapping 10.1.1.1 to zeus and
then it all falls apart evermore.

Now in Cloud-land its even more awkward, as we are not in command of our
IP addresses anymore, and have to wait till *after* we have turned the
VM on to find out which machine it is and what the IP is.

So, what we want is *either* a mapping between AWS instance IDs and the desired
fqdn, or a means of querying each machine and asking it what it thinks it should be.

I prefer the second, but thats a lot more work

"""


import boto
from boto import ec2
from conf import get_config


class ConfigError(Exception):
    pass

confd = get_config('dns.ini')

REGION = "eu-west-1"
# Module global, because ...
r53conn = boto.connect_route53()
HOSTEDZONEID = "Z37ZH240XSI8D6"


def get_canonical_DNS():
    """
    iterate over all instances in this connection,
    and gather the self-declared domain names


    returns a list of ResourceRecord Objects representing
    a record within a zone file
    """
    zones = {}
    allzones = r53conn.get_all_hosted_zones()
    for zone in allzones[u'ListHostedZonesResponse'][u'HostedZones']:

        name = zone['Name']
        zone_id = zone['Id'].replace("/hostedzone/", "")

        sets = r53conn.get_all_rrsets(zone_id)
        records = []
        for rec in sets:
            records.append(rec)
        zones[name] = records

    return zones


def sort_zoneinfo_by_canonicalname(zones):
    """
    """
    cnames = {}
    for z, records in zones.items():
        for rec in records:
            if rec.type == "CNAME":

                cnames.setdefault(rec.resource_records[0],
                                  []).append(rec.name)
    return cnames


def get_all_instances_by_region(region):
    """
    return list of all `Instance` objects in this account, this region

    AWS keeps instances in different 'reservations', as a billing convenience
    but really represents a set of instances started at the same time.
    http://boto.s3.amazonaws.com/ec2_tut.html

    """
    instances = []
    ec2conn = ec2.connect_to_region(region)
    reservations = ec2conn.get_all_reservations()
    for res in reservations:
        instances.extend(res.instances)
    return instances


def extract_CNAMES_by_instance(instances):
    cnamemaps = {}

    for inst in instances:
        for key in inst.tags.keys():
            if key.find("CNAME") != -1:
                cname = inst.tags[key]
                cnamemaps.setdefault(inst.dns_name, []).append(cname)
    return cnamemaps


def map_instances_by_machinename(instances):
    """
    A MACHINENAME is the unique name for a running host
    that we shall use throughout the org to determine
    what that host should be / do.

    The host simply says I am "this name".  AS long as that
    is not in conflict, fine.

    """
    machinenames = {}

    for inst in instances:
        if "MACHINENAME" in inst.tags.keys():
            machinenames[inst.tags['MACHINENAME']] = inst
        else:
            raise ConfigError("An instance has no valid MACHINENAME tag: %s"
                              % inst.dns_name)

    return machinenames


def change_record(create, recordtype, fqdn, ipaddr):
    """
    """
    if create == True:
        action = "CREATE"
    else:
        action = "DELETE"

    changes = boto.route53.record.ResourceRecordSets(conn, "Z37ZH240XSI8D6")
    change = changes.add_change(action, fqdn, recordtype)
    change.add_value(ipaddr)
    result = changes.commit()
    return result


def add_A_record(fqdn, ipaddr):
    change_record(True,
                  "A",
                  fqdn,
                  ipaddr
                  )


def delete_A_record(fqdn, current_ipaddr, new_ipaddr):
    change_record(False,
                  "A",
                  fqdn,
                  current_ipaddr
                  )


def update_A_record(fqdn, current_ipaddr, new_ipaddr):
    delete_A_record(fqdn, current_ipaddr, new_ipaddr)
    add_A_record(fqdn, new_ipaddr)


def add_CNAME(fqdn, tgtfqdn):
    """
    """
    print "Try adding %s to %s" % (fqdn, tgtfqdn)
    try:
        change_record(True,
                      "CNAME",
                      fqdn,
                      tgtfqdn
                      )
    except boto.route53.exception.DNSServerError, e:
        try:
            change_record(False,
                          "CNAME",
                          fqdn,
                          tgtfqdn
                          )
        except:
            pass

        change_record(True,
                      "CNAME",
                      fqdn,
                      tgtfqdn
                      )


def get_cnamemaps():

    instances = get_all_instances_by_region(REGION)
    #machinenames = map_instances_by_machinename(instances)
    cnamemaps = extract_CNAMES_by_instance(instances)
    return cnamemaps


def update_all_DNS_by_tag():
    """
    force update of route53 for each CNAME claimed in tags

    """

    instances = get_all_instances_by_region(REGION)
    #machinenames = map_instances_by_machinename(instances)
    cnamemaps = extract_CNAMES_by_instance(instances)

    #update_A_record("phab.cleanpython.com", "192.168.1.1", "192.168.1.2")
    for canonicalname in cnamemaps:
        for alias in cnamemaps[canonicalname]:
            add_CNAME(alias, canonicalname)
