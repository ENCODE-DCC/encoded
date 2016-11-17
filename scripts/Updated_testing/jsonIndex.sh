# !/bin/bash


curl -v -H "Accept:application/json"  https://v46-2-master.demo.encodedcc.org/_indexer?status=DESC | python -m json.tool >> indexTime.txt


