import React from 'react';
import PropTypes from 'prop-types';
import marked from 'marked';
import { Param, FetchedData } from './fetched';
import * as globals from './globals';

let lookupLibrary;
const outlineClass = ['indent-one', 'indent-two', 'indent-three', 'indent-four', 'indent-five', 'indent-six'];
function stringMethod(term) {
    return (
        <span>{term}</span>
    );
}
function booleanMethod(term) {
    return (
        <span>
        {term === false ?
            <span>false</span>
        :
            <span>true</span>
        }
        </span>
    );
}
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

lookupLibrary = {
    string: (item, currentValue, outlineNumber) =>
        stringMethod(item, currentValue, outlineNumber),
    array: (item, currentValue, outlineNumber) =>
        arrayMethod(item, currentValue, outlineNumber),
    object: (item, currentValue, outlineNumber) =>
        objectMethod(item, currentValue, outlineNumber),
    boolean: (item, currentValue, outlineNumber) =>
        booleanMethod(item, currentValue, outlineNumber),
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

class DisplayObject extends React.Component {
    render() {
        const { dataObject } = this.props;
        const dataArray = Object.keys(dataObject).map((term) => {
            const labels = term;
            return labels;
        });
        const removedItemKeys = ['type', 'additionalProperties', 'mixinProperties'];
        return (
            <div>
                {dataArray.map((term, id) =>
                    <div key={id}>
                        <dl className="key-value">
                            {removedItemKeys.includes(term) ?
                                null
                            :
                                term === 'properties' || term === 'dependencies' ?
                                    <div data-test="id">
                                        <dt>{term}</dt>
                                        <dd>
                                            {Object.keys(dataObject[term]).map((item, i) =>
                                                <CollapsibleElements term={item} dataObject={dataObject[term]} key={i} />
                                            )}
                                        </dd>
                                    </div>
                                :
                                <div data-test="id">
                                    <dt>{term}</dt>
                                    <dd>
                                    {Array.isArray(dataObject[term]) ?
                                        <div>{lookupLibrary.array(dataObject[term], dataObject[term], 0)}</div>
                                    :
                                        <div>{lookupLibrary[typeof dataObject[term]](dataObject[term], dataObject[term], 0)}</div>
                                    }
                                    </dd>
                                </div>
                            }
                        </dl>
                    </div>
                )}
            </div>
        );
    }
}

DisplayObject.propTypes = {
    dataObject: PropTypes.object.isRequired,
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
                <DisplayObject dataObject={context} />
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
