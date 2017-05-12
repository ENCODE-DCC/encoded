## Full-Page Rendering

People normally use React to make _part_ of the page dynamic in some way (imagine a live weather widget on an otherwise static page). _encoded_ uses full-page rendering, having React produce everything including the `<html>` tags. The React team at Facebook doesn’t [prefer](https://groups.google.com/forum/#!topic/reactjs/4jI5xe7TXzQ) full-page rendering, but has kept grudging support for it as long as you use server rendering.

## Server Rendering

_encoded_ uses React server rendering, so even before Javascript starts operating on your web browser, React has already rendered the HTML of the page on the server — except for anything that changes because of user input (e.g. dropping down a menu) or that gets loaded into the page after the page loads (e.g. data not built into the displayed ENCODE object itself, but needs display anyway) — and sent the completed HTML to your web browser.

After the page with the server-rendered HTML loads in the web browser, React Javascript running in the web browser treats the HTML on the page as if it had rendered the page itself — as React normally does without server rendering.

## Web Browser Startup Procedure

After the page loads in the web browser, [browser.js](../src/encoded/static/browser.js) comes into play. This code does _not_ run during server rendering — it runs in the web browser only. It begins by detecting the web browser's abilities using our [BrowserFeat](../src/encoded/static/components/browserfeat.js) module and injecting some CSS classes into the `<html>` tag of the page. React in the browser hasn’t started quite yet at this stage.

Then one of the most important operations for rendering an _encoded_ page happens: retrieving the properties of the object being displayed (e.g. Experiment, Biosample, etc.).

The server “renders” the displayed object properties as a JSON string into a `<script>` tag right at the beginning of the `<body>` section of the HTML that gets sent to the web browser. You can see this for any _encoded_ page by looking at the source of the page, or the “Elements” tab of the Chrome debugger, or in the server response of the http request. The `<script>` tag has a `data-prop-name` attribute with the value `context` that lets the `getRenderedProps` function find the JSON within the HTML to convert to a Javascript object that gets passed to the main `encoded` React component, called `<App>`, in [app.js](../src/encoded/static/components/app.js).

The launching of `<App>` looks familiar if you’ve looked at the [beginning of the React documentation](https://facebook.github.io/react/docs/hello-world.html), though instead of rendering an HTML tag, it renders our `<App>` component, and instead of rendering `<App>` into a `<div>`, it renders `<App>` into the DOM represented by `document`. At that moment, all the React code you see in `<App>` and all the code `<App>` calls follows the React concepts you find in their documentation.

Of course, the [browser.js](../src/encoded/static/browser.js) function only runs in the web browser, yet rendering the web page has to happen on the server too. And it does in the `render` function of [react-middleware.js](../src/encoded/static/libs/react-middleware.js) that _only_ runs on the server using the [documented server-rendering mechanism](https://facebook.github.io/react/docs/react-dom-server.html).

## React _props_

React at its fundamentals passes one immutable object (and yes, React enforces its immutability, so never mutate it) to each component you make: _props_. But though React owns this object, you as a React programmer populate it — React supplies the train; you supply the passengers. When you place attributes where a component gets rendered, those attributes go into the props object with property names matching the name of the attribute and values matching those you assign to each attribute. Let’s look at an example of rendering the `<LabCharts>` component you’ll find in [award.js](../src/encoded/static/components/award.js):

    <LabChart
        award={award}
        labs={experimentsConfig.labs}
        linkUri={experimentsConfig.linkUri}
        ident={experimentsConfig.ident}
    />

The `<LabChart>` component gets the attributes `award` (object), `labs` (array of objects), `linkUri` (string), and `ident` (string).

The implementation of `<LabCharts>` expects `this.props` to contain:

    {
        award: { object },
        labs: [{ object }, { object }, ...],
        linkUri: ' string ',
        ident: ' string '
    }

## The _encoded_ “context” prop

All _encoded_ components that render a page (`<Biosample>` in [biosample.js](../src/encoded/static/components/biosample.js) as an example) receive an object prop called `context`. It contains the _encoded_ object the component renders — the same object you see if you view it with `format=json` appended to its query string, or retrieve it with a GET request. This kind of component’s `render` method frequently starts with:

    const { context } = this.props;

Then you see the `context` local variable used throughout the `render` method, with properties referenced right from that object’s schema. For example, every biosample object must have a `biosample_type` property, so you’ll find in [biosample.js](../src/encoded/static/components/biosample.js) occurrences of `context.biosample_type`.

## The React Context

An unfortunate name collision — React itself has a [context object](https://facebook.github.io/react/docs/context.html). You can think of React contexts as props sharable by a component and any of its children without passing them explicitly.

The overall React way has components sending props to their child components, which send props to _their_ child components and so on. Data explicitly follows the hierarchy of components. Each component can pass through any or all props it receives to its children, and can generate new props for its children.

Now imagine you had a component that relies on data kept in its grandparent, but the parent has no use for this data. Without React context, the grandparent would pass this data as props to the parent, which would then pass these props it didn’t use to this component — not so bad perhaps at this scale. But imagine a taller hierarchy, where a distant leaf component needs data from its great-great-great-great-grandparent. Now every generation of components between them has to pass those props through even though they had no interest in these props themselves.

React _context_ objects short circuit props. You define a _context_ object in one component, and then any children and grand children of this component — no matter the number of generations between — can “subscribe” to the data in the context object without any intervening generations needing to know about this data.

The _encoded_ `<App>` component — being the direct or indirect parent of all _encoded_ components — has a context object sharable by any component in _encoded_.

    App.childContextTypes = {
        listActionsFor: PropTypes.func,
        currentResource: PropTypes.func,
        location_href: PropTypes.string,
        fetch: PropTypes.func,
        navigate: PropTypes.func,
        portal: PropTypes.object,
        projectColors: PropTypes.object,
        biosampleTypeColors: PropTypes.object,
        adviseUnsavedChanges: PropTypes.func,
        session: PropTypes.object,
        session_properties: PropTypes.object,
        localInstance: PropTypes.bool,
    };

As an example, the `<FileComponent>` component in [file.js](../src/encoded/static/components/file.js) subscribes to `<App>`’s `session` and `session_properties` context properties with:

    FileComponent.contextTypes = {
        session: PropTypes.object, // Login information
        session_properties: PropTypes.object,
    };

`<FileComponent>` can then reference these two properties with `this.context.session` and `this.context.session_properties`. Don’t confuse this with referencing the _encoded_ context with `this.props.context` — they have nothing to do with each other.

## View Registry

Each type of _encoded_ object generally gets rendered by its own React component. Experiment objects, for example, get rendered by the `<Experiment>` component in [experiment.js](../src/encoded/static/components/experiment.js). Yet you’ll find no giant `switch` statement farming out the different object types to different React components. Instead, this gets handled in two lines in  the `<App>` component in [app.js](../src/encoded/static/components/app.js):

    const ContentView = globals.content_views.lookup(context, currentAction);
    content = <ContentView context={context} />;

`globals.content_views.lookup` takes the _encoded_ `context` object (not the React context) and returns the React component in charge of rendering it. Later in this function, the `content` variable gets inserted into the page’s HTML in the usual React way.

This lookup function handles mapping _encoded_ objects to React components that render them through the _encoded_ View Registry — an inscrutable module lacking any documentation in [registry.js](../src/encoded/static/libs/registry.js).

_encoded_ components that get called directly from `<App>` register themselves with the View Registry on page load for both server and web browser rendering. Open any major object’s React file to see this. For example, GeneticModification objects get rendered by the `<GeneticModification>` component in [genetic_modification.js](../src/encoded/static/components/genetic_modification.js). Below the `<GeneticModificationComponent>` component, you’ll find (after getting wrapped in the audit decorator to make the `<GeneticModification>` component) the line:

    globals.content_views.register(GeneticModification, 'GeneticModification');

This registers `<GeneticModification>` as the component to call when a GeneticModification object comes through `<App>`. You find similar lines throughout _encoded_ Javascript.

### A little tangent — when components register themselves

Notice this code doesn’t _declare_ anything the way components themselves get declared but not executed until `<App>` calls them — this code gets executed in the “global” space on page load before `<App>` ever gets run (“global” in sneer quotes because with the module system and build tools like Webpack, the global space isn’t really global, but no harm in thinking of it that way). How does that happen?

If you look in [browser.js](../src/encoded/static/browser.js) you find near the top:

    import App from './components';

…and in [server.js](../src/encoded/static/server.js) you find near the middle:

    var app = require('./libs/react-middleware').build(require('./components'));

These import from './components' — a directory; not a file. When the Javascript module system imports or requires (same thing; different version of Javascript) a directory, the file called “index.js” in that directory gets loaded. Our [index.js](../src/encoded/static/components/index.js) imports many files in the “components” directory, then exports the `<App>` component so that [browser.js](../src/encoded/static/browser.js) and [server.js](../src/encoded/static/server.js) can call it. This causes that list of files to all get executed, which causes their View Registry `register` functions to get called at that stage. That means if you make a new object-rendering module that registers itself with the View Registry, that file has to be added to this list. Files that don’t register their components in the View Registry don’t need inclusion in this list.

### Back to the View Registry

Take another look at the registration for the `<GeneticModification>` component:

    globals.content_views.register(GeneticModification, 'GeneticModification');

The first parameter passes the component that gets called when an object needs rendering. The second passes an `@type` string. Objects that have a matching string in their `@type` array get passed to the component in the first parameter, with the object in `this.props`. You can think of the second parameter as the key of the giant `switch` statement.

_encoded_ has several independent view registries. `content_view` handles rendering entire objects as pages of their own. [globals.js](../src/encoded/static/components/globals.js) shows where these different registries get created near the top. As an example, `graph_detail` handles the types of modal dialogs that appear when different kinds of file graph elements get clicked.

## GET Requests

Several pages of the site display more than their objects contain, and they have to get the information through GET requests performed after the page has rendered in the browser. _encoded_ has two mechanisms to do these GET requests, each one appropriate depending on how much logic happens around these GET requests.

### FetchedData

The simplest mechanism involves the `<FetchedData>` React component in [fetched.js](../src/encoded/static/components/fetched.js). You can see an example of its normal pattern of usage in [award.js](../src/encoded/static/components/award.js)

    <FetchedData ignoreErrors>
        <Param name="experiments" url={`/search/?type=Experiment&award.name=${award.name}`} />
        <Param name="annotations" url={`/search/?type=Annotation&award.name=${award.name}`} />
        <ChartRenderer award={award} />
    </FetchedData>

The odd thing about the `<FetchedData>` and `<Param>` components — they never render anything of their own, and in fact `<Param>` never renders anything at all — they _do_ stuff.

`<FetchedData>` has a complex implementation beyond the scope of this document, but in the end it renders its children into a `<div>`. But it also reacts to the results of GET requests, yet it makes no GET request itself.

That role goes to `<Param>` a component required as a direct child of `<FetchedData>`. `<Param>` calls an npm library to perform the GET request. Once it receives the requested data from the server, it calls methods in `<FetchedData>` with this data to render it.

The required attributes to `<Param>` include `url` that holds the URL for the GET request, and `name` that names the property that receives the the results of the GET requests (you usually find only one `<Param>` inside a `<FetchedData>`, but this example happens to do two GET requests). More on that next.

The other child component within `<FetchedData>` renders the data returned from the GET requests. Look at the implementation of `<ChartRenderer>` and notice it takes three items from `this.props`: `award` which we passed directly as the `award` attribute, but also `experiments` and `annotations`. Notice these match the names of the `name` properties in the `<Param>` components — not a coincidence. Pass the name of the React prop to receive the GET request results as the `name` attribute in `<Param>`.

Also be aware that just because the GET request hasn’t gone out to the server yet doesn’t mean any of these components block. The first time through with no GET request data, `<ChartRenderer>` gets called, but with nothing in `experiments` and `annotations`. Once the data gets received, `<ChartRenderer>` gets called _again_ — this time _with_ the data in `experiments` and `annotations`. The data-rendering component within `<FetchedData>` has to handle the case where no data has arrived yet.

### Request Data

The other method has best use when the logic of GET requests gets more involved than “get data, render data.”  The `<DerivedFiles>` component provides a good example, because it follows this algorithm:

    Get minimal data on every file matching search criteria
    If that search returned more files than we allow on a table:
        Retrieve entire file objects only for the files that fit on the first page
        Once that data returns, render it
    Else
        Render all the files

In addition, when the user clicks a paging tool, it performs another GET request for the next page of files, but only if this page of files isn’t already cached. Clearly the `FetchedData` “get data, render data” method doesn’t work for this kind of situation.

The [objectutils.js](../src/encoded/static/components/objectutils.js) file provides three functions to implement this.

* **requestSearch**: Passed a search query string, returns search results
* **requestFiles**: Passed an array of file `@ids`, returns file objects
* **requestObjects**: Passed an array of object `@ids` and a search URI, return objects

Each of these returns a Javascript promise, so the GET request happens asynchronously. The typical way to call `requestObject` would appear like (`requestFiles` and `requestObjects` are just wrapper functions for `requestObject`):

    requestObjects(objectIdArray, searchUri).then((results) => {
        // Do something with the results
    })

The part within the callback would execute once the GET request had returned, with the results in the `results` parameter. Setting a React state variable for the component would typically go here, or something more complicated that could lead to another promise.

#### Historical “Other” reason

You’ll see some uses of these request functions that _do_ fit into a “get data, render data” model. Earlier versions of _encoded_ had a strict limit on the length of a URL. In cases where our search URI could have a long length, you had to use these request functions because if a URI’s length reached a certain maximum, these functions would break the request into _multiple_ GET requests so that each URI used fit into the maximum. Once all the GET requests returned, these functions put the results together and returned them to the caller. Now that _encoded_ accepts arbitrarily long URIs, these cases could be replaced with `<FetchedData>`.
