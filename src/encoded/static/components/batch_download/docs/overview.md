# Batch Download Module Overview

This module lets you add batch download functionality in just a few lines of code, including a modal dialog box with customizable instructions for the user, and a download button that includes a dropdown menu for various download options that you can (through a bit more effort) customize for individual situations. Download options typically include downloading processed files, raw files, etc.

To include a batch download button at any location on your page, you must first create a controller object included in this module, providing it the data it needs to configure the final download URLs (e.g. facet selections, dataset). You then pass this controller object to the provided UI element that renders the download button, manages the download options dropdown menu, and initiates the batch download on user request.

# Controller

You need one type of controller for each different batch download scenario, where a scenario includes the parts of the batch-download query string required for a specific type of download, as well as the data required to populate the query string. Two examples of scenario follow.

## Cart Scenario

When downloading files from a cart:

* The query string requires a dataset type, an assembly, and the path to a specific cart.
* When allocated, the controller therefore needs the current user-selected dataset type and assembly, as well as a path to the current cart.
* In addition, the currently selected facets on the cart page — as a QueryString object produced by the `query_string.js` library included in the encoded code base — also contributes to the query string.

You would allocate a cart batch download controller like this:

```javascript
const controller = new CartBatchDownloadController(cartPath, datasetType, assemblies, query);
```

## Search Scenario

When downloading files from a search-results page:

* The query string requires a dataset type.
* When allocated, the controller therefore needs the dataset type from the search URL.
* In addition, the currently selected facets on the search-results page — as a QueryString object produced by the `query_string.js` library included in the encoded code base — also contributes to the query string.

You would allocate a search-results page batch download controller like this:

```javascript
const controller = new SearchBatchDownloadController(datasetType, query);
```

# Download Button

The batch download module provides a single UI component — `BatchDownloadActuator` — that renders the Download button. This component also:

* manages the modal dialog box that appears when the user clicks the download button.
* manages user selections in the download-options dropdown menu.
* initiates the batch download when the user requests it.
* closes the batch download modal when the user requests it.

To render the Download button with no customizations:

```javascript
<BatchDownloadActuator controller={controller} />
```

Insert this anywhere in your JSX you wish the Download button to appear. You do not need to provide any code to handle the modal dialog box nor the batch download initiation — `BatchDownloadActuator` handles all of this internally.

When the user changes something that affects the batch download, changing the facet selections for example, allocate a new controller with the new selections and pass it to `BatchDownloadActuator`. Some generic code for this process using search-page batch download as an example (assume a `convertFacetToQuery` function exists that creates a QueryString object with the current set of facet selections):

```javascript
const SectionIncludingDownloadButton = ({ dataset, facetSelections }) => {
    const query = convertFacetToQuery(facetSelections);
    const controller = new SearchBatchDownloadController(dataset['@type'][0], query);
    return (
        <div className="download-section">
            <BatchDownloadActuator controller={controller} />
        </div>
    );
};
```
# Customizing the Download Button

The default download actuator button appears with a “Download” label and using the "btn btn-info btn-sm" CSS classes.

## Container CSS

`BatchDownloadActuator` has a `containerCss` property that accepts CSS class names that get added to a `<div>` that surrounds the default or custom actuator. You can then declare CSS classes that modify the style of the default actuator button.

## Custom Actuator

If the `containerCss` property doesn’t provide enough customizability, you can provide your own actuator by passing JSX to the `actuator` property of `BatchDownloadActuator`. In this example, the user clicks an SVG icon to initiate the download:

```javascript
<BatchDownloadActuator
    controller={batchDownloadController}
    actuator={
        <button className="download-icon-button" type="button">
            {svgIcon('download')}
        </button>
    }
/>
```

Instead of rendering the default button, `BatchDownloadActuator` renders this download icon instead.

Notice the lack of a click handler on the button. `BatchDownloadActuator` provides the click handler — do not include your own. However, if you have a React component as an actuator, `BatchDownloadActuator` attaches the click handler to your component; not the button within. You must therefore pass through the provided click handler to your button element, or whatever element you have that reacts to mouse clicks:

```javascript
const CustomBatchDownloadButton = ({ title, disabled, onClick }) => (
    <div className="custom-batch-download-button">
        <button
            type="button"
            className="btn btn-info btn-lg"
            disabled={disabled}
            onClick={onClick} {/* Attach the provided click handler here */}
        >
            {title}
        </button>
    </div>
);

<BatchDownloadActuator
    controller={controller}
    actuator={
        <CartBatchDownloadButton title={actuatorTitle} disabled={disabled} />
    }
/>
```

Any properties you provide to your actuator component get passed through, but `BatchDownloadActuator` adds the `onClick` property to your component’s properties. Attach that to your component’s button.

# Customizing the Modal

The batch download modal dialog box normally contains descriptive text and instructions for downloading the metadata.tsv file. You can replace this text, or keep it but add to it. To replace this text, pass your own JSX to the `modalContent` parameter.

```javascript
const CustomBatchDownloadModalContent = () => (
    <div className="custom-batch-download-modal-content">
        Custom text goes here. Make this as complicated or simple as you want.
    </div>
);

<BatchDownloadActuator
    controller={controller}
    modalContent={
        <CustomBatchDownloadModalContent />
    }
/>
```

To display the default contents and add your custom content above or below that, import the `DefaultBatchDownloadContent` React component and include it in your custom component:

```javascript
import { DefaultBatchDownloadContent } from './batch_download';

const CustomBatchDownloadModalContent = () => (
    <div className="custom-batch-download-modal-content">
        <div className="above">Custom content that appears above the default content.</div>
        <DefaultBatchDownloadContent />
        <div className="below">Custom content that appears below the default content.</div>
    </div>
);

<BatchDownloadActuator
    controller={controller}
    modalContent={
        <CustomBatchDownloadModalContent />
    }
/>
```

You can also add more complicated elements to the modal, including controls. In this example, two checkboxes appear below the default content that — through the fictional `CustomBatchDownloadController` — affect the query string. As mentioned before, notice that when the user changes a checkbox, the entire code runs again, allocating a new batch download controller and abandoning the one allocated the last time the code ran.

```javascript
const ModalContentWithCheckboxes = ({ isOption1Checked, isOption2Checked, optionChangeHandler }) => (
    <>
        <DefaultBatchDownloadContent />
        <div className="cart-batch-download-content">
            <div>
                <label>
                    <input
                        name="option-1"
                        type="checkbox"
                        checked={isOption1Checked}
                        onChange={optionChangeHandler}
                    />
                    Option 1
                </label>
            </div>
            <div>
                <label>
                    <input
                        name="option-2"
                        type="checkbox"
                        checked={isOption2Checked}
                        onChange={optionChangeHandler}
                    />
                    Option 2
                </label>
            </div>
        </div>
    </>
);

const [isOption1Checked, setIsOption1Checked] = React.useState(false);
const [isOption2Checked, setIsOption2Checked] = React.useState(false);

// Called when the user clicks a checkbox in the custom modal content.
const handleOptionChange = (event) => {
    if (event.target.name === 'option-1') {
        setIsOption1Checked((prev) => !prev);
    } else if (event.target.name === 'option-2') {
        setIsOption2Checked((prev) => !prev);
    }
};

// Allocate a new controller using the checkboxes in the modal.
const controller = new CustomBatchDownloadController(isOption1Checked, isOption2Checked);

<BatchDownloadActuator
    controller={controller}
    modalContent={
        <ModalContentWithCheckboxes
            isOption1Checked={isOption1Checked}
            isOption2Checked={isOption2Checked}
            optionChangeHandler={handleOptionChange}
        />
    }
/>
```

# Creating a Controller

Each different batch download scenario requires a different controller, implemented as a Javascript class that extends an abstract base controller class. You pass this controller to `BatchDownloadActuator` which accepts any batch download controller — this single actuator’s behavior gets modified by the controller you pass it; you do not need different versions of `BatchDownloadActuator` to implement the different batch download scenarios. 

These define a batch download scenario:

* The data needed to create the `/batch_download/` query strings for all download options
* The form of the `/batch_download/` query string
* The available batch download options in the dropdown menu

## Extending the Abstract Base Class

The batch download module provides the `BatchDownloadController` abstract base class that provides generic functionality. Extend this base class for each batch download scenario.

When you allocate a controller, the URLs for the different download options gets generated at that point. You never update a controller once you have allocated one. `BatchDownloadActuator` then uses the data within to generate the batch download options and the corresponding `/batch_download/` URLs for each option.

## Controller Parameters

The base controller accepts a dataset and QueryString object. Controllers that take those same two parameters in that order, even if they need additional parameters, don’t need their own constructors. But controllers that don’t use the dataset and QueryString in that order need a constructor to reorder the parameters for the base controller constructor. As an example, the `SearchBatchDownloadController`  controller takes a dataset _type_ as the first parameter in addition to a QueryString object in the second, so its constructor looks like:

```javascript
constructor(datasetType, query) {
    super(null, query, datasetType);
}
```

Its sole job is to reorder the parameters for the `BatchDownloadController` constructor, so that the additional `datasetType` parameter goes in the third spot, and the `dataset` parameter gets null as it goes unused in this controller.

The base `BatchDownloadController` class doesn’t know what to do with parameters beyond the QueryString one, so controllers must provide a `preBuildDownloadOptions` method to process the additional parameters, normally assigning them to an object property. The `BatchDownloadController` constructor calls that method before building the download options menu, passing it the base dataset object and QueryString parameters (which controllers can ignore if they don’t need them) followed by the additional parameters passed to `super()`, e.g.:

```javascript
constructor(datasetType, query) {
    super(null, query, datasetType);
}

// `dataset` not used in this controller. `query` used but already set by base constructor.
preBuildDownloadOptions(dataset, query, datasetType) {
    this._datasetType = datasetType;
}
```

## Building the Query Strings

The base class’s constructor initiates the building of download options as its final act, and that begins by building the query strings for each download option. The base class builds these query strings, which controllers can use in addition to adding other options, or replace completely.

* Processed files
```
type={dataset @type}&@id={dataset @id}&{selected facet queries}&files.assembly=*
```

* Raw files
```
type={dataset type}&@id={dataset path}&option=raw
```

* All files
```
type={dataset type}&@id={dataset path}
```

If these options and query strings work for your controller, you can keep them and add to them with the `addQueryStrings` method. The following example keeps the base class’s query strings and adds one more:

```javascript
formatDefaultFileQuery() {
    // Use the base class's `buildBasicQuery` method to use the given QueryString object containing
    // the selected facets.
    const query = this.buildBasicQuery();
    query.addKeyValue(`${this._fileQueryKey}.analyses.@id`, this._dataset.default_analysis);
    query.addKeyValue(`${this._fileQueryKey}.preferred_default`, 'true');

    // Format the query into its final form and save it.
    this._defaultFileQueryString = query.format();
}

addQueryStrings() {
    this.formatDefaultFileQuery();
}
```

If the base class’s options don’t apply to your controller, override the base class’s `buildQueryStrings` method and build the ones you need, saving the resulting formatted query strings in the controller object as data members, one query string per download option.

## Building the Download Options

After building all applicable query strings and saving them as object data members, build the download options. Recall that the base class provides “Processed,” “Raw,” and “All” options and the corresponding query strings. If these options apply to your controller, you can prepend and append other options to them using the `buildPreDownloadOptions` and `buildPostDownloadOptions` methods which both need to create and return an array of download options.

The download options reside in an array kept in a controller data member, and has this form:

```javascript
{
    // Unique ID among download options.
    id: 'processed-files',
    // Label that appears in the button; custom actuator might ignore this.
    label: 'Download processed files',
    // Title within dropdown.
    title: 'Processed files',
    // Description below title within dropdown.
    description: 'Downloads processed files matching the selected file filters.',
    // Query string corresponding to this download option.
    query: '',
},
```

If the base class’s download options don’t work for your controller, override the `buildDownloadOptions` method and build them from scratch.
