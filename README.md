# net_list_minimizer
a tool to combine networks list to desired size with the best possible accuracy

## how it works
* We build a binary tree out of all the nets in passed list. Finding the smallest common nets and creating fake net nodes.
* Then we calculate weight for all the nets. Weight is as bigger as much we can reduce the list size if we collapse the net. And as lower as many bad IPs are covered by that net.
* Then we recursively collapse nets starting from those who has the biggest weight (the biggest weight is infinity) until we have desired list size.

The difficult thing is that weight of the parent nets is changed when we collapse it's child.

## Usage

python3 minimize_net_list.py real_net_list_example.txt 30000 | grep -v ### > result.txt
