===============
Advanced Search
===============

Introduction
------------

The initial implementation of search for encoded could only search
for either string matches or checking to see if particular object
attributes match.

See: src/encoded/tests/features/search.feature for several examples

However BoxIII shows one query illustrating the new advanced query type.

Implementation
--------------

Laurence added a hook to pass lucene queries to elastic search through
via the searchTerm query. Either by constructing urls, or entering the
query into the search box.

The function that parses the advanced query is called
prepare_search_term() and is found in src/encoded/helper.py

It uses a parser written in a dependency called "lucenequery" 
which is available at: https://github.com/lrowe/lucenequery

Usage
-----

The advanced query is triggered by starting a query with

.. code::
   
    @type:<encodedobject type>

and then using something very close to `lucene queries`_ 

Examples
--------

You can query by constructing a url like
https://www.encodeproject.org/search/?searchTerm=%40type%3AItem+aliases%3Abarbara-wold%2A

However you can also enter the the query into the search box without url encoding
which is vastly easier to read and will be used for the examples.

To find all the experiments created in a particular date window you can do the
following

.. code::
   
  @type:Experiment date_created:[2016-01-01 TO 2016-01-31]

  
One could also try other classes like Biosample, or even Item if one
wanted to find all the objects created in a particular window

Lucene also supports substring matches, so another query that
would be difficult using the original syntax is to find all the
objects with a particular alias prefix.

It is also important to note that for colons ":" that appear in
the string being searched, will need to be escaped. "\:"

.. code::
   
   @type:Item aliases:barbara-wold\:*

One can also do logical operators. This query finds 4 biosamples with aliases and
obtained in a specfic date range

.. code::
    
   @type:Item aliases:barbara-wold\:* AND date_obtained:[2014-05-01 TO 2014-12-01]

This query removes two of the hits from the previous alias date_obtained query
by including a NOT query on the description. (Which appears to be the default
field searched)

.. code::

   @type:Item aliases:barbara-wold\:* AND date_obtained:[2014-05-01 TO 2014-12-01] NOT "adrenal gland" 

.. _lucene queries: https://lucene.apache.org/core/2_9_4/queryparsersyntax.html
