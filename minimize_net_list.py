#!/usr/local/bin/python3

import sys
import net_tree
import re
import struct

if len(sys.argv) < 3:
    print('You must give me a filename and required list size')
    sys.exit()

filename = str(sys.argv[1])
required_list_size = int(sys.argv[2])
if required_list_size < 2:
    print('Min size is 2')
    sys.exit()

file = open(filename, "r")
if not file:
    print('Cant open file')
    sys.exit()

# Filling the binary tree
# Each node has maximum two children (by design)

Root = net_tree.Node(net_tree.Net(0,0), 0)
for line in file.readlines():
    result = re.search('(\d+)\.(\d+)\.(\d+)\.(\d+)(?:\/(\d+))?', line)
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
Root.collapseRoot(Root.real_ip_records_count - required_list_size)

# printing the result
Root.printCollapsedTree();

# printing some stats
print('### list size:    ' + str(Root.real_ip_records_count))
print('### not real ips: ' + str(Root.getNotRealIpCount()))