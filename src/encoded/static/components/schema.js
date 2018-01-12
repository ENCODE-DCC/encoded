import React from 'react';
import PropTypes from 'prop-types';
import marked from 'marked';
import { Panel, PanelHeading, PanelBody, TabPanel, TabPanelPane } from '../libs/bootstrap/panel';
import { collapseIcon } from '../libs/svg-icons';
import { Param, FetchedData } from './fetched';
import * as globals from './globals';


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
        {Object.keys(props.schemaValue).map(key =>
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
    let displayMethod = simpleTypeDisplay[termType];
    if (displayMethod) {
        return <div>{displayMethod(termSchema)}</div>;
    }

    // If the schema term value is an object, see if it's actually an array.
    if (termType === 'object') {
        if (Array.isArray(termSchema)) {
            // The value's an array, so display a list.
            return (
                <div>
                    {termSchema.map((item, i) => {
                        displayMethod = simpleTypeDisplay[typeof item];
                        if (displayMethod) {
                            // The schema term value array item is a simple type, so just
                            // display it normally.
                            return <div key={i}>{displayMethod(item)}</div>;
                        }

                        // The array element isn't a simple type, so just ignore it.
                        return null;
                    })}
                </div>
            );
        }

        // The value's an object, so display the schema value itself.
        return <SchemaTermDisplay schemaValue={termSchema} />;
    }
    return null;
};

TermDisplay.propTypes = {
    termSchema: PropTypes.any.isRequired, // Value for `term` in the schema
};


// Display an entire formatted schema.
const DisplayObject = (props) => {
    const { schema } = props;
    const schemaTerms = Object.keys(schema).filter(term => excludedTerms.indexOf(term) === -1);
    return (
        <div className="profile-display">
            {schemaTerms.map(term =>
                <div className="profile-display__section" key={term}>
                    <h3>{titleMap[term] || term}</h3>
                    <div className="profile-display__values">
                        <TermDisplay termSchema={schema[term]} />
                    </div>
                </div>
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


const SchemaPage = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context);
    const title = context.title;
    const changelog = context.changelog;
    return (
        <div className={itemClass}>
            <header className="row">
                <div className="col-sm-12">
                    <h2>{title}</h2>
                </div>
            </header>
            {typeof context.description === 'string' ? <p className="description">{context.description}</p> : null}
            <Panel>
                <TabPanel tabs={{ formatted: 'Formatted', raw: 'Raw' }}>
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
            <Panel>
                <PanelHeading>
                    <h4>ChangeLog</h4>
                </PanelHeading>
                <PanelBody>
                    {changelog && <FetchedData>
                        <Param name="source" url={changelog} type="text" />
                        <ChangeLog />
                    </FetchedData>}
                </PanelBody>
            </Panel>
        </div>
    );
};

SchemaPage.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(SchemaPage, 'JSONSchema');
