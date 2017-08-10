import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import Table from './collection';
import { FetchedData, Param } from './fetched';
import { JSONSchemaForm } from './form';
import * as globals from './globals';
import { AlternateAccession } from './objectutils';
import { collapseIcon } from '../libs/svg-icons';

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
    const newValue = Object.values(currentValue);
    const classname = outlineClass[outlineNumber];
    const outline = outlineNumber + 1;
    return (
        <div>
            {typeof term !== 'object' ?
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
    dataObject: PropTypes.object.isRequired,
    term: PropTypes.string.isRequired,
    i: PropTypes.number.isRequired,
};
CollapsibleElements.defaultProps = {
    i: 0,
};

class ObjectPanel extends React.Component {
    constructor() {
        super();
        // Initialize React state variables.
        this.state = {
            collapsed: true, // Collapsed/uncollapsed state
        };
        this.handleCollapse = this.handleCollapse.bind(this);
    }
    handleCollapse() {
        // Handle click on panel collapse icon
        this.setState({ collapsed: !this.state.collapsed });
    }
    render() {
        const { title, idvalue, index, objectKeys, objectValues } = this.props;
        const removedItemKeys = ['type', 'additionalProperties', 'mixinProperties'];
        return (
            <div key={index} className="panel panel-default">
                <div className="file-gallery-graph-header collapsing-title">
                    <button className="collapsing-title-trigger" onClick={this.handleCollapse}>{collapseIcon(this.state.collapsed, 'collapsing-title-icon')}</button><h4>{title}</h4></div>
                {!this.state.collapsed ?
                    objectKeys.map((term, id) =>
                        <div key={id}>
                            <div className="container">
                                <dl className="key-value">
                                    {removedItemKeys.includes(term) ?
                                        null
                                    :
                                        term === 'properties' || term === 'dependencies' ?
                                        <div data-test="id">
                                            <dt>{term}</dt>
                                            <dd>
                                                {Object.keys(objectValues[id]).map((item, i) =>
                                                    <CollapsibleElements term={item} dataObject={objectValues[id]} key={i} />
                                                )}
                                            </dd>
                                        </div>
                                    :
                                        <div data-test="id">
                                            <dt>{term}</dt>
                                            <dd>
                                                {objectKeys[id] === 'id' ?
                                                    <div>{idvalue}</div>
                                                :
                                                    Array.isArray(objectValues[id]) !== true && typeof objectValues[id] !== 'object' && objectValues[id] !== false ?
                                                    <div>{objectValues[id]}</div>
                                                :
                                                    Array.isArray(objectValues[id]) === true && typeof objectValues[id][0] === 'string' ?
                                                    objectValues[id].map((item, i) => <div key={i}>{item}</div>)
                                                :
                                                    objectValues[id] === false && Array.isArray(objectValues[id]) !== true && typeof objectValues[id] !== 'object' ?
                                                    <div>false</div>
                                                :
                                                    Array.isArray(objectValues[id]) === true && typeof objectValues[id][0] === 'object' && objectValues[id][0].$ref ?
                                                    Object.keys(objectValues[id]).map((item, i) => <div key={i}>{objectValues[id][i].$ref}</div>)
                                                :
                                                    typeof objectValues[id] === 'object' && typeof objectValues[id][Object.keys(objectValues[id])[0]] !== 'object' ?
                                                    Object.keys(objectValues[id]).map((item, i) => <div key={i}>{Object.keys(objectValues[id])[i]}: {objectValues[id][Object.keys(objectValues[id])[i]]}</div>)
                                                :
                                                    typeof objectValues[id] === 'object' && typeof objectValues[id][Object.keys(objectValues[id])[0]] === 'object' ?
                                                    Object.keys(objectValues[id]).map((item, i) =>
                                                    <div key={i}>
                                                        {Array.isArray(objectValues[id]) ?
                                                            <div className={outlineClass[0]}>lookupLibrary.array(objectValues[id][Object.keys(objectValues[id])[0]][Object.keys(objectValues[id][Object.keys(objectValues[id])[0]])], Object.values(objectValues[id])[i], 0)</div>
                                                        :
                                                            <div className={outlineClass[0]}>{lookupLibrary[typeof objectValues[id]](item, Object.values(objectValues[id])[i], 0)}</div>
                                                        }
                                                    </div>
                                                    )
                                                :
                                                null
                                                }
                                            </dd>
                                        </div>
                                    }
                                </dl>
                            </div>
                        </div>
                    )
                :
                    null
                }
            </div>
        );
    }
}

ObjectPanel.propTypes = {
    title: PropTypes.string.isRequired,
    idvalue: PropTypes.string.isRequired,
    objectKeys: PropTypes.array.isRequired,
    objectValues: PropTypes.array.isRequired,
    index: PropTypes.number.isRequired,
};


class DisplayText extends React.Component {

    render() {
        const { dataObject } = this.props;
        const dataArray = Object.keys(dataObject).map((term) => {
            const labels = term;
            return labels;
        });
        const titles = [];
        const idvalues = [];

        const dataRenderObject = dataArray.map((item, index) => {
            const key = dataArray[index];
            const singleObject = dataObject[key];
            const objectKeys = Object.keys(singleObject);
            // const objectValues = Object.values(singleObject); // Only available in ES2017
            const objectValues = Object.keys(singleObject).map(stuff =>
                singleObject[stuff]
            );
            if (dataObject[key].title && dataObject[key].title.length > 0) {
                titles.push(dataObject[key].title);
            } else {
                titles.push(dataArray[index]);
            }
            if (dataObject[key].id && dataObject[key].id.length > 0) {
                const str = dataObject[key].id;
                const extract = str.match(/profiles\/(.*)\.json/);
                idvalues.push(extract[1]);
            } else {
                idvalues.push('N/A');
            }
            return (
                <ObjectPanel title={titles[index]} idvalue={idvalues[index]} index={index} objectKeys={objectKeys} objectValues={objectValues} />
            );
        });
        return (
            <div>
                {dataRenderObject}
            </div>
        );
    }
}

DisplayText.propTypes = {
    dataObject: PropTypes.object,
};

DisplayText.defaultProps = {
    dataObject: {},
};

const Fallback = (props, reactContext) => {
    const context = props.context;
    const title = typeof context.title === 'string' ? context.title : url.parse(reactContext.location_href).path;
    return (
        <div className="view-item">
            <header className="row">
                <div className="col-sm-12">
                    <h2>{title}</h2>
                </div>
            </header>
            {typeof context.description === 'string' ? <p className="description">{context.description}</p> : null}
            <DisplayText dataObject={context} />
        </div>
    );
};

Fallback.propTypes = {
    context: PropTypes.object.isRequired, // Object being displayed
};

Fallback.contextTypes = {
    location_href: PropTypes.string,
};


const Item = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'view-item');
    const title = globals.listingTitles.lookup(context)({ context });
    const ItemPanel = globals.panelViews.lookup(context);

    return (
        <div className={itemClass}>
            <header className="row">
                <div className="col-sm-12">
                    <h2>{title}</h2>
                    <AlternateAccession altAcc={context.alternate_accessions} />
                </div>
            </header>
            <div className="row item-row">
                <div className="col-sm-12">
                    {context.description ? <p className="description">{context.description}</p> : null}
                </div>
                <ItemPanel {...props} />
            </div>
        </div>
    );
};

Item.propTypes = {
    context: PropTypes.object.isRequired, // Object being displayed as a generic item.
};

globals.contentViews.register(Item, 'Item');

// Also use this view as a fallback for anything we haven't registered.
globals.contentViews.fallback = function fallback() {
    return Fallback;
};


export const Panel = (props) => {
    const context = props.context;
    const itemClass = globals.itemClass(context, 'view-detail panel');
    return (
        <section className="col-sm-12">
            <div className={itemClass}>
                <pre>{JSON.stringify(context, null, 4)}</pre>
            </div>
        </section>
    );
};

Panel.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.panelViews.register(Panel, 'Item');


// Also use this view as a fallback for anything we haven't registered
globals.panelViews.fallback = function fallback() {
    return Panel;
};


const listingTitle = function listingTitle(props) {
    const context = props.context;
    return context.title || context.name || context.accession || context['@id'];
};

globals.listingTitles.register(listingTitle, 'Item');

// Also use this view as a fallback for anything we haven't registered
globals.listingTitles.fallback = function fallback() {
    return listingTitle;
};


class ItemEdit extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.finished = this.finished.bind(this);
    }

    finished(data) {
        const atId = data['@graph'][0]['@id'];
        this.context.navigate(atId);
    }

    render() {
        const context = this.props.context;
        const itemClass = globals.itemClass(context, 'view-item');
        let title = globals.listingTitles.lookup(context)({ context });
        let action;
        let fetchedForm;
        let type;
        if (context['@type'][0].indexOf('Collection') !== -1) {  // add form
            type = context['@type'][0].substr(0, context['@type'][0].length - 10);
            title = `${title}: Add`;
            action = context['@id'];
            fetchedForm = (
                <FetchedData>
                    <Param name="schemas" url="/profiles/" />
                    <JSONSchemaForm
                        type={type} action={action} method="POST"
                        onFinish={this.finished} showReadOnly={false} showSaveAndAdd
                    />
                </FetchedData>
            );
        } else {  // edit form
            type = context['@type'][0];
            title = `Edit ${title}`;
            const id = this.props.context['@id'];
            const editUrl = `${id}?frame=edit`;
            fetchedForm = (
                <FetchedData>
                    <Param name="context" url={editUrl} etagName="etag" />
                    <Param name="schemas" url="/profiles/" />
                    <JSONSchemaForm id={id} type={type} action={id} method="PUT" onFinish={this.finished} />
                </FetchedData>
            );
        }
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{title}</h2>
                    </div>
                </header>
                {fetchedForm}
            </div>
        );
    }
}

ItemEdit.propTypes = {
    context: PropTypes.object.isRequired,
};

ItemEdit.contextTypes = {
    navigate: PropTypes.func,
};

globals.contentViews.register(ItemEdit, 'Item', 'edit');
globals.contentViews.register(ItemEdit, 'Collection', 'add');


const FetchedRelatedItems = (props) => {
    const { Component, context, title, itemUrl } = props;
    if (context === undefined) return null;
    const items = context['@graph'];
    if (!items || !items.length) return null;

    return (
        <Component {...props} title={title} context={context} total={context.total} items={items} url={itemUrl} showControls={false} />
    );
};

FetchedRelatedItems.propTypes = {
    Component: PropTypes.any,
    context: PropTypes.object,
    title: PropTypes.string,
    itemUrl: PropTypes.string,
};

FetchedRelatedItems.defaultProps = {
    Component: Table,
    context: null,
    title: '',
    itemUrl: '',
};


export const RelatedItems = (props) => {
    const itemUrl = globals.encodedURI(`${props.url}&status=released&status=started&status=submitted&status=ready+for+review&status=in+progress`);
    const limitedUrl = `${itemUrl}&limit=${props.limit}`;
    const unlimitedUrl = `${itemUrl}&limit=all`;
    return (
        <FetchedData>
            <Param name="context" url={limitedUrl} />
            <FetchedRelatedItems {...props} itemUrl={unlimitedUrl} />
        </FetchedData>
    );
};

RelatedItems.propTypes = {
    url: PropTypes.string,
    limit: PropTypes.number,
};

RelatedItems.defaultProps = {
    url: '',
    limit: 5,
};
