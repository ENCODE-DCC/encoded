import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import * as globals from './globals';


// Fixed-position lightbox background and image
class Lightbox extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = { imgHeight: 0 };

        // Bind this to non-React methods.
        this.handleResize = this.handleResize.bind(this);
    }

    componentDidMount() {
        globals.bindEvent(window, 'resize', this.handleResize);
        this.setState({ imgHeight: this.lightbox.offsetHeight - 40 });
    }

    componentWillUnmount() {
        globals.unbindEvent(window, 'resize', this.handleResize);
    }

    // Window resized; set max-height of image
    handleResize() {
        this.setState({ imgHeight: this.lightbox.offsetHeight - 40 });
    }

    render() {
        const lightboxVisible = this.props.lightboxVisible;
        const lightboxClass = `lightbox${lightboxVisible ? ' active' : ''}`;
        const imgStyle = { maxHeight: this.state.imgHeight };

        /* eslint-disable jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */
        return (
            <div className={lightboxClass} onClick={this.props.clearLightbox} aria-label="Close" ref={(div) => { this.lightbox = div; }}>
                <div className="lightbox-img">
                    <a aria-label="Open image" data-bypass="true" href={this.props.lightboxImg}>
                        <img src={this.props.lightboxImg} alt="Attachment from submitters" style={imgStyle} />
                    </a>
                    <button className="lightbox-close" aria-label="Close" onClick={this.clearLightbox} />
                </div>
            </div>
        );
        /* eslint-enable jsx-a11y/click-events-have-key-events, jsx-a11y/no-static-element-interactions */
    }
}

Lightbox.propTypes = {
    lightboxVisible: PropTypes.bool, // True if lightbox should be rendered or hidden initially
    clearLightbox: PropTypes.func.isRequired, // Callback function to hide light box
    lightboxImg: PropTypes.string.isRequired, // URI of image to display in the light box
};

Lightbox.defaultProps = {
    lightboxVisible: false,
};


export class Attachment extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = { lightboxVisible: false };

        // Bind this to non-React methods.
        this.lightboxClickImage = this.lightboxClickImage.bind(this);
        this.clearLightbox = this.clearLightbox.bind(this);
        this.handleEscKey = this.handleEscKey.bind(this);
    }

    // Register for keyup events for ESC key
    componentDidMount() {
        globals.bindEvent(window, 'keyup', this.handleEscKey);
    }

    // Unregister keyup events when component closes
    componentWillUnmount() {
        globals.unbindEvent(window, 'keyup', this.handleEscKey);
    }

    // Handle a click on the lightbox trigger (thumbnail)
    lightboxClickImage(e) {
        e.preventDefault();
        e.stopPropagation();
        this.setState({ lightboxVisible: true });
    }

    clearLightbox() {
        this.setState({ lightboxVisible: false });
    }

    // If lightbox visible, ESC key closes it
    handleEscKey(e) {
        if (this.state.lightboxVisible && e.keyCode === 27) {
            this.clearLightbox();
        }
    }

    render() {
        const { context, attachment, className, showLink } = this.props;
        let attachmentHref;
        let src;
        let alt;
        let height = '100';
        let width = '100';
        if (attachment && attachment.href && attachment.type) {
            attachmentHref = url.resolve(context['@id'], attachment.href);
            const attachmentType = attachment.type.split('/', 1)[0];
            if (attachmentType === 'image' && attachment.type !== 'image/tiff') {
                const imgClass = className ? `${className}-img` : '';
                src = attachmentHref;
                height = attachment.height || 100;
                width = attachment.width || 100;
                alt = 'Attachment from submitter';
                if (!showLink) {
                    // Just display the attachment image without any lightbox.
                    return <img className={imgClass} src={src} height={height} width={width} alt={alt} />;
                }

                // Display the attachment image in a light box.
                return (
                    <div>
                        <div className="attachment">
                            <a className="attachment__button" data-bypass="true" href={attachmentHref} onClick={this.lightboxClickImage} title="View attachment in this window">
                                <div className="attachment__hover" />
                                <img className={imgClass} src={src} height={height} width={width} alt={alt} />
                            </a>
                        </div>
                        <Lightbox lightboxVisible={this.state.lightboxVisible} lightboxImg={attachmentHref} clearLightbox={this.clearLightbox} />
                    </div>
                );
            } else if (attachment.type === 'application/pdf') {
                // Attachment is a PDF. Show the PDF icon, and clicks in it show the PDF in a new
                // window using the browser's PDF viewer.
                return (
                    <div className="attachment">
                        <a data-bypass="true" href={attachmentHref} className="attachment__button" target="_blank" rel="noopener noreferrer" title="Open attachment in a new window">
                            <div className="attachment__hover" />
                            <div className="file-pdf">Attachment PDF Icon</div>
                        </a>
                    </div>
                );
            }

            // Non image, non PDF attachment (likely a text file). Show the generic document icon
            // and open it in a new window.
            return (
                <div className="attachment">
                    <a data-bypass="true" href={attachmentHref} className="attachment__button" target="_blank" rel="noopener noreferrer" title="Open attachment in a new window">
                        <div className="attachment__hover" />
                        <div className="file-generic">Attachment Icon</div>
                    </a>
                </div>
            );
        }

        // No attachment given; display a broken file icon.
        return (
            <div className="attachment">
                <div className="attachment__button">
                    <div className="file-missing">Attachment file broken icon</div>
                </div>
            </div>
        );
    }
}

Attachment.propTypes = {
    context: PropTypes.object.isRequired, // Object within which the attachment is to be displayed
    attachment: PropTypes.object, // Attachment object to display
    className: PropTypes.string, // CSS class name to add to image element; '-img' added to it
    showLink: PropTypes.bool, // False to just display image preview without link or lightbox
};

Attachment.defaultProps = {
    attachment: null,
    className: '',
    showLink: true,
};


const Image = props => (
    <figure>
        <Attachment context={props.context} attachment={props.context.attachment} showLink={false} />
        <figcaption>{props.context.caption}</figcaption>
    </figure>
);

Image.propTypes = {
    context: PropTypes.object.isRequired, // Image object to display
};

globals.contentViews.register(Image, 'Image');


// Displays a graphic badge for the award project.
export const ProjectBadge = (props) => {
    const award = props.award;
    const project = award.rfa;
    const projectMeta = ProjectBadge.projectMap[project];
    const imageClass = projectMeta ? projectMeta.imageClass + (props.addClasses ? (` ${props.addClasses}`) : '') : '';

    if (projectMeta) {
        return <div className={imageClass}><span className="sr-only">{projectMeta.alt}</span></div>;
    }
    return null;
};

ProjectBadge.propTypes = {
    award: PropTypes.object.isRequired, // Award whose project's badge we display
    addClasses: PropTypes.string, // Classes to add to image
};

ProjectBadge.defaultProps = {
    addClasses: '',
};

ProjectBadge.projectMap = {
    ENCODE: {
        imageClass: 'badge-encode',
        alt: 'ENCODE project',
    },
    ENCODE2: {
        imageClass: 'badge-encode2',
        alt: 'ENCODE2 project',
    },
    ENCODE3: {
        imageClass: 'badge-encode3',
        alt: 'ENCODE3 project',
    },
    ENCODE4: {
        imageClass: 'badge-encode4',
        alt: 'ENCODE4 project',
    },
    Roadmap: {
        imageClass: 'badge-roadmap',
        alt: 'Roadmap Epigenomics Mapping Consortium',
    },
    modENCODE: {
        imageClass: 'badge-modencode',
        alt: 'modENCODE Project',
    },
    modERN: {
        imageClass: 'badge-modern',
        alt: 'modERN project',
    },
    GGR: {
        imageClass: 'badge-ggr',
        alt: 'Genomics of Gene Regulation Project',
    },
    'ENCODE2-Mouse': {
        imageClass: 'badge-mouseencode',
        alt: 'ENCODE Mouse Project',
    },
    community: {
        imageClass: 'badge-community',
        alt: 'Community submission',
    },
    ENCORE: {
        imageClass: 'badge-encore',
        alt: 'ENCORE project',
    },
};
