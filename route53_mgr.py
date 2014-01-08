

"""operations:

`show` : show all instances, plus their current tags so we can see what they
should be

`update`: update all instances, based on their current tags

Needs, well, logging and stuff.

"""

from optparse import OptionParser
import libroute53 as r53


def showall():
    """
    dnsname to cnames
    """
    cmaps = r53.get_cnamemaps()
    for fqdn in cmaps:
        print "---------------------"
        print fqdn
        for alias in cmaps[fqdn]:
            print "   ", alias,
        print
        print

    z = r53.get_canonical_DNS()

    print "*****"
    cmaps2 = r53.sort_zoneinfo_by_canonicalname(z)
    for fqdn in cmaps2:
        print "---------------------"
        print fqdn
        for alias in cmaps2[fqdn]:
            print "   ", alias,
        print
        print

    # compare the dicts

    for fqdn in cmaps:
        if fqdn in cmaps2.keys():
            if sorted(cmaps[fqdn]) == sorted(cmaps2[fqdn]):
                print "%s is ok, all dns on servers match dns on r53" % fqdn
            else:
                print "%s fails, mismatch of %s and %s" % (fqdn,
                                                           cmaps[fqdn],
                                                           cmaps2[fqdn])
        else:
            print "%s is on a server but no Zone at all" % fqdn

    for fqdn in cmaps2:
        if fqdn in cmaps.keys():
            if sorted(cmaps[fqdn]) == sorted(cmaps2[fqdn]):
                print "%s is ok, all dns on servers match dns on r53" % fqdn
            else:
                print "%s fails, mismatch of %s and %s" % (fqdn,
                                                           cmaps[fqdn],
                                                           cmaps2[fqdn])
        else:
            print "%s is on Route53 but not on any instance" % fqdn


if __name__ == '__main__':

    parser = OptionParser()
    parser.add_option("-f", "--file", dest="filename",
                      help="write report to FILE", metavar="FILE")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")

    (options, args) = parser.parse_args()
    if "show" in args:
        showall()
