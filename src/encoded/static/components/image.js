/** @jsx React.DOM */
'use strict';
var React = require('react');
var cx = require('react/lib/cx');
var ReactForms = require('react-forms');
var ItemEdit = require('./item').ItemEdit;
var globals = require('./globals');
var url = require('url');


// Fixed-position lightbox background and image
var Lightbox = module.exports.Lightbox = React.createClass({
    ignoreClick: function(e) {
        e.preventDefault();
        e.stopPropagation();
    },

    render: function() {
        var lightboxVisible = this.props.lightboxVisible;
        var lightboxClass = cx({
            "lightbox": true,
            "active": lightboxVisible
        });

        return(
            <div className={lightboxClass} onClick={this.props.clearLightbox}>
                <div className="lightbox-img">
                    <img src={this.props.lightboxImg} onClick={this.ignoreClick} />
                    <i className="lightbox-close icon-remove-sign"></i>
                </div>
            </div>
        );
    }
});


var Attachment = module.exports.Attachment = React.createClass({
    // Handle a click on the lightbox trigger (thumbnail)
    lightboxClick: function(attachmentType, e) {
        if(attachmentType === 'image') {
            e.preventDefault();
            e.stopPropagation();
            this.setState({lightboxVisible: true});
        }
    },

    getInitialState: function() {
        return {lightboxVisible: false};
    },

    clearLightbox: function() {
        this.setState({lightboxVisible: false});
    },

    // If lightbox visible, ESC key closes it
    handleEscKey: function(e) {
        if(this.state.lightboxVisible && e.keyCode == 27) {
            this.clearLightbox();
        }
    },

    // Register for keyup events for ESC key
    componentDidMount: function() {
        window.addEventListener('keyup', this.handleEscKey);
    },

    // Unregister keyup events when component closes
    componentWillUnmount: function() {
        window.removeEventListener('keyup', this.handleEscKey);
    },

    render: function() {
        var context = this.props.context;
        var attachmentHref;
        var src, alt;
        var height = "100";
        var width = "100";
        if (context.attachment) {
            attachmentHref = url.resolve(context['@id'], context.attachment.href);
            var attachmentType = context.attachment.type.split('/', 1)[0];
            if (attachmentType == 'image') {
                var imgClass = this.props.className ? this.props.className + '-img' : '';
                src = attachmentHref;
                height = context.attachment.height;
                width = context.attachment.width;
                alt = "Attachment Image";
                return (
                    <div>
                        <a data-bypass="true" href={attachmentHref} onClick={this.lightboxClick.bind(this, attachmentType)}>
                            <img className={imgClass} src={src} alt={alt} />
                        </a>
                        <Lightbox lightboxVisible={this.state.lightboxVisible} lightboxImg={attachmentHref} clearLightbox={this.clearLightbox} />
                    </div>
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
});


globals.content_views.register(Image, 'image');


var FileInput = React.createClass({

    getInitialState: function() {
        return {
            value: this.props.value
        };
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
            };
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
