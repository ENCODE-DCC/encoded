# !bin/bash
#fetch the indexing time for each 0.1 of a second until status of waiting then
# calc start and end time. 
counter=0

	startTime=$(date 2>&1)

	indexerOutput=$(python jsonParse.py 2>&1)
while [ "$indexerOutput" == "indexing" ]
	do
		indexerOutput=$(python jsonParse.py 2>&1) 
		sleep 1
		((counter++))
	done
endTime=$(date 2>&1)

echo "Counter:" $counter

echo "StartTime: " $startTime
echo "EndTime: " $endTime
echo "Elapsed time: "

export IT_FINISH=1
