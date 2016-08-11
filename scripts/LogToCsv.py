import re
#regex = '([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) "-" (.*?) "(.*?)" "(.*?)"'
pattern = re.compile('([(\d\.)]+) - - \[(.*?)\] "(.*?)" (\d+) (\d+) "-" "(.*?)" "(.*?)"')
pattern_trim = re.compile('([(\d\.)]+) - (.*?) \[(.*?)\] "(.*?)" (\d+) (\d+) "(.*?)" "(.*?)" (.*?)')

none_count = 0
elif_count = 0

file = open('encodeproject.org.log', 'r')

outputFile = open('encodeProjectToCSV.csv', 'w')

for line in file:
	result = re.search(pattern, line)
	result_trim = re.search(pattern_trim, line)
	
	if result:
		split_line = result.group(7)
		do_split = re.split(r'[-&?()]', split_line)
		completed_line = result.group(1,2,3,4,5,6), do_split

		outputFile.write(str(completed_line))
		outputFile.write("\n")
			
	elif not result:
		elif_count = +1
		split_line = result_trim.group(7)
		do_split = re.split(r'[-&?()]', split_line)
		completed_line = result_trim.group(1,3,4,5,6,8), do_split
		
		outputFile.write(str(completed_line))
		outputFile.write("\n")
	
	else:
		none_count = +1
		outputFile.write(line)
		
print("None count: %d" % none_count)
file.close()
outputFile.close()