'use strict';
var React = require('react');
var globals = require('./globals');
var fetched = require('./fetched');


var Markdown = module.exports.Markdown = React.createClass({
    render: function() {
        var marked = require('marked');
        var html = marked(this.props.source, {sanitize: true});
        return <div dangerouslySetInnerHTML={{__html: html}} />;
    }
});


var ChangeLog = module.exports.ChangeLog = React.createClass({
    render: function() {
        return (
            <section className="view-detail panel">
                <div className="container">
                    <Markdown source={this.props.source} />
                </div>
            </section>
        );
    }
});


var Schema = module.exports.Schema = React.createClass({
    render: function() {
        var schema = this.props.schema;
        var required = schema.required || [];
        return <div>
            {schema.title && <header>{schema.title}</header>}
            {schema.type && <p>{JSON.stringify(schema.type)}</p>}
            {schema.description && <p>{schema.description}</p>}
            {schema.comment && <p><i>{schema.comment}</i></p>}
            {schema.properties &&
                <div>
                    <header>Properties</header>
                    {Object.keys(schema.properties).map(propname => {
                        var subschema = schema.properties[propname];
                        var proprequired = required.indexOf(propname) != -1;
                        return !subschema.calculatedProperty && <div className={proprequired ? 'required' : null}>
                            <header>{propname}</header>
                            <Schema schema={subschema} />
                        </div>;
                    })}
                </div>}
            {schema.items &&
                <div>
                    <header>Items</header>
                    <Schema schema={schema.items} />
                </div>}
        </div>;
    }
});


var SchemaPage = module.exports.SchemaPage = React.createClass({
    render: function() {
        var context = this.props.context;
        var itemClass = globals.itemClass(context);
        var title = context['title'];
        var changelog = context['changelog'];
        return (
            <div className={itemClass}>
                <header className="row">
                    <div className="col-sm-12">
                        <h2>{title}</h2>
                    </div>
                </header>
                {typeof context.description == "string" ? <p className="description">{context.description}</p> : null}
                <section className="view-detail panel">
                    <div className="container">
                        <Schema schema={context} />
                    </div>
                </section>
                {changelog && <fetched.FetchedData>
                    <fetched.Param name="source" url={changelog} type='text' />
                    <ChangeLog />
                </fetched.FetchedData>}
            </div>
        );
    }
});
globals.content_views.register(SchemaPage, 'jsonschema');
