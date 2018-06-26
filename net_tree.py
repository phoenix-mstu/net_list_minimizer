
BIG_MASK = (1 << 32) - 1

def getMaskByMaskSize(mask_size):
    return BIG_MASK ^ ((1 << (32 - mask_size)) - 1)

def getIpVolumeByMaskSize(mask_size):
    return 1 << (32 - mask_size);

class Net:
    def __init__(self, net: int, mask_size: int):
        self.mask_size = mask_size
        self.net = net & getMaskByMaskSize(mask_size)
        self.mask = getMaskByMaskSize(self.mask_size)
        self.ip_volume = getIpVolumeByMaskSize(mask_size)

    def hasSubnet(self, Net: 'Net'):
        if Net.mask_size <= self.mask_size: return 0
        return self.net == Net.net & self.mask

    def isSameNet(self, Net: 'Net'):
        return (Net.mask_size == self.mask_size) and (Net.net == self.net)

    def getCommonNet(self, OtherNet: 'Net', min_mask_size: int):
        if self.mask_size <= min_mask_size: return 0
        if OtherNet.mask_size <= min_mask_size: return 0
        for mask_size in range(min(self.mask_size, OtherNet.mask_size) - 1, min_mask_size - 1, -1):
          mask = getMaskByMaskSize(mask_size)
          if (self.net & mask) == (OtherNet.net & mask):
              return Net(self.net, mask_size)
        return 0

    def getAsString(self):
        net = self.net
        bytes = []
        for i in range(4):
            bytes.append(str(net % 256))
            net = net >> 8

        return '.'.join(reversed(bytes)) + ('' if self.mask_size == 32 else "/" + str(self.mask_size))

class Node:
    def __init__(self, net: Net, is_real_net: int):
        self.net = net
        self.children = []
        self.is_real_net = is_real_net
        self.real_ip_volume = 0
        self.real_ip_records_count = 0
        self.weight = 0.0
        self.max_child_weight = 0.0

    def getNet(self):
        return self.net

    def addSubnet(self, NewNode: 'Node'):
        if self.net.isSameNet(NewNode.net):
            if not self.is_real_net and NewNode.is_real_net:
                self.is_real_net = 1
                self.children = []
            return 1

        if self.is_real_net and self.net.hasSubnet(NewNode.net):
            return 1

        if not self.net.hasSubnet(NewNode.net):
            return 0

        for Child in self.children:
            if Child.addSubnet(NewNode):
                return 1

        for i, Child in enumerate(self.children):
            CommonNet = Child.net.getCommonNet(NewNode.net, self.net.mask_size + 1)
            if CommonNet:
                CommonNode = Node(CommonNet, 0)
                CommonNode.addSubnet(NewNode)
                CommonNode.addSubnet(Child)
                self.children[i] = CommonNode
                return 1

        self.children.append(NewNode)
        return 1

    def printTree(self, level):
        prefix = ''
        for i in range(level):
            prefix = prefix + '    '

        if self.is_real_net: sign = '*'
        elif self.weight == 0: sign = '.'
        else: sign = ''

        print(prefix + self.net.getAsString() + ' ' + str(self.real_ip_records_count))
        for i, Child in enumerate(self.children):
            Child.printTree(level + 1)

    def finishTreeFirst(self):
        if self.is_real_net:
            self.real_ip_volume = self.net.ip_volume
            self.real_ip_records_count = 1
            self.weight = 0
            self.max_child_weight = 0
        else:
            self.real_ip_volume = 0
            self.real_ip_records_count = 0
            self.max_child_weight = 0
            for Child in self.children:
                Child.finishTreeFirst()
                self.real_ip_volume += Child.real_ip_volume
                self.real_ip_records_count += Child.real_ip_records_count
                self.max_child_weight = max(self.max_child_weight, Child.weight, Child.max_child_weight)
            self.recalcWeight()

    def collapse(self, min_weight, max_net_delta):
        net_delta = 0
        self.max_child_weight = 0
        for Child in self.children:
            if net_delta < max_net_delta and min_weight <= max(Child.weight, Child.max_child_weight):
                net_delta += Child.collapse(min_weight, max_net_delta - net_delta)
            self.max_child_weight = max(self.max_child_weight, Child.weight, Child.max_child_weight)

        if net_delta > 0:
            self.real_ip_records_count -= net_delta
            self.recalcWeight()

        # trying to collapse self
        if self.weight >= min_weight:
            self.weight = 0
            self.max_child_weight = 0
            return self.real_ip_records_count - 1
        else:
            return net_delta

    def collapseRoot(self, required_net_delta):
        while required_net_delta > 0:
            required_net_delta -= self.collapse(self.max_child_weight, required_net_delta)

    def printCollapsedTree(self):
        if self.is_real_net or self.weight == 0:
            print(self.net.getAsString())
        else:
            for Child in self.children:
                Child.printCollapsedTree()

    def recalcWeight(self):
        if self.net.ip_volume - self.real_ip_volume:
            self.weight = (self.real_ip_records_count - 1) / (self.net.ip_volume - self.real_ip_volume)
        else:
            self.weight = float('Inf')

    def getNotRealIpCount(self):
        if self.is_real_net: return 0
        if self.weight == 0: return self.net.ip_volume - self.real_ip_volume
        res = 0
        for Child in self.children:
            res = res + Child.getNotRealIpCount()
        return res



