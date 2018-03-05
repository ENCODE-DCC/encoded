import React from 'react';
import PropTypes from 'prop-types';
import marked from 'marked';
import { Panel, PanelHeading, PanelBody, TabPanel, TabPanelPane } from '../libs/bootstrap/panel';
import { collapseIcon } from '../libs/svg-icons';
import { Param, FetchedData } from './fetched';
import * as globals from './globals';
import { Breadcrumbs } from './navigation';


// Used to map schema property names to more visually pleasing versions.
const titleMap = {
    required: 'Required',
    comment: 'Comment',
    approvalRequired: 'Approval required',
    identifyingProperties: 'Identifying properties',
    dependencies: 'Dependencies',
    properties: 'Properties',
};


// List of schema terms we don't display.
const excludedTerms = [
    'type',
    'additionalProperties',
    'mixinProperties',
    'title',
    'description',
    'id',
    '$schema',
    'facets',
    'columns',
    'boost_values',
    'changelog',
    '@type',
    'output_type_output_category',
    'file_format_file_extension',
    'sort_by',
    'anyOf',
];


// Functions to display simple schema term types, keyed by `typeof` result.
const simpleTypeDisplay = {
    string: item => <span>{item}</span>,
    boolean: item => <span>{item ? 'True' : 'False'}</span>,
    number: item => <span >{item}</span>,
};


// Keys in a schema for objects that should be searched for links to other schemas.
const linkedTerms = ['properties'];


/**
 * Create a brace read-only editor instance that goes into the HTML element with the given ID and
 * displaying the given schema term.
 *
 * @param {*} elementId - HTML element ID to draw the editor into.
 * @param {*} term - Schema term object to display.
 */
function createJsonDisplay(elementId, term) {
    return new Promise((resolve) => {
        require.ensure([
            'brace',
            'brace/mode/json',
            'brace/theme/katzenmilch',
        ], (require) => {
            const ace = require('brace');
            require('brace/mode/json');
            require('brace/theme/katzenmilch');
            const value = JSON.stringify(term, null, 4);
            const editor = ace.edit(elementId);
            const session = editor.getSession();
            session.setMode('ace/mode/json');
            editor.setTheme('ace/theme/katzenmilch');
            editor.setValue(value);
            editor.setOptions({
                maxLines: 500,
                minLines: 1,
                readOnly: true,
                highlightActiveLine: false,
                highlightGutterLine: false,
                showGutter: false,
                showPrintMargin: false,
            });
            editor.clearSelection();
            editor.textInput.getElement().disabled = true;
            editor.renderer.$cursorLayer.element.style.opacity = 0;
            resolve(editor);
        }, 'brace');
    });
}


/**
 * Convert the contents of the `id` field of a schema to a schema name.
 *
 * @param {*} schemaId - `id` property from schema
 */
function schemaIdToName(schemaId) {
    const pathMatch = schemaId.match(/\/profiles\/(.*).json/);
    return pathMatch && pathMatch.length ? pathMatch[1] : null;
}


/**
 * Convert the schema id property value to a page URI.
 *
 * @param {string} schemaId - value of id property within a schema
 */
function schemaIdToPage(schemaId) {
    return schemaId.slice(0, -5);
}


/**
 * Collect any linkTo and linkFrom properties within the schema object in the `prop` object. Two
 * arrays of these string properties get returned as an object with this format...
 *
 * {
 *     linkTo - array of linkTo property strings
 *     linkFrom - array of linkFrom property strings
 * }
 *
 * @param {object} prop - Schema property containing its own terms.
 */
function collectLinks(prop) {
    const propKeys = Object.keys(prop);
    const linksLists = { linkTo: [], linkFrom: [] };

    propKeys.forEach((key) => {
        if (key === 'linkTo' || key === 'linkFrom') {
            // Simple linkTo or linkFrom property; adds its value to the array we're collecting.
            linksLists[key].push(key === 'linkFrom' ? prop[key].split('.')[0] : prop[key]);
        } else if (typeof prop[key] === 'object' && !Array.isArray(prop[key])) {
            // The schema property key is not one of `nonlinkProps` and has a value that's an object.
            // Look for linkTo properties within this object.
            const subLinksLists = collectLinks(prop[key]);
            linksLists.linkTo = linksLists.linkTo.concat(subLinksLists.linkTo);
            linksLists.linkFrom = linksLists.linkFrom.concat(subLinksLists.linkFrom);
        }
    });

    return linksLists;
}


// Display links to the schemas specified by the array of schema object names given in
// `schemaNames`. Any schema objects name without a corresponding schema get displayed as plain
// text instead of a link.
const SchemaTermLinks = (props) => {
    const { schemaNames, profilesMap } = props;

    return (
        <span>
            {schemaNames.map((link, i) => {
                const schemaId = profilesMap[link];
                if (schemaId) {
                    return (
                        <span key={link}>
                            {i > 0 ? <span>, </span> : null}
                            <a href={schemaIdToPage(schemaId)}>{link}</a>
                        </span>
                    );
                }

                // No corresponding schema, so just display the schema name as plain text.
                return <span key={link}>{i > 0 ? <span>, </span> : null}{link}</span>;
            })}
        </span>
    );
};

SchemaTermLinks.propTypes = {
    schemaNames: PropTypes.array.isRequired, // Array of the names of schemas to link to
    profilesMap: PropTypes.object.isRequired, // Map of schema object @type to corresponding schema ID
};


// Display linkFrom and linkTo property values as links to the respecive schema pages, given a
// property in the schema that contains at least one linkTo and/or linkFrom.
const SchemaTermLinksSection = (props) => {
    const { schemaProp, profilesMap } = props;

    // Collect all the linkTo and linkFrom @types from schemaProp.
    const collectedLinks = collectLinks(schemaProp);

    if (collectedLinks.linkTo.length || collectedLinks.linkFrom.length) {
        return (
            <div className="schema-term-links">
                {collectedLinks.linkTo.length ?
                    <div>
                        <span className="schema-term-links__title">References: </span>
                        <SchemaTermLinks schemaNames={collectedLinks.linkTo} profilesMap={profilesMap} />
                    </div>
                : null}
                {collectedLinks.linkFrom.length ?
                    <div>
                        <span className="schema-term-links__title">Referenced by: </span>
                        <SchemaTermLinks schemaNames={collectedLinks.linkFrom} profilesMap={profilesMap} />
                    </div>
                : null}
            </div>
        );
    }

    // No linkTo or linkFrom found in the property being displayed.
    return null;
};

SchemaTermLinksSection.propTypes = {
    schemaProp: PropTypes.object.isRequired, // Schema property from which to collect and display links
    profilesMap: PropTypes.object.isRequired, // Map of schema object @type to corresponding schema ID
};


// Display JSON for one schema term.
class SchemaTermJsonDisplay extends React.Component {
    constructor(props) {
        super(props);

        // Initialize component properties.
        this.editor = null; // Tracks brace editor reference.
        this.id = `profile-value-json-${props.term}`; // HTML ID of component to draw brace editor into
    }

    componentDidMount() {
        // Now that the JSON display component has mounted,
        const { schemaValue, term } = this.props;

        // Create a read-only brace editor to display the formatted JSON.
        createJsonDisplay(this.id, schemaValue[term]).then((editor) => {
            // The brace editor successfully created. Save the reference to the brace editor
            // instance so we can get rid of it when the JSON display is closed.
            this.editor = editor;
        });
    }

    componentWillUnmount() {
        if (this.editor) {
            this.editor.destroy();
            this.editor = null;
        }
    }

    render() {
        return (
            <div className="profile-value__json-content">
                <div id={this.id} />
            </div>
        );
    }
}

SchemaTermJsonDisplay.propTypes = {
    schemaValue: PropTypes.object.isRequired, // Schema object to display
    term: PropTypes.string.isRequired, // Item within the schema object to display
};


// Display one object-type term, with associated JSON.
class SchemaTermItemDisplay extends React.Component {
    constructor() {
        super();

        // Set initial React state
        this.state = {
            jsonOpen: false,
        };

        // Bind `this` to non-React methods.
        this.handleDisclosureClick = this.handleDisclosureClick.bind(this);

        // Set object properties.
        this.editor = null;
    }

    handleDisclosureClick() {
        this.setState(prevState => ({ jsonOpen: !prevState.jsonOpen }));
    }

    render() {
        const { schemaValue, term, linkedTerm, profilesMap } = this.props;

        return (
            <div>
                <div className="profile-value__item">
                    <button className="profile-value__disclosure-button" onClick={this.handleDisclosureClick}>{collapseIcon(!this.state.jsonOpen)}</button>
                    <span> {term}</span>
                </div>
                {this.state.jsonOpen ?
                    <div>
                        <SchemaTermJsonDisplay schemaValue={schemaValue} term={term} />
                        {linkedTerm ? <SchemaTermLinksSection schemaProp={schemaValue[term]} profilesMap={profilesMap} /> : null}
                    </div>
                : null}
            </div>
        );
    }
}

SchemaTermItemDisplay.propTypes = {
    schemaValue: PropTypes.object.isRequired, // Schema object to display
    term: PropTypes.string.isRequired, // Item within the schema object to display
    linkedTerm: PropTypes.bool.isRequired, // True if property should be searched for linkTo/linkFrom
    profilesMap: PropTypes.object.isRequired, // Map of schema object @type to corresponding schema ID
};


// Display all property terms of a schema object (usually dependencies and properties).
const SchemaTermDisplay = (props) => {
    const { schemaValue, linkedTerm, schemaName, profilesMap } = props;

    return (
        <div>
            {Object.keys(props.schemaValue).sort().map(key =>
                <SchemaTermItemDisplay key={`${schemaName}-${key}`} term={key} schemaValue={schemaValue} schemaName={schemaName} linkedTerm={linkedTerm} profilesMap={profilesMap} />
            )}
        </div>
    );
};

SchemaTermDisplay.propTypes = {
    schemaValue: PropTypes.object.isRequired, // Object from schema to display
    linkedTerm: PropTypes.bool.isRequired, // True if property should be searched for linkTo/linkFrom
    schemaName: PropTypes.string.isRequired, // Name of the schema from the URL
    profilesMap: PropTypes.object.isRequired, // Map of schema object @type to corresponding schema ID
};


// Display one term of the schema regardless of its value type.
const TermDisplay = (props) => {
    const { termSchema, linkedTerm, schemaName, profilesMap } = props;
    const termType = typeof termSchema;

    // If the schema term value has a simple type (string, boolean, number), then just display
    // that.
    const displayMethod = simpleTypeDisplay[termType];
    if (displayMethod) {
        return <div>{displayMethod(termSchema)}</div>;
    }

    // If the schema term value is an object, see if it's actually an array.
    if (termType === 'object') {
        if (Array.isArray(termSchema)) {
            // The value's an array, so display a list. Filter out any non-simple types in the
            // array (at this time, I don't think any schema array values have non-simple types)
            // and sort the results.
            const simpleTermValues = termSchema.filter(item => !!simpleTypeDisplay[typeof item]).sort();
            if (simpleTermValues.length) {
                return (
                    <div>
                        {simpleTermValues.map((item, i) => (
                            <div key={i}>{simpleTypeDisplay[typeof item](item)}</div>
                        ))}
                    </div>
                );
            }

            // No simple term types in the schema value, so don't show anything.
            return null;
        }

        // The value's an object, so display the schema value itself.
        return <SchemaTermDisplay schemaValue={termSchema} linkedTerm={linkedTerm} schemaName={schemaName} profilesMap={profilesMap} />;
    }
    return null;
};

TermDisplay.propTypes = {
    termSchema: PropTypes.any.isRequired, // Value for `term` in the schema
    linkedTerm: PropTypes.bool.isRequired, // True if the schema term should be searched for linkTo/linkFrom
    schemaName: PropTypes.string.isRequired, // Name of the schema from URL
    profilesMap: PropTypes.object.isRequired, // Map of schema object @type to corresponding schema ID
};


class DisplayObjectSection extends React.PureComponent {
    constructor() {
        super();

        // Set initial React component state.
        this.state = {
            sectionOpen: false, // True if the section has been opened for display
        };

        // Bind `this` to non-React methods.
        this.handleDisclosureClick = this.handleDisclosureClick.bind(this);
    }

    handleDisclosureClick() {
        // Click in the disclosure icon. Toggle the `sectionOpen` state to show or hide the list of
        // child properties.
        this.setState(prevState => ({ sectionOpen: !prevState.sectionOpen }));
    }

    render() {
        const { term, schema, schemaName, profilesMap } = this.props;

        // Set aria values for accessibility.
        const accordionId = `profile-display-values-${term}`;
        const accordionLabel = `profile-value-item-${term}`;

        return (
            <div className={`profile-display__section${this.state.sectionOpen ? ' profile-display__section--open' : ''}`}>
                <h3 className="profile-value__item" id={accordionLabel}>
                    <button
                        className="profile-value__disclosure-button"
                        data-toggle="collapse"
                        data-target={`#${accordionId}`}
                        aria-controls={accordionId}
                        aria-expanded={this.state.sectionOpen}
                        onClick={this.handleDisclosureClick}
                    >
                        {collapseIcon(!this.state.sectionOpen)}
                    </button>
                    {titleMap[term] || term}
                </h3>
                {this.state.sectionOpen ?
                    <div id={accordionId} aria-labelledby={accordionLabel} className="profile-display__values">
                        <TermDisplay termSchema={schema[term]} linkedTerm={linkedTerms.indexOf(term) !== -1} schemaName={schemaName} profilesMap={profilesMap} />
                    </div>
                : null}
            </div>
        );
    }
}

DisplayObjectSection.propTypes = {
    term: PropTypes.string.isRequired, // Top-level property name in schema being displayed
    schema: PropTypes.object.isRequired, // Entire Schema containing term being displayed
    schemaName: PropTypes.string.isRequired, // Name of the schema from URL
    profilesMap: PropTypes.object.isRequired, // Map of schema object @type to corresponding schema ID
};


// Display an entire formatted schema.
const DisplayObject = (props) => {
    const { schema, schemaName, profilesMap } = props;
    const schemaTerms = Object.keys(schema).filter(term => excludedTerms.indexOf(term) === -1);
    return (
        <div className="profile-display">
            {schemaTerms.map(term =>
                <DisplayObjectSection key={`${schemaName}-${term}`} term={term} schemaName={schemaName} profilesMap={profilesMap} schema={schema} />
            )}
        </div>
    );
};

DisplayObject.propTypes = {
    schema: PropTypes.object.isRequired, // Schema being displayed
    schemaName: PropTypes.string.isRequired, // Name of the schema from URL
    profilesMap: PropTypes.object, // Map of schema object @type to corresponding schema ID; required but provided by GET response
};


// Display a complete raw schema object.
class DisplayRawObject extends React.Component {
    constructor() {
        super();

        // Set object properties.
        this.editor = null;
    }

    componentDidMount() {
        // Create a read-only brace editor to display the formatted JSON.
        createJsonDisplay('raw-schema', this.props.schema).then((editor) => {
            // The brace editor successfully created. Save the reference to the brace editor
            // instance so we can get rid of it when the JSON display is closed.
            this.editor = editor;
        });
    }

    componentWillUnmount() {
        if (this.editor) {
            this.editor.destroy();
            this.editor = null;
        }
    }

    render() {
        return <div id="raw-schema" />;
    }
}

DisplayRawObject.propTypes = {
    schema: PropTypes.object.isRequired, // Schema to display as a raw object
};


// Display markdown.
const Markdown = (props) => {
    const html = marked(props.source, { sanitize: true });
    return <div dangerouslySetInnerHTML={{ __html: html }} />;
};

Markdown.propTypes = {
    source: PropTypes.string,
};

Markdown.defaultProps = {
    source: '',
};


// Display the Markdown-formatted change log.
const ChangeLog = props => (
    <div>
        <Markdown source={props.source} />
    </div>
);

ChangeLog.propTypes = {
    source: PropTypes.string,
};

ChangeLog.defaultProps = {
    source: '',
};


// Renders the panel that displays the schema given in the `schema` prop. Included in this
// implementation is a GET request for /profiles-map/ which is a mapping of schema object name to
// schema id. /profiles/ provides the same information but in a very large object not provided when
// loading a single schema, while /profiles-map/ is a relatively small object.
const SchemaPanel = (props, reactContext) => {
    const { schema, schemaName } = props;

    // Determine whether we should display an "Add" button or not depending on the user's logged-in
    // state.
    const loggedIn = !!(reactContext.session && reactContext.session['auth.userid']);
    const decoration = loggedIn ? <a href={`/${schemaName}/#!add`} className="btn btn-info profiles-add-obj__btn">Add</a> : null;
    const decorationClasses = loggedIn ? 'profiles-add-obj' : '';

    return (
        <Panel>
            <TabPanel
                tabs={{ formatted: 'Formatted', raw: 'Raw' }}
                decoration={decoration}
                decorationClasses={decorationClasses}
            >
                <TabPanelPane key="formatted">
                    <PanelBody>
                        <FetchedData>
                            <Param name="profilesMap" url="/profiles-map/" />
                            <DisplayObject schema={schema} schemaName={schemaName} />
                        </FetchedData>
                    </PanelBody>
                </TabPanelPane>
                <TabPanelPane key="raw">
                    <PanelBody>
                        <DisplayRawObject schema={schema} />
                    </PanelBody>
                </TabPanelPane>
            </TabPanel>
        </Panel>
    );
};

SchemaPanel.propTypes = {
    schema: PropTypes.object.isRequired, // Schema to display
    schemaName: PropTypes.string, // Schema name e.g. genetic_modification
};

SchemaPanel.defaultProps = {
    profilesMap: {},
};

SchemaPanel.contextTypes = {
    session: PropTypes.object,
};


// Displays a page for a single schema given in the `context` prop.
const SchemaPage = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context);
    const title = context.title;

    // The schema id is a path to the schema's JSON. Convert that to just the schema name.
    const schemaName = schemaIdToName(context.id);

    // Set up the "breadcrumbs" (sneer quotes because it's really just a link to /profiles/).
    // If schemaName happened to be null (which it realistically can't), <BreadCrumbs> would
    // harmlessly display nothing in the second element.
    const crumbs = [
        { id: 'Profiles', uri: '/profiles/', wholeTip: 'All schemas' },
        { id: schemaName },
    ];

    return (
        <div className={itemClass}>
            <header className="row">
                <div className="col-sm-12">
                    <Breadcrumbs root="/profiles/" crumbs={crumbs} />
                    <h2>{title}</h2>
                </div>
            </header>
            {typeof context.description === 'string' ? <p className="description">{context.description}</p> : null}
            <SchemaPanel schema={context} schemaName={schemaName} />
            {context.changelog ?
                <Panel>
                    <PanelHeading>
                        <h4>ChangeLog</h4>
                    </PanelHeading>
                    <PanelBody>
                        <FetchedData>
                            <Param name="source" url={context.changelog} type="text" />
                            <ChangeLog />
                        </FetchedData>
                    </PanelBody>
                </Panel>
            : null}
        </div>
    );
};

SchemaPage.propTypes = {
    context: PropTypes.object.isRequired, // Schema to display
};

globals.contentViews.register(SchemaPage, 'JSONSchema');


// Displays a page listing all schemas available in the system, as well as buttons by each one to
// add a new object of that type if you're logged in.
const AllSchemasPage = (props, reactContext) => {
    const { context } = props;
    const loggedIn = !!(reactContext.session && reactContext.session['auth.userid']);

    // Get a sorted list of all available schema object names (e.g. GeneticModification). Filter
    // out those without any `identifyingProperties` because the user can't add objects of that
    // type, nor display their schemas.
    const objectNames = Object.keys(context).sort().filter(objectName => (
        !!(context[objectName].identifyingProperties && context[objectName].identifyingProperties.length)
    ));

    return (
        <Panel>
            <PanelBody>
                <div className="schema-list">
                    {objectNames.map((objectName) => {
                        // `objectName` is the @type of each objects e.g. GeneticModification
                        // `schemaName` is the system name of the objects e.g. genetic_modification
                        // `schemaPath` is the schema page path e.g. /profiles/genetic_modification
                        const schemaName = schemaIdToName(context[objectName].id);
                        const schemaPath = schemaIdToPage(context[objectName].id);

                        return (
                            <div className="schema-list__item" key={objectName}>
                                {loggedIn ? <a className="btn btn-info btn-xs" href={`/${schemaName}/#!add`}>Add</a> : null}
                                <a href={schemaPath} title={context[objectName].description}>{objectName}</a>
                            </div>
                        );
                    })}
                </div>
            </PanelBody>
        </Panel>
    );
};

AllSchemasPage.propTypes = {
    context: PropTypes.object.isRequired, // /profiles/ object
};

AllSchemasPage.contextTypes = {
    session: PropTypes.object,
};

globals.contentViews.register(AllSchemasPage, 'JSONSchemas');
