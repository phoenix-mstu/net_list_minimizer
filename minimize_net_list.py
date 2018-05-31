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

# Updating real ip counters in each node

Root.finishTree();

# Making a flat list of fake nodes, in this list each node has a weight atribute.
# Nodes width less fake ip volume will have lower weight

nodesByFakeIpVolume = []
Root.getNodesByFakeIpVolume(nodesByFakeIpVolume)

# Sort nodes in list by weight.
# So collapsing the first nodes in list will have less impact on count of "not real" ips in script result
# with a greater impact on reducing resulting ips list size

nodesByFakeIpVolume.sort(key=lambda x: x[0])

# Collapsing the nodes untill we have a desired resulting list size

list_size = Root.real_ip_records_count
for nodeArr in nodesByFakeIpVolume:
    Node = nodeArr[1]
    if Node.is_collapsed: continue

    # Each fake node has several child ips that are returned in a resulting list
    # After collapsing the node resulting list size will be reduced on count of the ips that were collapsed
    # And increased by 1 - all these ips will be replaced by a single ip
    list_size = list_size + 1 - Node.recursiveCollapse()

    if list_size <= required_list_size: break

# printing the result
Root.printCollapsedTree();

# printing some stats
print('### list size:    ' + str(list_size))
print('### not real ips: ' + str(Root.getNotRealIpCount()))