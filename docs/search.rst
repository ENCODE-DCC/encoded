**Search Documentation:**


**URIS**

http://{SERVER_NAME}/search/?searchTerm={term}

	Fetches all the documents which contain the 'term'. 
	The result set includes wild card searches and the 'term' should be atleast 3 characters long. 
	
	SERVER_NAME - ENCODE production server
	term - string that can be searched accross four item_types (i.e., experiment, biosample, antibody_approval, target)

http://{SERVER_NAME}/search/?type={item_type}


http://{SERVER_NAME}/search/?searchTerm={term}&type={item_type}&{field_field}={text_field}