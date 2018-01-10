import React from 'react';
import PropTypes from 'prop-types';
import marked from 'marked';
import { collapseIcon } from '../libs/svg-icons';
import { Param, FetchedData } from './fetched';
import * as globals from './globals';

const outlineClass = ['indent-one', 'indent-two', 'indent-three', 'indent-four', 'indent-five', 'indent-six'];

function arrayMethod(term, currentValue, outlineNumber) {
    const outline = outlineNumber + 1;
    return (
        term.map((item, i) => <div key={i} className={outlineClass[outlineNumber]}>{lookupLibrary[typeof item](item, item, outline)}</div>)
    );
}


function objectMethod(term, currentValue, outlineNumber) {
    const newKey = Object.keys(currentValue);
    const newValue = Object.keys(currentValue).map(stuff =>
        currentValue[stuff]
    );
    // const newValue = Object.values(currentValue);
    const classname = outlineClass[outlineNumber];
    const outline = outlineNumber + 1;
    return (
        <div>
            {
                typeof term !== 'object' ?
                    <strong>{lookupLibrary[typeof term](term, currentValue, outline)}</strong>
                :
                    null
                }
                {newValue.map((item, i) =>
                <div key={i}>
                    {Array.isArray(item) ?
                        outlineNumber === 1 ?
                            <div className={classname}><i>{newKey[i]}:</i> {lookupLibrary.array(item, item, outline)}</div>
                        :
                            <div className={classname}>{newKey[i]}: {lookupLibrary.array(item, item, outline)}</div>
                    :
                        outlineNumber === 1 ?
                            <div className={classname}><i>{newKey[i]}:</i> {lookupLibrary[typeof item](item, item, outline)}</div>
                        :
                            <div className={classname}>{newKey[i]}: {lookupLibrary[typeof item](item, item, outline)}</div>
                    }
                </div>)
            }
        </div>
    );
}

const lookupLibrary = {
    string: (item) =>
        <span>{item}</span>,
    array: (item, currentValue, outlineNumber) =>
        arrayMethod(item, currentValue, outlineNumber),
    object: (item, currentValue, outlineNumber) =>
        objectMethod(item, currentValue, outlineNumber),
    boolean: (item) =>
        <span>{item ? 'True' : 'False'}</span>,
    number: (item, currentValue, outlineNumber) =>
        <span className={outlineClass[outlineNumber]}>{item}</span>,
};


class CollapsibleElements extends React.Component {
    constructor() {
        super();
        // Initialize React state variables.
        this.state = {
            collapsed: true, // Collapsed/uncollapsed state
            active: false,
        };
        this.handleCollapse = this.handleCollapse.bind(this);
    }
    handleCollapse() {
        // Handle click on panel collapse icon
        this.setState({ collapsed: !this.state.collapsed, active: !this.state.active });
    }

    render() {
        const { term, dataObject, i } = this.props;
        return (
            <div className="expandable">
                <div className="dropPanel">
                    <div onClick={this.handleCollapse} className={this.state.active ? 'triangle-down' : 'triangle-right'} />
                    <span>{term}</span>
                </div>
                <div key={i}>
                    {!this.state.collapsed ?
                        Array.isArray(dataObject[term]) ?
                            <div>{lookupLibrary.array(dataObject[term], dataObject[term], 0)}</div>
                        :
                            <div>{lookupLibrary[typeof dataObject[term]](dataObject[term], dataObject[term], 0)}</div>
                    :
                        null
                    }
                </div>
            </div>
        );
    }
}
CollapsibleElements.propTypes = {
    term: PropTypes.string.isRequired,
    i: PropTypes.number,
    dataObject: PropTypes.object.isRequired,
};
CollapsibleElements.defaultProps = {
    i: 0,
};


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


class SchemaTermItemDisplay extends React.Component {
    constructor() {
        super();

        // Set initial React state
        this.state = {
            jsonOpen: false,
        };

        // Bind `this` to non-React methods.
        this.handleDisclosureClick = this.handleDisclosureClick.bind(this);
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
                    <pre>{JSON.stringify(schemaValue[term], null, 4)}</pre>
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
        return <span>{displayMethod(termSchema)}</span>;
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
