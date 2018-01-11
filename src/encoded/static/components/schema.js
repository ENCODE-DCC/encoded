import React from 'react';
import PropTypes from 'prop-types';
import marked from 'marked';
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


// Functions to display simple schema term types.
const simpleTypeDisplay = {
    string: item => <span>{item}</span>,
    boolean: item => <span>{item ? 'True' : 'False'}</span>,
    number: item => <span >{item}</span>,
};


class SchemaTermJsonDisplay extends React.Component {
    constructor() {
        super();

        // Initialize component properties.
        this.editor = null; // Tracks brace editor reference.
    }

    componentDidMount() {
        const { schemaValue, term } = this.props;

        require.ensure([
            'brace',
            'brace/mode/json',
            'brace/theme/katzenmilch',
        ], (require) => {
            const ace = require('brace');
            require('brace/mode/json');
            require('brace/theme/katzenmilch');
            const value = JSON.stringify(schemaValue[term], null, 4);
            this.editor = ace.edit(term);
            const session = this.editor.getSession();
            session.setMode('ace/mode/json');
            this.editor.setTheme('ace/theme/katzenmilch');
            this.editor.setValue(value);
            this.editor.setOptions({
                maxLines: 500,
                minLines: 1,
                readOnly: true,
                highlightActiveLine: false,
                highlightGutterLine: false,
                showGutter: false,
                showPrintMargin: false,
            });
            this.editor.clearSelection();
            this.editor.textInput.getElement().disabled = true;
            this.editor.renderer.$cursorLayer.element.style.opacity = 0;
        }, 'brace');
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
        )
    }
}

SchemaTermItemDisplay.propTypes = {
    schemaValue: PropTypes.object.isRequired, // Schema object to display
    term: PropTypes.string.isRequired, // Item within the schema object to display
};


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


const TermDisplay = (props) => {
    const { term, termSchema } = props;
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
    term: PropTypes.string.isRequired, // schema property term
    termSchema: PropTypes.any.isRequired, // Value for `term` in the schema
};


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


class DisplayObject extends React.Component {
    render() {
        const { schema } = this.props;
        const schemaTerms = Object.keys(schema).filter(term => excludedTerms.indexOf(term) === -1);
        return (
            <div className="profile-display">
                {schemaTerms.map(term =>
                    <dl className="profile-display__section" key={term}>
                        <dt>{titleMap[term] || term}</dt>
                        <TermDisplay term={term} termSchema={schema[term]} />
                    </dl>
                )}
            </div>
        );
    }
}

DisplayObject.propTypes = {
    schema: PropTypes.object.isRequired,
};


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


const ChangeLog = props => (
    <section className="view-detail panel">
        <div className="container">
            <Markdown source={props.source} />
        </div>
    </section>
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
            <section className="view-detail panel">
                <DisplayObject schema={context} />
            </section>
            {changelog && <FetchedData>
                <Param name="source" url={changelog} type="text" />
                <ChangeLog />
            </FetchedData>}
        </div>
    );
};

SchemaPage.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.contentViews.register(SchemaPage, 'JSONSchema');
