#!/bin/bash

for f in `ls tests`
do
percentage=`cat tests/$f | head -1`
cat tests/$f | grep ">" | cut -d ' ' -f 2 | sort > test_tmp.txt
cat tests/$f | grep "<" | cut -d ' ' -f 2 | sort > test_tmp1.txt
python3 minimize_net_list.py test_tmp.txt $percentage | cut -d ' ' -f 1 | sort > test_tmp2.txt
diff test_tmp1.txt test_tmp2.txt
if [ $? -ne 0 ]
then
    echo error in test: $f;
    break;
fi
done;
