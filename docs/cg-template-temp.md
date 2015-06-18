# ClinGen Temporary Templating System

Until we have the database, schemas, and test data working, I put in a temporary, hacked-in templating system so we can see pages running. Hopefully, the templated Javascript files can be used pretty much as-is once the back-end system comes up.

## UI Templates

Like the ENCODE system, the Javascript front-end files go into the directory:

```
clincoded/src/clincoded/static/components
```

For now, I have the ```curator.js``` file working with this temporary templating system, so that’s a good place to look initially. This file follows the ENCODE/ReactJS system that includes a main entry point (the ```Curator``` function) that’s exported from this file, and any private functions and ReactJS components it needs.

Notice below the ```Curator``` function:

```
globals.cg_template.register(Curator, 'curator');
```

This registers the ```Curator``` function as the display for any pages with the name, ```curator``` (the case is important here — ```Curator``` comes from the function we want called, and ```curator``` is the name of the test data from the JSON; more on that later).

While it uses a similar principle to the ENCODE view registry system, it doesn’t work like the rest of the system that uses the JSON-LD ```@type``` chooser. For your uses though, it acts like the rest of the system.


## Pages

The ```curator.js``` code runs when you go to the **/curator/** path. This path comes from:

```
clincoded/src/clincoded/tests/data/inserts/page.json
```

ENCODED uses this page.json schema to define content pages like in a CMS (as opposed to data pages that display experiments, antibodies, etc). I’m corrupting its use here temporarily. Notice at the bottom of the JSON:

```
    {
        "name": "curator",
        "title": "Curator",
        "status": "released",
        "uuid": "61edd6b2-bfdb-4db1-b950-8845ac37f65c"
    }
```

The ```name``` field defines both the path and the registry name, so you pass it as the second parameter to the ```register``` function above, and you go to that path in the browser to display the page. The rest is just needed so it gets loaded during indexing.


## Adding New Templates/Pages

To add new kinds of pages, define it as a ReactJS component in the ```components``` directory, then add it to the ```index.js``` file so that the registery function gets called. Then add to the ```page.json``` test data so that it exists at a path.