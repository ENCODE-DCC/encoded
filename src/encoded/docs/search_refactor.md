Search Refactor

Helpers:

The first stage in this refactor was, moving the helper functions from search.py to a separate module called helper.py. This module lives in the snovault repository at src/snovault/helpers/helper.py.

All these helper functions are used inside the main search class and other classes for pre, and post processing of the query and result objects needed by the calls made to ElasticSearch.

Class Hierarchy:

The view_configs present inside search.py have been moved out in to their own classes in separate class files. The path where these modules live are:

Snovault:

src/snovault/viewconfigs/base_view.py => Base class for all the search related view_configs
src/snovault/viewconfigs/searchview.py => Search view_config that inherits from base_view and is the parent class for report view and news view
src/snovault/viewconfigs/report.py => Report view_config that inherits from searchview.
src/snovault/viewconfigs/views.py => Snovault’s views.py module that holds the routes for search and report that were originally present in snovault’s search.py module.

Encoded:

src/encoded/viewconfigs/news.py => News view that inherits from snovault’s searchview.py
src/encoded/viewconfigs/matrix.py => Matrix view that inherits from base_view and is the parents class for summary and audit view
src/encoded/viewconfigs/auditview.py => Audit view that inherits from matrix.py
src/encoded/viewconfigs/summary.py => Summary view that inherits from matrix.py
src/encoded/viewconfigs/views.py => Encoded’s views.py module that holds the routes for search, report, news, matrix, audit and summary that were originally present in encoded’s search.py module. Here, the search and report classes are imported from snovault as they’re defined in snovault


Extending the architecture to new routes:

If you want to write a new route that requires search.py, subclass it from search.py in encoded and write a class for the new route, re-use the methods that are needed for pre and post processing the query and results objects, or override these methods inside the new class when the implementation changes. Add the route to src/encoded/viewconfigs/views.py and create an instance of the class and call the prepreocess_view() method on the created instance to return the results object.
