#!/usr/local/bin/python3

import argparse
import sys
import net_tree
import re
import struct

parser = argparse.ArgumentParser(description='Minimizes list of IPv4 addresses and networks by collapsing some subnetworks.')
parser.add_argument('source', type=argparse.FileType('r'), help='File to read IP addresses from (use "-" to indicate stdin).')
parser.add_argument('N', type=int, help='Size of resulting list. The smaller it is, the more extra addresses will be included into resulting subnets.')
parser.add_argument('--mask', action='store_true', help='Use "1.2.3.4 255.255.255.0" output format instead of "1.2.3.4/24".')

args = parser.parse_args()

if args.N < 2:
    print('Min size is 2')
    sys.exit(1)

# Filling the binary tree
# Each node has maximum two children (by design)

Root = net_tree.Node(net_tree.Net(0,0), 0)
ipre = re.compile('(\d+)\.(\d+)\.(\d+)\.(\d+)(?:\/(\d+))?')
for line in args.source:
    result = ipre.search(line)
    if result:
        ip = 0
        for i in range(1, 5):
            ip = ip * 256 + int(result.group(i))

        if result.group(5):
            mask_size = int(result.group(5))
        else:
            mask_size = 32

        Root.addSubnet(net_tree.Node(net_tree.Net(ip, mask_size), 1))

# Collapsing the nodes untill we have a desired resulting list size
Root.finishTreeFirst();
Root.collapseRoot(Root.real_ip_records_count - args.N)

# printing the result
Root.printCollapsedTree('{addr} {mask}' if args.mask else '{addr}/{masklen}');

# printing some stats
print('### list size:    ' + str(Root.real_ip_records_count), file=sys.stderr)
print('### not real ips: ' + str(Root.added_fake_ip_volume), file=sys.stderr)
