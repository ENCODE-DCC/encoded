/** @jsx React.DOM */
'use strict';
var React = require('react');
var url = require('url');
var globals = require('./globals');


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


globals.content_views.register(Attachment, 'image');
