'use strict';
var React = require('react');
import createReactClass from 'create-react-class';
var globals = require('./globals');
var fetched = require('./fetched');


var Markdown = module.exports.Markdown = createReactClass({
    render: function() {
        var marked = require('marked');
        var html = marked(this.props.source, {sanitize: true});
        return <div dangerouslySetInnerHTML={{__html: html}} />;
    }
});


var ChangeLog = module.exports.ChangeLog = createReactClass({
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

var SchemaPage = module.exports.SchemaPage = createReactClass({
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
                        <pre>{JSON.stringify(context, null, 4)}</pre>
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
globals.content_views.register(SchemaPage, 'JSONSchema');
