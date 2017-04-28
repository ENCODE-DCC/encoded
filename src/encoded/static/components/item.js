'use strict';
var React = require('react');
var collection = require('./collection');
var fetched = require('./fetched');
var globals = require('./globals');
var audit = require('./audit');
var form = require('./form');
var _ = require('underscore');

var cx = require('react/lib/cx');
var AuditIndicators = audit.AuditIndicators;
var AuditDetail = audit.AuditDetail;
var AuditMixin = audit.AuditMixin;
var JSONSchemaForm = form.JSONSchemaForm;
var Table = collection.Table;


var Fallback = module.exports.Fallback = React.createClass({
    contextTypes: {
        location_href: React.PropTypes.string
    },

    render: function() {
        var url = require('url');
        var context = this.props.context;
        var title = typeof context.title == "string" ? context.title : url.parse(this.context.location_href).path;
        return (
            <div className="view-item">
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{title}</h2>
                    </div>
                </header>
                {typeof context.description == "string" ? <p className="description">{context.description}</p> : null}
                <section className="view-detail panel">
                    <div className="container">
                        <pre>{JSON.stringify(context, null, 4)}</pre>
                    </div>
                </section>
            </div>
        );
    }
});


var Item = module.exports.Item = React.createClass({
    mixins: [AuditMixin],
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var title = globals.listing_titles.lookup(context)({context: context});
        var Panel = globals.panel_views.lookup(context);

        // Make string of alternate accessions
        var altacc = context.alternate_accessions ? context.alternate_accessions.join(', ') : undefined;

        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{title}</h2>
                        {altacc ? <h4 className="repl-acc">Replaces {altacc}</h4> : null}
                        <div className="status-line">
                            <AuditIndicators context={context} key="biosample-audit" />
                        </div>
                    </div>
                </header>
                <AuditDetail audits={context.audit} except={context['@id']} key="biosample-audit" />
                <div className="row item-row">
                    <div className="col-sm-12">
                        {context.description ? <p className="description">{context.description}</p> : null}
                    </div>
                    <Panel {...this.props} />
                </div>
            </div>
        );
    }
});

globals.content_views.register(Item, 'Item');


// Also use this view as a fallback for anything we haven't registered
globals.content_views.fallback = function () {
    return Fallback;
};


var Panel = module.exports.Panel = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-detail panel');
        return (
            <section className="col-sm-12">
                <div className={itemClass}>
                    <pre>{JSON.stringify(context, null, 4)}</pre>
                </div>
            </section>
        );
    }
});

globals.panel_views.register(Panel, 'Item');


// Also use this view as a fallback for anything we haven't registered
globals.panel_views.fallback = function () {
    return Panel;
};


var title = module.exports.title = function (props) {
    var context = props.context;
    return context.title || context.name || context.accession || context['@id'];
};

globals.listing_titles.register(title, 'Item');


// Also use this view as a fallback for anything we haven't registered
globals.listing_titles.fallback = function () {
    return title;
};


var ItemEdit = module.exports.ItemEdit = React.createClass({
    contextTypes: {
        navigate: React.PropTypes.func
    },

    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context, 'view-item');
        var title = globals.listing_titles.lookup(context)({context: context});
        var action, form, schemaUrl, type;
        if (context['@type'][0].indexOf('Collection') !== -1) {  // add form
            type = context['@type'][0].substr(0, context['@type'][0].length - 10);
            title = title + ': Add';
            action = context['@id'];
            form = (
                <fetched.FetchedData>
                    <fetched.Param name="schemas" url="/profiles/" />
                    <JSONSchemaForm type={type} action={action} method="POST" onFinish={this.finished}
                                    showReadOnly={false} />
                </fetched.FetchedData>
            );
        } else {  // edit form
            type = context['@type'][0];
            title = 'Edit ' + title;
            var id = this.props.context['@id'];
            var url = id + '?frame=edit';
            form = (
                <fetched.FetchedData>
                    <fetched.Param name="context" url={url} etagName="etag" />
                    <fetched.Param name="schemas" url="/profiles/" />
                    <JSONSchemaForm id={id} type={type} action={id} method="PUT" onFinish={this.finished} />
                </fetched.FetchedData>
            );
        }
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{title}</h2>
                    </div>
                </header>
                {form}
            </div>
        );
    },
    finished: function(data) {
      var url = data['@graph'][0]['@id'];
      this.context.navigate(url);
    }
});

globals.content_views.register(ItemEdit, 'Item', 'edit');
globals.content_views.register(ItemEdit, 'Collection', 'add');


var FetchedRelatedItems = React.createClass({
    getDefaultProps: function() {
        return {Component: Table};
    },

    render: function() {
        var {Component, context, title, url, ...props} = this.props;
        if (context === undefined) return null;
        var items = context['@graph'];
        if (!items || !items.length) return null;

        return (
            <Component {...props} title={title} context={context} total={context.total} items={items} url={url} showControls={false} />
        );
    },

});


var RelatedItems = module.exports.RelatedItems = React.createClass({
    getDefaultProps: function() {
        return {limit: 5};
    },

    render: function() {
        var url = globals.encodedURI(this.props.url + '&status!=deleted&status!=revoked&status!=replaced');
        var limited_url = url + '&limit=' + this.props.limit;
        var unlimited_url = url + '&limit=all';
        return (
            <fetched.FetchedData ignoreErrors={this.props.ignoreErrors}>
                <fetched.Param name="context" url={limited_url} />
                <FetchedRelatedItems {...this.props} url={unlimited_url} />
            </fetched.FetchedData>
        );
    },
});
