
BIG_MASK = (1 << 32) - 1

def getMaskByMaskSize(mask_size):
    return BIG_MASK ^ ((1 << (32 - mask_size)) - 1)

class Net:
    def __init__(self, net: int, mask_size: int):
        self.mask_size = mask_size
        self.net = net & getMaskByMaskSize(mask_size)
        self.mask = getMaskByMaskSize(self.mask_size)

    def getNet(self):
        return self.net

    def getMaskSize(self):
        return self.mask_size

    def getMask(self):
        return getMaskByMaskSize(self.mask_size)

    def getIpVolume(self):
        return 1 << (32 - self.mask_size);

    def hasSubnet(self, Net: 'Net'):
        if Net.mask_size <= self.mask_size: return 0
        return self.net == Net.net & self.mask

    def isSameNet(self, Net: 'Net'):
        return Net.mask_size == self.mask_size and Net.net == self.net

    def getCommonNet(self, OtherNet: 'Net', min_mask_size: int):
        if self.mask_size <= min_mask_size: return 0
        if OtherNet.mask_size <= min_mask_size: return 0
        for mask_size in range(min(self.mask_size, OtherNet.mask_size) - 1, min_mask_size, -1):
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
    def __init__(self, net: Net, is_real_net: bool):
        self.net = net
        self.children = []
        self.is_real_net = is_real_net
        self.real_ip_volume = 0;

    def getNet(self):
        return self.net

    def addSubnet(self, NewNode: 'Node'):
        if not self.is_real_net and NewNode.is_real_net and self.net.isSameNet(NewNode.net):
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

    def printTree(self, level):
        str = ''
        for i in range(level):
            str = str + '    '
        print(str + self.net.getAsString())
        for i, Child in enumerate(self.children):
            Child.printTree(level + 1)

    def updateRealIpVolume(self):
        if self.is_real_net:
            self.real_ip_volume = self.net.getIpVolume();
        else:
            for Child in self.children:
                self.real_ip_volume += Child.updateRealIpVolume();
        return self.real_ip_volume;

    def printMinimizedList(self, percentage):
        current_percentage = 100 if self.is_real_net else 100 * self.real_ip_volume / self.net.getIpVolume()
        if (current_percentage >= percentage):
            print(self.net.getAsString() + ' ' + str(current_percentage))
        else:
            for Child in self.children:
                Child.printMinimizedList(percentage)