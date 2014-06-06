/** @jsx React.DOM */
'use strict';
var React = require('react');
var ReactForms = require('react-forms');
var ItemEdit = require('./item').ItemEdit;
var globals = require('./globals');
var url = require('url');


var Attachment = module.exports.Attachment = React.createClass({
    render: function() {
        var context = this.props.context;
        var attachmentHref, attachmentUri;
        var src, alt;
        var height = "100";
        var width = "100";
        if (context.attachment) {
            attachmentHref = url.resolve(context['@id'], context.attachment.href);
            if (context.attachment.type.split('/', 1)[0] == 'image') {
                var imgClass = this.props.className ? this.props.className + '-img' : '';
                src = attachmentHref;
                height = context.attachment.height;
                width = context.attachment.width;
                alt = "Attachment Image";
                return (
                    <a data-bypass="true" href={attachmentHref}>
                        <img className={imgClass} src={src} height={height} width={width} alt={alt} />
                    </a>
                );
            } else if (context.attachment.type == "application/pdf"){
                return (
                    <a data-bypass="true" href={attachmentHref} className="file-pdf text-hide">Attachment PDF Icon</a>
                );
            } else {
                return (
                    <a data-bypass="true" href={attachmentHref} className="file-generic text-hide">Attachment Icon</a>
                );
            }
        } else {
            return (
                <div className="file-missing text-hide">Attachment file broken icon</div>
            );
        }

    }
});


var Image = React.createClass({
    render: function() {
        return (
            <figure>
                {this.props.actions}
                <Attachment context={this.props.context} />
                <caption>{this.props.context.caption}</caption>
            </figure>
        );
    }
})


globals.content_views.register(Image, 'image');


var FileInput = React.createClass({

    getInitialState: function() {
        return {
            value: this.props.value
        }
    },

    componentWillReceiveProps: function(nextProps) {
        this.setState({value: nextProps.value});
    },

    render: function() {
        var mimetype = this.state.value.type;
        var preview = (mimetype && mimetype.indexOf('image/') === 0) ? <img src={this.state.value.href} width="128" /> : '';
        return (
            <div className="dropzone" onDragOver={this.onDragOver} onDrop={this.onDrop}>
                <div className="drop">Drop a file here.
                    <div>{preview}</div>
                </div>
                <div className="browse">Or <input ref="input" type="file" onChange={this.onChange} /></div>
            </div>
        );
    },

    onDragOver: function(e) {
        e.dataTransfer.dropEffect = 'copy';
        return false;  // indicate we are going to handle the drop
    },

    onDrop: function(e) {
        var file = e.dataTransfer.files[0];
        this.onChange(file);
        return false;
    },

    onChange: function(file) {
        if (file === undefined) {
            var input = this.refs.input.getDOMNode();
            file = input.files[0];
        }
        var reader = new FileReader();
        reader.onloadend = function() {
            var value = {
                download: file.name,
                type: file.type,
                href: reader.result
            }
            this.props.onChange(value);
        }.bind(this);
        if (file) {
            reader.readAsDataURL(file);
        }
    }
});


var Schema    = ReactForms.schema.Schema;
var Property  = ReactForms.schema.Property;

var ImageFormSchema = (
    <Schema>
        <Property name="caption" label="Caption" />
        <Property name="attachment" label="Image" input={FileInput()} />
    </Schema>
);


var ImageEdit = React.createClass({
    render: function() {
        return this.transferPropsTo(<ItemEdit context={this.props.context} schema={ImageFormSchema} />);
    }
});


globals.content_views.register(ImageEdit, 'image', 'edit');
globals.content_views.register(ImageEdit, 'image_collection', 'add');
