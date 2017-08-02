import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import _ from 'underscore';
import Table from './collection';
import { FetchedData, Param } from './fetched';
import { JSONSchemaForm } from './form';
import * as globals from './globals';
import { AlternateAccession } from './objectutils';


class DisplayText extends React.Component {
    render() {
        const { dataObject } = this.props;
        // const mixinArray = [];
        // const typevalues = [];
        // const categoryTitles = [];
        const dataArray = Object.keys(dataObject).map((term) => {
            const labels = term;
            return labels;
        });
        const titles = [];
        const idvalues = [];


            // if (dataObject[key].type) {
            //     typevalues.push(dataObject[key].type);
            // } else {
            //     typevalues.push('N/A');
            // }
            // if (dataObject[key].mixinProperties && dataObject[key].mixinProperties.length) {
            //     mixinArray.push(dataObject[key].mixinProperties);
            // } else {
            //     mixinArray.push('N/A');
            // }

        const dataRenderObject = dataArray.map((item, index) => {
            // const arrayObject = mixinArray[index];
            // for (let i = 0; i < dataArray.length; i += 1) {
            const key = dataArray[index];
            const singleObject = dataObject[key];
            // console.log(_.size(singleObject));
            const objectKeys = Object.keys(singleObject);
            // const objectValues = Object.values(singleObject); // Only available in ES2017
            const objectValues = Object.keys(singleObject).map(stuff =>
                singleObject[stuff]
            );
            console.log(objectValues);

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
                <div key={index} className="panel panel-default">
                    <div className="file-gallery-graph-header collapsing-title"><button className="collapsing-title-trigger pull-left" data-trigger="true"><svg className="collapsing-title-control collapsing-title-icon" data-name="Collapse Icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512"><g><title>Panel open</title><circle className="bg" cx="256" cy="256" r="240" /><line className="content-line" x1="151.87" y1="256" x2="360.13" y2="256" /></g></svg></button><h4>{titles[index]}</h4></div>
                    {objectKeys.map((term, id) =>
                        <div key={id}>
                            <div className="container" data-role="collapsible">
                                <dl className="key-value">
                                    <div data-test="id">
                                        <dt>{term}</dt>
                                        <dd>
                                            {objectKeys[id] === 'id' ?
                                                <div>{idvalues[index]}</div>
                                            :
                                                Array.isArray(objectValues[id]) !== true && typeof objectValues[id] !== 'object' && objectValues[id] !== false ?
                                                <div>{objectValues[id]}</div>
                                            :
                                            null
                                            }
                                        </dd>
                                    </div>
                                </dl>
                            </div>
                        </div>
                    )};
                </div>
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
            {/* <section className="view-detail panel"> */}
                {/* <div className="container"> */}
                    <DisplayText dataObject={context} />
                    <pre>{JSON.stringify(context, null, 4)}</pre>
                {/* </div> */}
            {/* </section> */}
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
