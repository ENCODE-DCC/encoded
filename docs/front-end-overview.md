## Full-Page Rendering

People normally use React to make _part_ of the page dynamic in some way (imagine a live weather widget on an otherwise static page). _encoded_ uses full-page rendering, having React produce everything including the `<html>` tags. The React team at Facebook doesn’t [prefer](https://groups.google.com/forum/#!topic/reactjs/4jI5xe7TXzQ) full-page rendering, but has kept grudging support for it as long as you use server rendering.

## Server Rendering

_encoded_ uses React server rendering, so even before Javascript starts operating on your web browser, React has already rendered the HTML of the page on the server — except for anything that changes because of user input (e.g. dropping down a menu) or that gets loaded into the page after the page loads (e.g. data not built into the displayed ENCODE object itself, but needs display anyway) — and sent the completed HTML to your web browser.

After the page with the server-rendered HTML loads in the web browser, React Javascript running in the web browser treats the HTML on the page as if it had rendered the page itself — as React normally does without server rendering.

## Web Browser Startup Procedure

After the page loads in the web browser, [browser.js](../src/encoded/static/browser.js) comes into play` . This code does _not_ run during server rendering — it runs in the web browser only. It begins by detecting the web browser's abilities using our [BrowserFeat](../src/encoded/static/components/browserfeat.js) module and injecting some CSS classes into the `<html>` tag of the page. React in the browser hasn’t started quite yet at this stage.

Then one of the most important operations for rendering an _encoded_ happens: retrieving the properties of the object being displayed (e.g. Experiment, Biosample, etc.).

The server “renders” the displayed object properties as a JSON string into a `<script>` tag right at the beginning of the `<body>` section of the HTML that gets sent to the web browser. You can see this for any _encoded_ page by looking at the source of the page, or the “Elements” tab of the Chrome debugger, or in the server response of the http request. The `<script>` tag has a `data-prop-name` attribute with the value `context` that lets the `getRenderedProps` function find the JSON within the HTML to convert to a Javascript object that gets passed to the main `encoded` React component, called `<App>`, in [app.js](../src/encoded/static/components/app.js).

The launching of `<App>` looks familiar if you’ve looked at [very beginning of the React documentation](https://facebook.github.io/react/docs/hello-world.html), though instead of rendering an HTML tag, it renders our `<App>` component, and instead of rendering `<App>` into a `<div>`, it renders `<App>` into the DOM represented by `document`. At that moment, all the React code you see in `<App>` and all the code `<App>` calls follows the React concepts you find in their documentation.

Of course, the [browser.js](../src/encoded/static/browser.js) function only runs in the web browser, yet rendering the web page has to happen on the server too. And it does in the `render` function of[react-middleware.js](../src/encoded/static/libs/react-middleware.js) that _only_ runs on the server using the [documented server-rendering mechanism](https://facebook.github.io/react/docs/react-dom-server.html).

## React _props_

React at its fundamentals passes one immutable object (and yes, React enforces its immutability, so never mutate it) to each component you make: _props_. But though React owns this object, you as a React programmer populate it — React supplies the train; you supply the passengers. When you place attributes where a component gets rendered, those attributes go into the props object with property names matching the name of the attribute and values matching those you assign to each attribute. Let’s look at an example of rendering the `<LabCharts>` component you’ll find in [award.js](../src/encoded/static/components/award.js):

    <LabChart
        award={award}
        labs={experimentsConfig.labs}
        linkUri={experimentsConfig.linkUri}
        ident={experimentsConfig.ident}
    />

The `<LabChart>` component gets the attributes `award` (object), `labs` (an array of objects), `linkUri` (a string), and `ident` (another string).

The implementation of `<LabCharts>` expects `this.props` to contain:

    {
        award: { object },
        labs: [{ object }, { object }, ...],
        linkUri: ' string ',
        ident: ' string '
    }

## The _encoded_ “context” prop

All _encoded_ components that render a page (`<Biosample>` in [biosample.js](../src/encoded/static/components/biosample.js) as an example) receive an object prop called `context`. It contains the _encoded_ object being rendered — the same object you would see if you viewed an individual _encoded_ object in the browser with `format=json` appended to its query string. You can witness this common sight at the beginning of this kind of component’s `render` method:

    const { context } = this.props

Then you see the `context` local variable used throughout the `render` method and other methods in the object, with properties referenced right from that object’s schema. For example, every biosample object must have a `biosample_type` property, so you’ll find in [biosample.js](../src/encoded/static/components/biosample.js) occurrences of `context.biosample_type`.

## Search


## Multiple Adjacent React Components

A particularly troublesome aspect of React that every new React developer runs into: multiple adjacent components. While `encoded` shares this with _all_ React project, people run into difficulties enough to make this worth discussing.

_You cannot have a React component that returns multiple components._

Imagine you’ve defined a React component called `<Hello>` and another called `<There>`. Your main component renders both of those components like this:

```
function hello() {
  return (
    <div>
      <Hello />
      <There />
    </div>
  );
}
```

You might think, “Why have the divs there?” and remove them, but React doesn’t allow this.

```
function hello() {
  return (
    <Hello />
    <There />
  );
}

Error: Adjacent JSX elements must be wrapped in an enclosing tag.
```

All React components get transpiled to a function call to `React.createElement` which returns a React component object. Functions can return zero React component objects (by returning null) or one of them —— no more. You can see this more clearly by using pure Javascript instead of JSX. The correct function above without JSX looks like:

```
function hello() {
  return React.createElement(
    "div",
    null,
    React.createElement(Hello, null),
    React.createElement(There, null)
  );
}
```

Transpilers like [babel](https://babeljs.io) convert JSX to this form, so they convert `<div>` to a function call to `React.createElement` with the component or component name as the first parameter — “div” in this case, then a null, then any number of function calls to nested components’ `React.createElement` calls.

If you tried the form without the enclosing `<div>`, it would have to look like:

```
function hello() {
  return [
    React.createElement(Hello, null),
    React.createElement(There, null)
  ];
}
```

React component functions cannot return an array however, so you always need to return one component:

```
return <Greetings />;
```

…or multiple wrapped in an enclosing tag:

```
return (
    <div>
        <Hello />
        <There />
    </div>
);
```

This situation might change sooner rather than later with [React Fibre](https://github.com/acdlite/react-fiber-architecture).

## Keys

## View Registry