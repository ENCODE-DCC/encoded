'use strict';
var React = require('react');
var cx = require('react/lib/cx');
var globals = require('./globals');
var url = require('url');


// Fixed-position lightbox background and image
var Lightbox = module.exports.Lightbox = React.createClass({
    getInitialState: function() {
        return {imgHeight: 0};
    },

    // Window resized; set max-height of image
    handleResize: function() {
        this.setState({imgHeight: this.refs.lightbox.getDOMNode().offsetHeight - 40});
    },

    componentDidMount: function() {
        globals.bindEvent(window, 'resize', this.handleResize);
        this.setState({imgHeight: this.refs.lightbox.getDOMNode().offsetHeight - 40});
    },

    componentWillUnmount: function() {
        globals.unbindEvent(window, 'resize', this.handleResize);
    },

    render: function() {
        var lightboxVisible = this.props.lightboxVisible;
        var lightboxClass = cx({
            "lightbox": true,
            "active": lightboxVisible
        });
        var imgStyle = {maxHeight: this.state.imgHeight};

        return (
            <div className={lightboxClass} onClick={this.props.clearLightbox} aria-label="Close" ref="lightbox">
                <div className="lightbox-img">
                    <a aria-label="Open image" data-bypass="true" href={this.props.lightboxImg}>
                        <img src={this.props.lightboxImg} style={imgStyle} />
                    </a>
                    <button className="lightbox-close" aria-label="Close" onClick={this.clearLightbox}></button>
                </div>
            </div>
        );
    }
});


var Attachment = module.exports.Attachment = React.createClass({
    propTypes: {
        context: React.PropTypes.object.isRequired, // Object within which the attachment is to be displayed
        attachment: React.PropTypes.object, // Attachment object to display
        className: React.PropTypes.string, // CSS class name to add to image element; '-img' added to it
        show_link: React.PropTypes.bool // False to just display image preview without link or lightbox
    },

    // Handle a click on the lightbox trigger (thumbnail)
    lightboxClick: function(attachmentType, e) {
        if (attachmentType === 'image') {
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
        if (this.state.lightboxVisible && e.keyCode == 27) {
            this.clearLightbox();
        }
    },

    // Register for keyup events for ESC key
    componentDidMount: function() {
        globals.bindEvent(window, 'keyup', this.handleEscKey);
    },

    // Unregister keyup events when component closes
    componentWillUnmount: function() {
        globals.unbindEvent(window, 'keyup', this.handleEscKey);
    },

    render: function() {
        var {context, attachment, className, show_link} = this.props;
        var attachmentHref;
        var src, alt;
        var height = "100";
        var width = "100";
        if (attachment && attachment.href && attachment.type) {
            attachmentHref = url.resolve(context['@id'], attachment.href);
            var attachmentType = attachment.type.split('/', 1)[0];
            if (attachmentType == 'image' && attachment.type != 'image/tiff') {
                var imgClass = className ? className + '-img' : '';
                src = attachmentHref;
                height = attachment.height || 100;
                width = attachment.width || 100;
                alt = "Attachment Image";
                if (show_link === false) {
                    return <img className={imgClass} src={src} height={height} width={width} alt={alt} />;
                } else {
                    return (
                        <div>
                            <div className="attachment">
                                <a className="attachment-button" data-bypass="true" href={attachmentHref} onClick={this.lightboxClick.bind(this, attachmentType)}>
                                    <img className={imgClass} src={src} height={height} width={width} alt={alt} />
                                </a>
                            </div>
                            <Lightbox lightboxVisible={this.state.lightboxVisible} lightboxImg={attachmentHref} clearLightbox={this.clearLightbox} />
                        </div>
                    );
                }
            } else if (attachment.type == "application/pdf"){
                return (
                    <div className="attachment">
                        <a data-bypass="true" href={attachmentHref} className="attachment-button file-pdf">Attachment PDF Icon</a>
                    </div>
                );
            } else {
                return (
                    <div className="attachment">
                        <a data-bypass="true" href={attachmentHref} className="attachment-button file-generic">Attachment Icon</a>
                    </div>
                );
            }
        } else {
            return (
                <div className="attachment">
                    <div className="file-missing">Attachment file broken icon</div>
                </div>
            );
        }
    }
});


var Image = React.createClass({
    render: function() {
        return (
            <figure>
                <Attachment context={this.props.context} attachment={this.props.context.attachment} show_link={false} />
                <figcaption>{this.props.context.caption}</figcaption>
            </figure>
        );
    }
});


globals.content_views.register(Image, 'Image');


// Displays a graphic badge for the award project.
var ProjectBadge = module.exports.ProjectBadge = React.createClass({
    propTypes: {
        award: React.PropTypes.object.isRequired, // Award whose project's badge we display
        addClasses: React.PropTypes.string // Classes to add to image
    },

    projectMap: {
        'ENCODE': {
            imageClass: 'badge-encode',
            alt: 'ENCODE project'
        },
        'ENCODE2': {
            imageClass: 'badge-encode2',
            alt: 'ENCODE2 project'
        },
        'ENCODE3': {
            imageClass: 'badge-encode3',
            alt: 'ENCODE3 project'
        },
        'ENCODE4': {
            imageClass: 'badge-encode4',
            alt: 'ENCODE4 project'
        },
        'Roadmap': {
            imageClass: 'badge-roadmap',
            alt: 'Roadmap Epigenomics Mapping Consortium'
        },
        'modENCODE': {
            imageClass: 'badge-modencode',
            alt: 'modENCODE Project'
        },
        'modERN': {
            imageClass: 'badge-modern',
            alt: 'modERN project'
        },
        'GGR': {
            imageClass: 'badge-ggr',
            alt: 'Genomics of Gene Regulation Project'
        },
        'ENCODE2-Mouse': {
            imageClass: 'badge-mouseencode',
            alt: 'ENCODE Mouse Project'
        }
    },

    render: function() {
        var award = this.props.award;
        var project = award.rfa;
        var projectMeta = this.projectMap[project];
        var imageClass = projectMeta ? projectMeta.imageClass + (this.props.addClasses ? (' ' + this.props.addClasses) : '') : '';

        if (projectMeta) {
            return <div className={imageClass}><span className="sr-only">{projectMeta.alt}</span></div>;
        }
        return null;
    }
});
