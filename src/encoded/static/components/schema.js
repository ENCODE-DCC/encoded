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
];


// Functions to display simple schema term types, keyed by `typeof` result.
const simpleTypeDisplay = {
    string: item => <span>{item}</span>,
    boolean: item => <span>{item ? 'True' : 'False'}</span>,
    number: item => <span >{item}</span>,
};


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
 * Convert the contents of the `id` field of a schema to a path we can use to link to the page to
 * add a new object of its type.
 *
 * @param {*} schemaId - `id` property from schema
 */
function schemaIdToPath(schemaId) {
    const pathMatch = schemaId.match(/\/profiles\/(.*).json/);
    return pathMatch && pathMatch.length ? pathMatch[1] : null;
}


// Display JSON for one schema term.
class SchemaTermJsonDisplay extends React.Component {
    constructor() {
        super();

        // Initialize component properties.
        this.editor = null; // Tracks brace editor reference.
    }

    componentDidMount() {
        // Now that the JSON display component has mounted,
        const { schemaValue, term } = this.props;

        // Create a read-only brace editor to display the formatted JSON.
        createJsonDisplay(term, schemaValue[term]).then((editor) => {
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
        const { term } = this.props;

        return (
            <div className="profile-value__json">
                <div id={term} />
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
        const { schemaValue, term } = this.props;

        return (
            <div>
                <div className="profile-value__item">
                    <button className="profile-value__disclosure-button" onClick={this.handleDisclosureClick}>{collapseIcon(!this.state.jsonOpen)}</button>
                    <span> {term}</span>
                </div>
                {this.state.jsonOpen ?
                    <SchemaTermJsonDisplay schemaValue={schemaValue} term={term} />
                : null}
            </div>
        );
    }
}

SchemaTermItemDisplay.propTypes = {
    schemaValue: PropTypes.object.isRequired, // Schema object to display
    term: PropTypes.string.isRequired, // Item within the schema object to display
};


// Display all property terms of a schema object (usually dependencies and properties).
const SchemaTermDisplay = props => (
    <div>
        {Object.keys(props.schemaValue).sort().map(key =>
            <SchemaTermItemDisplay key={key} schemaValue={props.schemaValue} term={key} />
        )}
    </div>
);

SchemaTermDisplay.propTypes = {
    schemaValue: PropTypes.object, // Object from schema to display
};


// Display one term of the schema regardless of its value type.
const TermDisplay = (props) => {
    const { termSchema } = props;
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
        return <SchemaTermDisplay schemaValue={termSchema} />;
    }
    return null;
};

TermDisplay.propTypes = {
    termSchema: PropTypes.any.isRequired, // Value for `term` in the schema
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
        const { term, schema } = this.props;

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
                        <TermDisplay termSchema={schema[term]} />
                    </div>
                : null}
            </div>
        );
    }
}

DisplayObjectSection.propTypes = {
    term: PropTypes.string.isRequired, // Top-level property name in schema being displayed
    schema: PropTypes.object.isRequired, // Entire Schema containing term being displayed
};


// Display an entire formatted schema.
const DisplayObject = (props) => {
    const { schema } = props;
    const schemaTerms = Object.keys(schema).filter(term => excludedTerms.indexOf(term) === -1);
    return (
        <div className="profile-display">
            {schemaTerms.map(term =>
                <DisplayObjectSection key={term} term={term} schema={schema} />
            )}
        </div>
    );
};

DisplayObject.propTypes = {
    schema: PropTypes.object.isRequired,
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


const SchemaPage = (props, reactContext) => {
    const context = props.context;
    const itemClass = globals.itemClass(context);
    const title = context.title;
    const changelog = context.changelog;
    const loggedIn = !!(reactContext.session && reactContext.session['auth.userid']);

    // Generate a link to add an object for the currently displayed schema.
    const schemaPath = schemaIdToPath(context.id);

    // Set up the "breadcrumbs" (sneer quotes because it's really just a link to /profiles/).
    // If schemaPath happened to be null (which it realistically can't), <BreadCrumbs> would
    // harmlessly display nothing.
    const crumbs = [
        { id: 'Profiles', uri: '/profiles/', wholeTip: 'All schemas' },
        { id: schemaPath },
    ];


    // Determine whether we should display an "Add" button or not depending on the user's logged-in
    // state.
    const decoration = loggedIn ? <a href={`/${schemaPath}/#!add`} className="btn btn-info profiles-add-obj__btn">Add</a> : null;
    const decorationClasses = loggedIn ? 'profiles-add-obj' : '';

    return (
        <div className={itemClass}>
            <header className="row">
                <div className="col-sm-12">
                    <Breadcrumbs root="/profiles/" crumbs={crumbs} />
                    <h2>{title}</h2>
                </div>
            </header>
            {typeof context.description === 'string' ? <p className="description">{context.description}</p> : null}
            <Panel>
                <TabPanel
                    tabs={{ formatted: 'Formatted', raw: 'Raw' }}
                    decoration={decoration}
                    decorationClasses={decorationClasses}
                >
                    <TabPanelPane key="formatted">
                        <PanelBody>
                            <DisplayObject schema={context} />
                        </PanelBody>
                    </TabPanelPane>
                    <TabPanelPane key="raw">
                        <PanelBody>
                            <DisplayRawObject schema={context} />
                        </PanelBody>
                    </TabPanelPane>
                </TabPanel>
            </Panel>
            {changelog ?
                <Panel>
                    <PanelHeading>
                        <h4>ChangeLog</h4>
                    </PanelHeading>
                    <PanelBody>
                        <FetchedData>
                            <Param name="source" url={changelog} type="text" />
                            <ChangeLog />
                        </FetchedData>
                    </PanelBody>
                </Panel>
            : null}
        </div>
    );
};

SchemaPage.propTypes = {
    context: PropTypes.object.isRequired,
};

SchemaPage.contextTypes = {
    session: PropTypes.object,
};

globals.contentViews.register(SchemaPage, 'JSONSchema');


// Displays a page listing all schemas available in the system.
const AllSchemasPage = (props, reactContext) => {
    const { context } = props;
    const loggedIn = !!(reactContext.session && reactContext.session['auth.userid']);

    // Get a sorted list of all available schemas. Filter out those without any
    // `identifyingProperties` because the user can't add objects of that type.
    const schemaNames = Object.keys(context).sort().filter(schemaName => (
        !!(context[schemaName].identifyingProperties && context[schemaName].identifyingProperties.length)
    ));

    return (
        <Panel>
            <PanelBody>
                <div className="schema-list">
                    {schemaNames.map((schemaName) => {
                        const schemaId = context[schemaName].id;
                        const schemaPath = schemaIdToPath(schemaId);

                        return (
                            <div className="schema-list__item" key={schemaName}>
                                {loggedIn ? <a className="btn btn-info btn-xs" href={`/${schemaPath}/#!add`}>Add</a> : null}
                                <a href={schemaId} title={context[schemaName].description}>{schemaName}</a>
                            </div>
                        );
                    })}
                </div>
            </PanelBody>
        </Panel>
    );
};

AllSchemasPage.propTypes = {
    context: PropTypes.object.isRequired,
};

AllSchemasPage.contextTypes = {
    session: PropTypes.object,
};

globals.contentViews.register(AllSchemasPage, 'JSONSchemas');
