#!/bin/bash
IFS=$'\n'
j=0
i=1
for line in `cat domain.txt`
do
  let j=i++
  echo "-----------------------第'$j'次获取----搜集目标: '$line' -----------------------"
  python3 batch.py -d $line -k -ws -cs -ss -o
  sleep 2
done