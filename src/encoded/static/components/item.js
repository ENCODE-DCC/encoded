import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import * as encoding from '../libs/query_encoding';
import { Panel } from '../libs/ui/panel';
import Table from './collection';
import { FetchedData, Param } from './fetched';
import { JSONSchemaForm } from './form';
import * as globals from './globals';
import { AlternateAccession, ItemAccessories } from './objectutils';


const Fallback = (props, reactContext) => {
    const { context } = props;
    const title = typeof context.title === 'string' ? context.title : url.parse(reactContext.location_href).path;
    return (
        <div className="view-item">
            <header>
                <h1>{title}</h1>
                <ItemAccessories item={context} />
            </header>
            {typeof context.description === 'string' ? <p className="description">{context.description}</p> : null}
            <section className="view-detail panel">
                <pre>{JSON.stringify(context, null, 4)}</pre>
            </section>
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
    const { context } = props;
    const itemClass = globals.itemClass(context, 'view-item');
    const title = globals.listingTitles.lookup(context)({ context });
    const ItemPanel = globals.panelViews.lookup(context);

    return (
        <div className={itemClass}>
            <header>
                <h1>{title}</h1>
                <div className="replacement-accessions">
                    <AlternateAccession altAcc={context.alternate_accessions} />
                </div>
                <ItemAccessories item={context} />
            </header>
            {context.description ? <p className="description">{context.description}</p> : null}
            <Panel>
                <ItemPanel {...props} />
            </Panel>
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


export const ItemComponent = (props) => {
    const { context } = props;
    const itemClass = globals.itemClass(context, 'view-detail');
    return (
        <div className={itemClass}>
            <pre>{JSON.stringify(context, null, 4)}</pre>
        </div>
    );
};

ItemComponent.propTypes = {
    context: PropTypes.object.isRequired,
};

globals.panelViews.register(ItemComponent, 'Item');


const listingTitle = function listingTitle(props) {
    const { context } = props;
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
        const { context } = this.props;
        const itemClass = globals.itemClass(context, 'view-item');
        let title = globals.listingTitles.lookup(context)({ context });
        let action;
        let fetchedForm;
        let type;
        if (context['@type'][0].indexOf('Collection') !== -1) { // add form
            type = context['@type'][0].substr(0, context['@type'][0].length - 10);
            title = `${title}: Add`;
            action = context['@id'];
            fetchedForm = (
                <FetchedData>
                    <Param name="schemas" url="/profiles/" />
                    <JSONSchemaForm
                        type={type}
                        action={action}
                        method="POST"
                        onFinish={this.finished}
                        showReadOnly={false}
                        showSaveAndAdd
                    />
                </FetchedData>
            );
        } else { // edit form
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
                <header>
                    <h2>{title}</h2>
                    <ItemAccessories item={context} />
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
    if (!items || !items.length > 0) return null;

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
    const itemUrl = encoding.encodedURIOLD(`${props.url}&status=released&status=submitted&status=in+progress`);
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
