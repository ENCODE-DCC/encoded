#!/usr/bin/env python3
# -*- coding: latin-1 -*-

import requests
import json
import sys
import logging
from urllib.parse import urljoin
from urllib.parse import quote
import os.path
import hashlib
import copy
import subprocess

class dict_diff(object):
    """
    Calculate items added, items removed, keys same in both but changed values,
    keys same in both and unchanged values
    """
    def __init__(self, current_dict, past_dict):
        self.current_dict, self.past_dict = current_dict, past_dict
        self.current_keys, self.past_keys = [
            set(d.keys()) for d in (current_dict, past_dict)
        ]
        self.intersect = self.current_keys.intersection(self.past_keys)

    def added(self):
        diff = self.current_keys - self.intersect
        if diff == set():
            return None
        else:
            return diff

    def removed(self):
        diff = self.past_keys - self.intersect
        if diff == set():
            return None
        else:
            return diff

    def changed(self):
        diff = set(o for o in self.intersect
                   if self.past_dict[o] != self.current_dict[o])
        if diff == set():
            return None
        else:
            return diff

    def unchanged(self):
        diff = set(o for o in self.intersect
                   if self.past_dict[o] == self.current_dict[o])
        if diff == set():
            return None
        else:
            return diff

    def same(self):
        return self.added() is None and self.removed() is None and self.changed() is None


class ENC_Key:
    def __init__(self, keyfile, keyname):
        if os.path.isfile(str(keyfile)):
            keys_f = open(keyfile, 'r')
            keys_json_string = keys_f.read()
            keys_f.close()
            keys = json.loads(keys_json_string)
        else:
            keys = keyfile
        key_dict = keys[keyname]
        self.authid = key_dict['key']
        self.authpw = key_dict['secret']
        self.server = key_dict['server']
        if not self.server.endswith("/"):
            self.server += "/"


class ENC_Connection(object):
    def __init__(self, key):
        self.headers = {'content-type': 'application/json', 'accept': 'application/json'}
        self.server = key.server
        self.auth = (key.authid, key.authpw)


class ENC_Collection(object):
    def __init__(self, connection, supplied_name, frame='object'):
        if supplied_name.endswith('s'):
            self.name = supplied_name.replace('_', '-')
            self.search_name = supplied_name.rstrip('s').replace('-', '_')
            self.schema_name = self.search_name + '.json'
        elif supplied_name.endswith('.json'):
            self.name = supplied_name.replace('_', '-').rstrip('.json')
            self.search_name = supplied_name.replace('-', '_').rstrip('.json')
            self.schema_name = supplied_name
        else:
            self.name = supplied_name.replace('_', '-') + 's'
            self.search_name = supplied_name.replace('-', '_')
            self.schema_name = supplied_name.replace('-', '_') + '.json'
        schema_uri = '/profiles/' + self.schema_name
        self.connection = connection
        self.server = connection.server
        self.schema = get_ENCODE(schema_uri, connection)
        self.frame = frame
        search_string = '/search/?format=json&limit=all&\
                        type=%s&frame=%s' % (self.search_name, frame)
        collection = get_ENCODE(search_string, connection)
        self.items = collection['@graph']
        self.es_connection = None

    def query(self, query_dict, maxhits=10000):
        from pyelasticsearch import ElasticSearch
        if self.es_connection is None:
            es_server = self.server.rstrip('/') + ':9200'
            self.es_connection = ElasticSearch(es_server)
        results = self.es_connection.search(query_dict, index='encoded',
                                            doc_type=self.search_name,
                                            size=maxhits)
        return results

global schemas
schemas = []


class ENC_Schema(object):
    def __init__(self, connection, uri):
        self.uri = uri
        self.connection = connection
        self.server = connection.server
        response = get_ENCODE(uri, connection)
        self.properties = response['properties']


class ENC_Item(object):
    def __init__(self, connection, id, frame='object'):
        self.id = id
        self.connection = connection
        self.server = connection.server
        self.frame = frame

        if id is None:
            self.type = None
            self.properties = {}
        else:
            if id.rfind('?') == -1:
                get_string = id + '?'
            else:
                get_string = id + '&'
            get_string += 'frame=%s' % (frame)
            item = get_ENCODE(get_string, connection)
            self.type = next(x for x in item['@type'] if x != 'item')
            self.properties = item

    def get(self, key):
        try:
            return self.properties[key]
        except KeyError:
            return None

    def sync(self):
        if self.id is None:  # There is no id, so this is a new object to POST
            excluded_from_post = ['schema_version']
            self.type = self.properties.pop('@type')
            schema_uri = 'profiles/%s.json' % (self.type)
            try:
                schema = next(x for x in schemas if x.uri == schema_uri)
            except StopIteration:
                schema = ENC_Schema(self.connection, schema_uri)
                schemas.append(schema)

            post_payload = {}
            for prop in self.properties:
                if prop in schema.properties and prop not in excluded_from_post:
                    post_payload.update({prop: self.properties[prop]})
                else:
                    pass
            # should return the new object that comes back from the patch
            new_object = new_ENCODE(self.connection, self.type, post_payload)

        else:  # existing object to PATCH or PUT
            if self.id.rfind('?') == -1:
                get_string = self.id + '?'
            else:
                get_string = self.id + '&'
            get_string += 'frame=%s' % (self.frame)
            on_server = get_ENCODE(get_string, self.connection)
            diff = dict_diff(on_server, self.properties)
            if diff.same():
                logging.warning("%s: No changes to sync" % (self.id))
            elif diff.added() or diff.removed():  # PUT
                excluded_from_put = ['schema_version']
                schema_uri = '/profiles/%s.json' % (self.type)
                try:
                    schema = next(x for x in schemas if x.uri == schema_uri)
                except StopIteration:
                    schema = ENC_Schema(self.connection, schema_uri)
                    schemas.append(schema)

                put_payload = {}
                for prop in self.properties:
                    if prop in schema.properties and prop not in excluded_from_put:
                        put_payload.update({prop: self.properties[prop]})
                    else:
                        pass
                # should return the new object that comes back from the patch
                new_object = replace_ENCODE(self.id, self.connection, put_payload)

            else:  # PATCH

                excluded_from_patch = ['schema_version', 'accession', 'uuid']
                patch_payload = {}
                for prop in diff.changed():
                    if prop not in excluded_from_patch:
                        patch_payload.update({prop: self.properties[prop]})
                # should probably return the new object that comes back from the patch
                new_object = patch_ENCODE(self.id, self.connection, patch_payload)

        return new_object

    def new_creds(self):
        if self.type.lower() == 'file':  # There is no id, so this is a new object to POST
            r = requests.post("%s/%s/upload/" % (self.connection.server, self.id),
                              auth=self.connection.auth,
                              headers=self.connection.headers,
                              data=json.dumps({}))
            return r.json()['@graph'][0]['upload_credentials']
        else:
            return None


def get_ENCODE(obj_id, connection, frame="object"):
    '''GET an ENCODE object as JSON and return as dict'''
    if frame is None:
        if '?' in obj_id:
            url = urljoin(connection.server, obj_id+'&limit=all')
        else:
            url = urljoin(connection.server, obj_id+'?limit=all')
    elif '?' in obj_id:
        url = urljoin(connection.server, obj_id+'&limit=all&frame='+frame)
    else:
        url = urljoin(connection.server, obj_id+'?limit=all&frame='+frame)
    logging.debug('GET %s' % (url))
    response = requests.get(url, auth=connection.auth, headers=connection.headers)
    logging.debug('GET RESPONSE code %s' % (response.status_code))
    try:
        if response.json():
            logging.debug('GET RESPONSE JSON: %s' % (json.dumps(response.json(), indent=4, separators=(',', ': '))))
    except:
        logging.debug('GET RESPONSE text %s' % (response.text))
    if not response.status_code == 200:
        if response.json().get("notification"):
            logging.warning('%s' % (response.json().get("notification")))
        else:
            logging.warning('GET failure.  Response code = %s' % (response.text))
    return response.json()


def replace_ENCODE(obj_id, connection, put_input):
    '''PUT an existing ENCODE object and return the response JSON
    '''
    if isinstance(put_input, dict):
        json_payload = json.dumps(put_input)
    elif isinstance(put_input, str):
        json_payload = put_input
    else:
        logging.warning('Datatype to PUT is not string or dict.')
    url = urljoin(connection.server, obj_id)
    logging.debug('PUT URL : %s' % (url))
    logging.debug('PUT data: %s' % (json_payload))
    response = requests.put(url, auth=connection.auth, data=json_payload,
                            headers=connection.headers)
    logging.debug('PUT RESPONSE: %s' % (json.dumps(response.json(), indent=4,
                                                   separators=(',', ': '))))
    if not response.status_code == 200:
        logging.warning('PUT failure.  Response = %s' % (response.text))
    return response.json()


def patch_ENCODE(obj_id, connection, patch_input):
    '''PATCH an existing ENCODE object and return the response JSON
    '''
    if isinstance(patch_input, dict):
        json_payload = json.dumps(patch_input)
    elif isinstance(patch_input, str):
        json_payload = patch_input
    else:
        print('Datatype to PATCH is not string or dict.', file=sys.stderr)
    url = urljoin(connection.server, obj_id)
    logging.debug('PATCH URL : %s' % (url))
    logging.debug('PATCH data: %s' % (json_payload))
    response = requests.patch(url, auth=connection.auth, data=json_payload,
                              headers=connection.headers)
    logging.debug('PATCH RESPONSE: %s' % (json.dumps(response.json(), indent=4,
                                                     separators=(',', ': '))))
    if not response.status_code == 200:
        logging.warning('PATCH failure.  Response = %s' % (response.text))
    return response.json()


def new_ENCODE(connection, collection_name, post_input):
    '''POST an ENCODE object as JSON and return the response JSON
    '''
    if isinstance(post_input, dict):
        json_payload = json.dumps(post_input)
    elif isinstance(post_input, str):
        json_payload = post_input
    else:
        print('Datatype to POST is not string or dict.', file=sys.stderr)
    url = urljoin(connection.server, collection_name)
    logging.debug("POST URL : %s" % (url))
    logging.debug("POST data: %s" % (json.dumps(post_input,
                                     sort_keys=True, indent=4,
                                     separators=(',', ': '))))
    response = requests.post(url, auth=connection.auth,
                             headers=connection.headers, data=json_payload)
    logging.debug("POST RESPONSE: %s" % (json.dumps(response.json(),
                                         indent=4, separators=(',', ': '))))
    if not response.status_code == 201:
        logging.warning('POST failure. Response = %s' % (response.text))
    logging.debug("Return object: %s" % (json.dumps(response.json(),
                                         sort_keys=True, indent=4,
                                         separators=(',', ': '))))
    return response.json()


def flat_one(JSON_obj):
    try:
        return [JSON_obj[identifier] for identifier in
                ['accession', 'name', 'email', 'title', 'uuid', 'href']
                if identifier in JSON_obj][0]
    except:
        return JSON_obj


def flat_ENCODE(JSON_obj):
    flat_obj = {}
    for key in JSON_obj:
        if isinstance(JSON_obj[key], dict):
            flat_obj.update({key: flat_one(JSON_obj[key])})
        elif isinstance(JSON_obj[key], list) and JSON_obj[key] != [] and isinstance(JSON_obj[key][0], dict):
            newlist = []
            for obj in JSON_obj[key]:
                newlist.append(flat_one(obj))
            flat_obj.update({key: newlist})
        else:
            flat_obj.update({key: JSON_obj[key]})
    return flat_obj


def pprint_ENCODE(JSON_obj):
    if ('type' in JSON_obj) and (JSON_obj['type'] == "object"):
        print(json.dumps(JSON_obj['properties'],
                         sort_keys=True, indent=4, separators=(',', ': ')))
    else:
        print(json.dumps(flat_ENCODE(JSON_obj),
                         sort_keys=True, indent=4, separators=(',', ': ')))


class GetFields():
    def __init__(self, connection, args, facet=None):
        self.connection = connection
        self.data = []
        self.header = []
        self.accessions = []
        self.fields = []
        self.subobj = ""
        self.facet = facet
        self.args = args

    def setup(self):
        ''' facet contains a list with the first item being a list
        of the accessions and the second a list of the fieldnames
        essentially: facet = [ [accession1, accession2, ...], [field1, field2, ...] ]'''
        if self.facet:
            self.accessions = self.facet[0]
            self.fields = self.facet[1]
        else:
            temp = []
            if self.args.collection:
                if self.args.es:
                    temp = get_ENCODE("/search/?type=" + self.args.collection, self.connection).get("@graph", [])
                else:
                    temp = get_ENCODE(self.args.collection, self.connection, frame=None).get("@graph", [])
            elif self.args.query:
                if "search" in self.args.query:
                    temp = get_ENCODE(self.args.query, self.connection).get("@graph", [])
                else:
                    temp = [get_ENCODE(self.args.query, self.connection)]
            elif self.args.object:
                if os.path.isfile(self.args.object):
                    self.accessions = [line.strip() for line in open(self.args.object)]
                else:
                    self.accessions = self.args.object.split(",")
            if any(temp):
                for obj in temp:
                    if obj.get("accession"):
                        self.accessions.append(obj["accession"])
                    elif obj.get("uuid"):
                        self.accessions.append(obj["uuid"])
                    elif obj.get("@id"):
                        self.accessions.append(obj["@id"])
                    elif obj.get("aliases"):
                        self.accessions.append(obj["aliases"][0])
                    else:
                        print("ERROR: object has no identifier", file=sys.stderr)
            if self.args.allfields:
                if self.args.collection:
                    obj = get_ENCODE("/profiles/" + self.args.collection + ".json", self.connection).get("properties")
                else:
                    obj_type = get_ENCODE(self.accessions[0], self.connection).get("@type")
                    if any(obj_type):
                        obj = get_ENCODE("/profiles/" + obj_type[0] + ".json", self.connection).get("properties")
                self.fields = list(obj.keys())
                for key in obj.keys():
                    if obj[key]["type"] == "string":
                        self.header.append(key)
                    else:
                        self.header.append(key + ":" + obj[key]["type"])
                self.header.sort()
            elif self.args.field:
                if os.path.isfile(self.args.field):
                    self.fields = [line.strip() for line in open(self.args.field)]
                else:
                    self.fields = self.args.field.split(",")
        if len(self.accessions) == 0:
            print("ERROR: Need to provide accessions", file=sys.stderr)
            sys.exit(1)
        if len(self.fields) == 0:
            print("ERROR: Need to provide fields!", file=sys.stderr)
            sys.exit(1)

    def get_fields(self):
        import csv
        from collections import deque
        self.setup()
        self.header = ["accession"]
        for acc in self.accessions:
            acc = quote(acc)
            obj = get_ENCODE(acc, self.connection)
            newObj = {}
            newObj["accession"] = acc
            for f in self.fields:
                path = deque(f.split("."))  # check to see if someone wants embedded value
                field = self.get_embedded(path, obj)  # get the last element in the split list
                if field:  # after the above loop, should have final field value
                    name = f
                    if not self.facet:
                        name = name + self.get_type(field)
                    newObj[name] = field
                    if not self.args.allfields:
                        if name not in self.header:
                            self.header.append(name)
            self.data.append(newObj)
        if not self.facet:
            writer = csv.DictWriter(sys.stdout, delimiter='\t', fieldnames=self.header)
            writer.writeheader()
            for d in self.data:
                writer.writerow(d)

    def get_type(self, attr):
        ''' given an object return its type as a string to append
        '''
        if type(attr) == int:
            return ":integer"
        elif type(attr) == list:
            return ":array"
        elif type(attr) == dict:
            return ":dict"
        else:
            # this must be a string
            return ""

    def get_embedded(self, path, obj):
        '''
        The 'path' is built from a string such as "target.title"
        that has been split on the "." to result in ["target", "title"]
        and saved as a queue object

        'obj' is the object currently being explored and expanded

        The 'path' queue is checked for length, because it points to the final
        location of the desired value, if the queue is 1 then we have reached
        the bottom of the search and we return "obj[path]" value
        Otherwise the leftmost item is popped from the list and treated as a
        link to the new object to be expanded, then the new object and the
        shortened queue are fed back into the method

        EXAMPLE:
        path = ["target", "title"]
        obj = {Experiment}
        Length is greather than 1, pop leftmost value
        field = "target"
        path = ["title"]

        get obj[field] and save as new obj, in this case Experiment["target"]
        call get_embedded() with new value for path and obj

        path = ["title"]
        obj = {target}
        path is length 1, we have reached end of search queue
        pop leftmost value
        field = "title"
        return obj[field] which is target["title"]

        There are some special cases checked for, such as if the value
        expended is a list-type setup, such as path = ["replicates", "status"]

        Here path.popleft() gets us "replicates" which is a list
        This list is stored temporarily and then iterated through
        immediately to retrieve the next value (in this case "status")

        This is why it can't retrieve lists the are doubly embedded
            Ex: path = ["replicates", "library", "anyvalue"]
                won't work because both replicates and library are lists

        There is another special check for "files" to iterate through it
        '''
        if len(path) > 1:
            field = path.popleft()  # first element in queue
            if obj.get(field):  # check to see if the element is in the current object
                if field == "files":
                    files_list = []  # empty list for later
                    for f in obj[field]:
                        temp = get_ENCODE(f, self.connection)
                        if temp.get(path[0]):
                            if len(path) == 1:  # if last element in path then get from each item in list
                                files_list.append(temp[path[0]])  # add items to list
                            else:
                                return self.get_embedded(path, temp)
                    if self.args.listfull:
                        return files_list
                    else:
                        return list(set(files_list))  # return unique list of last element items
                else:
                    if type(obj[field]) == int:
                        return obj[field]  # just return integers as is, we can't expand them
                    elif type(obj[field]) == list:
                        if len(path) == 1:  # if last element in path then get from each item in list
                            files_list = []
                            for f in obj[field]:
                                if type(f) == dict:  # if this is like a flowcell or something it should catch here
                                    return f
                                temp = get_ENCODE(f, self.connection)
                                if temp.get(path[0]):
                                    if type(temp[path[0]]) == list:
                                        files_list.append(temp[path[0]][0])
                                    else:
                                        files_list.append(temp[path[0]])
                            if self.args.listfull:
                                return files_list
                            else:
                                return list(set(files_list))  # return unique list of last element items
                        elif self.facet:  # facet is a special case for the search page flattener
                            temp = get_ENCODE(obj[field][0], self.connection)
                            return self.get_embedded(path, temp)
                        else:  # if this is not the last item in the path, but we are in a list
                            return obj[field]  # return the item since we can't dig deeper without getting lost
                    elif type(obj[field]) == dict:
                        return obj[field]  # return dictionary objects, probably things like flowcells anyways
                    else:
                        temp = get_ENCODE(obj[field], self.connection)  # if found get_ENCODE the embedded object
                        return self.get_embedded(path, temp)
            else:  # if not obj.get(field) then we kick back an error
                return ""
        else:
            field = path.popleft()
            if obj.get(field):
                return obj[field]
            else:
                return ""


def patch_set(args, connection):
    import csv
    data = []
    print("Running on", connection.server)
    if args.update:
        print("This is an UPDATE run, data will be patched")
        if args.remove:
            print("On this run data will be REMOVED")
    else:
        print("This is a test run, nothing will be changed")
    if args.accession:
        if args.field and args.data:
            data.append({"accession": args.accession, args.field: args.data})
        else:
            print("Missing field/data! Cannot PATCH object", args.accession)
            sys.exit(1)
    elif args.infile:
        if os.path.isfile(args.infile):
            with open(args.infile, "r") as tsvfile:
                reader = csv.DictReader(tsvfile, delimiter='\t')
                for row in reader:
                    data.append(row)
        else:
            print("{} was not found".format(args.infile))
            sys.exit(1)
    else:
        reader = csv.DictReader(sys.stdin, delimiter='\t')
        for row in reader:
            data.append(row)
    identifiers = ["accession", "uuid", "@id", "alias"]
    for d in data:
        temp_data = d
        accession = ''
        for i in identifiers:
            if d.get(i):
                accession = d[i]
                temp_data.pop(i)
        if not accession:
            print("No identifier found in headers!  Cannot PATCH data")
            sys.exit(1)
        accession = quote(accession)
        full_data = get_ENCODE(accession, connection, frame="edit")
        if args.remove:
            put_dict = full_data
            for key in temp_data.keys():
                k = key.split(":")
                name = k[0]
                if name not in full_data.keys():
                    print("Cannot PATCH '{}' may be a calculated property".format(name))
                    sys.exit(1)
                print("OBJECT:", accession)
                if len(k) > 1:
                    if k[1] in ["list", "array"]:
                        old_list = full_data[name]
                        l = temp_data[key].strip("[]").split(",")
                        l = [x.replace("'", "") for x in l]
                        new_list = []
                        # this should remove items from the list even if they are only a partial match
                        # such as ENCFF761JAF instead of /files/ENCFF761JAF/
                        for x in l:
                            for y in old_list:
                                if x in y:
                                    new_list.append(y)

                        patch_list = list(set(old_list) - set(new_list))
                        put_dict[name] = patch_list
                        print("OLD DATA:", name, old_list)
                        print("NEW DATA:", name, patch_list)
                        if args.update:
                            patch_ENCODE(accession, connection, put_dict)
                else:
                    put_dict.pop(name, None)
                    print("Removing value:", name)
                    if args.update:
                        replace_ENCODE(accession, connection, put_dict)
        else:
            patch_data = {}
            if args.flowcell:
                # if flowcell is picked search for flowcell details
                flow = ["flowcell", "lane", "machine", "barcode"]
                cell = {}
                for f in flow:
                    if temp_data.get(f):
                        cell[f] = temp_data[f]
                        temp_data.pop(f)
                temp_data["flowcell_details:list"] = cell
            for key in temp_data.keys():
                k = key.split(":")
                if len(k) > 1:
                    if k[1] == "int" or k[1] == "integer":
                        patch_data[k[0]] = int(temp_data[key])
                    elif k[1] == "array" or k[1] == "list":
                        if type(temp_data[key]) == dict:
                            l = [temp_data[key]]
                        else:
                            l = temp_data[key].strip("[]").split(", ")
                            l = [x.replace("'", "") for x in l]
                        if args.overwrite:
                            patch_data[k[0]] = l
                        else:
                            append_list = get_ENCODE(accession, connection).get(k[0], [])
                            patch_data[k[0]] = l + append_list
                    elif k[1] == "dict":
                        # this is a dictionary that is being PATCHed
                        temp_data[key] = temp_data[key].replace("'", '"')
                        patch_data[k[0]] = json.loads(temp_data[key])
                    elif k[1] in ["bool", "Boolean", "boolean", "BOOLEAN"]:
                        if temp_data[key] in ["True", "true", "TRUE"]:
                            patch_data[k[0]] = True
                        elif temp_data[key] in ["False", "false", "FALSE"]:
                            patch_input[k[0]] = False
                else:
                    patch_data[k[0]] = temp_data[key]
                old_data = {}
                for key in patch_data.keys():
                    old_data[key] = full_data.get(key)
                print("OBJECT:", accession)
                for key in patch_data.keys():
                    print("OLD DATA:", key, old_data[key])
                    print("NEW DATA:", key, patch_data[key])
                if args.update:
                    patch_ENCODE(accession, connection, patch_data)


def fastq_read(connection, uri=None, filename=None, reads=1):
    '''Read a few fastq records
    '''
    # https://github.com/detrout/encode3-curation/blob/master/validate_encode3_aliases.py#L290
    # originally written by Diane Trout
    import gzip
    from io import BytesIO
    # Reasonable power of 2 greater than 50 + 100 + 5 + 100
    # which is roughly what a single fastq read is.
    if uri:
        BLOCK_SIZE = 512
        url = urljoin(connection.server, quote(uri))
        data = requests.get(url, auth=connection.auth, stream=True)
        block = BytesIO(next(data.iter_content(BLOCK_SIZE * reads)))
        compressed = gzip.GzipFile(None, 'r', fileobj=block)
    elif filename:
        compressed = gzip.GzipFile(filename, 'r')
    else:
        print("No url or filename provided! Cannot access file!")
        return
    for i in range(reads):
        header = compressed.readline().rstrip()
        sequence = compressed.readline().rstrip()
        qual_header = compressed.readline().rstrip()
        quality = compressed.readline().rstrip()
        yield (header, sequence, qual_header, quality)


def md5(path):
    md5sum = hashlib.md5()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            md5sum.update(chunk)
    return md5sum.hexdigest()


def post_file(file_metadata, connection, update=False):
    local_path = file_metadata.get('submitted_file_name')
    if not file_metadata.get('md5sum'):
        file_metadata['md5sum'] = md5(local_path)
    try:
        logging.debug("POST JSON: %s" % (json.dumps(file_metadata)))
    except:
        pass
    if update:
        url = urljoin(connection.server, '/files/')
        r = requests.post(url, auth=connection.auth, headers=connection.headers, data=json.dumps(file_metadata))
        try:
            r.raise_for_status()
        except:
            # if conflicts return the conflict for submit files
            if r.status_code == 409:
                return r
            else:
                logging.warning('POST failed: %s %s' % (r.status_code, r.reason))
                logging.warning(r.text)
                return None
        else:
            return r.json()['@graph'][0]
    else:
        file_obj = copy.copy(file_metadata)
        file_obj.update({'accession': None})
        return file_obj


def upload_file(file_obj, update=False):
    if update:
        if isinstance(file_obj, ENC_Item):
            creds = file_obj.new_creds()
        else:
            creds = file_obj['upload_credentials']
        logging.debug('AWS creds: %s' % (creds))
        env = os.environ.copy()
        env.update({
            'AWS_ACCESS_KEY_ID': creds['access_key'],
            'AWS_SECRET_ACCESS_KEY': creds['secret_key'],
            'AWS_SECURITY_TOKEN': creds['session_token'],
        })
        path = file_obj.get('submitted_file_name')
        try:
            subprocess.check_call(['aws', 's3', 'cp', path, creds['upload_url']], env=env)
        except subprocess.CalledProcessError as e:
            # The aws command returns a non-zero exit code on error.
            logging.error("AWS upload failed with exit code %d" % (e.returncode))
            return e.returncode
        else:
            return 0
    else:
        return None
