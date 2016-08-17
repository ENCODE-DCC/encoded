# !/bin/bash
# stress.py needs the access  and the URL and keys in keyfile.json need to be updated for the instance
# To get the access keys for relesanator login to the server you are testing 
# access your profile
# create your access keys 
URL_PREF=$1
export URL_PREF
IT_FINISH=0
export IT_FINISH

#fullExit allows the indexer timer to finish 
function fullExit () {
	#echo "IT_FINISH: " $IT_FINISH
		
		while [ $IT_FINISH == "0" ]
			do
				sleep 1
			done
		exit
}

indexerOutput=$(python jsonParse.py 2>&1)
echo "Status: " $indexerOutput

./indexerTimer.sh indexerOutput &

if [ $indexerOutput == "indexing" ];then
	echo "server is still indexing do you wish to continue with the tests? yes/no"
	read input

	if [ $input == "no" ];then
		echo "Do you wish to stop the indexing timer? yes/no"
		read timerInput
			if [ timerInput == "yes" ];then
				IT_FINISH=1
			fi
	else
		time python3 ~/Documents/ENCODE-DCC-encoded/pyencoded-tools/ENCODE_patch_set.py --key test --accession 4c911ae3-9007-4777-9680-2c526ab8fdbb --field aliases:encode --data "test:Preformance" --update; python3 stress.py $URL_PREF;
 		fullExit
	fi
	
	else
		time python3 ~/Documents/ENCODE-DCC-encoded/pyencoded-tools/ENCODE_patch_set.py --key test --accession 4c911ae3-9007-4777-9680-2c526ab8fdbb --field aliases:encode --data "test:Preformance" --update; python3 stress.py $URL_PREF;
		IT_FINISH=1
 		fullExit
fi
