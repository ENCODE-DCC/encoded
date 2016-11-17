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
		##Locust
		osascript -e 'tell application "Terminal" to activate' -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' -e 'tell application "Terminal" to do script "locust -f locustfile.py --host='$URL_PREF'" in selected tab of the front window'
		time python3 ~/Documents/ENCODE-DCC-encoded/Master_ENCODE-DCC-encoded/ENCODE-DCC-encoded/pyencoded-tools/ENCODE_patch_set.py --infile fasq; python3 stress.py $URL_PREF;
 		fullExit
	fi
	
	else
		osascript -e 'tell application "Terminal" to activate' -e 'tell application "System Events" to tell process "Terminal" to keystroke "t" using command down' -e 'tell application "Terminal" to do script "locust -f locustfile.py --host='$URL_PREF'" in selected tab of the front window'
		time python3 ~/Documents/ENCODE-DCC-encoded/Master_ENCODE-DCC-encoded/ENCODE-DCC-encoded/pyencoded-tools/ENCODE_patch_set.py --infile fasq; python3 stress.py $URL_PREF;
		IT_FINISH=1
 		fullExit
fi
