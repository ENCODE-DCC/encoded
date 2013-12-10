Search Documentation:
=====================

**URIS**

1. http://{SERVER_NAME}/search/?searchTerm={term}
	Fetches all the documents which contain the text 'term'. 
	The result set includes wild card searches and the 'term' should be atleast 3 characters long. 
	
	- SERVER_NAME: ENCODE server
	- term: string that can be searched accross four item_types (i.e., experiment, biosample, antibody_approval, target)

2. http://{SERVER_NAME}/search/?type={item_type}
	Fetches all the documents of that particular 'item_type'

	- SERVER_NAME: ENCODE server
	- item_type: ENCODE item type (values can be: biosample, experiment, antibody_approval and target)

3. http://{SERVER_NAME}/search/?type={item_type}&{field_name}={text}
	Fetches and then filters all the documents of a particular item_type on that field 

	- SERVER_NAME: ENCODE server
	- item_type: ENCODE item type (values can be: biosample, experiment, antibody_approval and target)
	- field_name: Any of the json property in the ENCODE 'item_type' schema
