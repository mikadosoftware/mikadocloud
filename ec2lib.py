

"""
Managing ec2 instances for mikado

1. Create Security Groups

webservers (nginx)
applicationservers (

run thru instances, see tags, any cname in a tag that is not in DNS
gets added to DNS.  Try to be idempotent later.
"""

from boto import ec2


REGION = "eu-west-1"
AMI = "ami-66ef0111"
# This is athe ami for 12.04 in EU-West, from
# http://cloud-images.ubuntu.com/locator/ec2/. It just is.

conn = ec2.connect_to_region(REGION)


def mk_webgroup():
    web = conn.create_security_group('nginx', 'Mikado Web Proxy Servers')
    web.authorize('tcp', 80, 80, '0.0.0.0/0', None)
    web.authorize('tcp', 443, 443, '0.0.0.0/0', None)
    web.authorize('tcp', 22, 22, '0.0.0.0/0', None)  # wow really??
    return web


def mk_appsvrs(web):
    """
    """
    app = conn.create_security_group('app_svrs', 'Flask app svrs')
    app.authorize('tcp', 8000, 8999, '0.0.0.0/0', web)
    app.authorize('tcp', 22, 22, '0.0.0.0/0', None)  # wow really??
    return app

# one time setup of security grpups
# really need to check and be idempotent
#sgs =  conn.get_all_security_groups()
    #websg = mk_webgroup()
#appsvrs = mk_appsvrs(websg)


# add an instance

def create_instance():
    conn.run_instances(
        AMI,
        key_name='pbrian_aws',
        instance_type='t1.micro',
        security_groups=['nginx', ])


def term_instance(instID):
    conn.terminate_instances(instance_ids=[instID, ])


def stop_instance(instID):
    conn.stop_instances(instance_ids=[instID, ])


def start_instance(instID):
    conn.start_instances(instance_ids=[instID, ])

import pprint


def show_all():
    reservations = conn.get_all_reservations()
    instances = reservations[0].instances
    for inst in instances:
        pprint.pprint(inst.__dict__)

        # print """
        # ID:%(id)s
        # dns:%(dns_name)s
        # current ip:%(ip_address)s
        #""" % inst.__dict__

        print "   ", inst.tags


# create_instance()



# show_all()
# create_instance()
# show_all()
