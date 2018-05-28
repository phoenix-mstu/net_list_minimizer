#!/usr/local/bin/python3

import sys
import net_tree
import re
import struct

if len(sys.argv) < 3:
    print('You must give me a filename and percentage')
    sys.exit()

filename = str(sys.argv[1])
percentage = int(sys.argv[2])

file = open(filename, "r")
if not file:
    print('Cant open file')
    sys.exit()

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
#         Root.printTree(0);


Root.updateRealIpVolume();
Root.printMinimizedList(percentage);

