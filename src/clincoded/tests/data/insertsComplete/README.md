The \*.json files in this directory represent the 'complete'/non-test data for the initial load into the database. To load the complete data into your test server, replace the corresponding file(s) in src/clincoded/tests/data/inserts. Please note that depending on which file(s) you load in server performance will be adversely affected.

The scripts used to generate the \*.json files are in the scripts subdirectory. Run obtain\_external\_data\_files.py (with python3) to grab the raw data, then whatever create\_\*\_json.py (with python2) to convert the data to the JSON format required by the database.

Ex:
```
python3 obtain_external_data_files.py --source hgnc
python create_gene_json.py
```

```
python3 obtain_external_data_files.py --source orphanet
python create_orphaPhenotype_json.py
```

- **gene.json** - 39,446 entries - data grabbed 2015/07/24
- **orphaPhenotype.json** - 9,193 entries - data grabbed 2015/07/24 (1.1.4 / 4.1.3 ORPHANET [2014-10-03])
