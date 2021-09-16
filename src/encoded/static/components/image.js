import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import * as globals from './globals';


// Fixed-position lightbox background and image
const Lightbox = ({ lightboxVisible, clearLightbox, lightboxImg }) => {
    // Height of the image within the light box.
    const [imgHeight, setImgHeight] = React.useState(0);
    const lightbox = React.useRef(null);

    // Called when the window is resized to resize the image within it.
    const handleResize = () => {
        setImgHeight(lightbox.current.offsetHeight - 40);
    };

    // Called when a key is pressed to close the lightbox with ESC.
    const handleKeyDown = (e) => {
        if (e.keyCode === 27) {
            clearLightbox();
        }
    };

    React.useEffect(() => {
        // Need to resize and attach event handlers at mount.
        handleResize();
        window.addEventListener('resize', handleResize);
        return (() => {
            window.removeEventListener('resize', handleResize);
        });
    }, []);

    const lightboxClass = `lightbox${lightboxVisible ? ' active' : ''}`;
    return (
        <div tabIndex="-1" className={lightboxClass} onClick={clearLightbox} onKeyDown={handleKeyDown} role="button" aria-label="Close" ref={lightbox}>
            <div className="lightbox-img">
                <a aria-label="Open image" data-bypass="true" href={lightboxImg}>
                    <img src={lightboxImg} alt="Attachment from submitters" style={{ maxHeight: imgHeight }} />
                </a>
                <button type="button" className="lightbox-close" aria-label="Close" onClick={clearLightbox} />
            </div>
        </div>
    );
};

Lightbox.propTypes = {
    /** True if lightbox should be rendered or hidden initially */
    lightboxVisible: PropTypes.bool,
    /** Callback function to hide light box */
    clearLightbox: PropTypes.func.isRequired,
    /** URI of image to display in the light box */
    lightboxImg: PropTypes.string.isRequired,
};

Lightbox.defaultProps = {
    lightboxVisible: false,
};


export const Attachment = ({ context, attachment, className, showLink }) => {
    const [lightboxVisible, setLightboxVisible] = React.useState(false);

    // Handle a click on the lightbox trigger (thumbnail)
    const lightboxClickImage = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setLightboxVisible(true);
    };

    // Close the lightbox and image.
    const clearLightbox = () => {
        setLightboxVisible(false);
    };

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

            console.log(attachmentHref);

            // Display the attachment image in a light box.
            return (
                <div>
                    <div className="attachment">
                        <a className="attachment__button" data-bypass="true" href={attachmentHref} onClick={lightboxClickImage} title="View attachment in this window">
                            <div className="attachment__hover" />
                            <img className={imgClass} src={src} height={height} width={width} alt={alt} />
                        </a>
                    </div>
                    <Lightbox lightboxVisible={lightboxVisible} lightboxImg={attachmentHref} clearLightbox={clearLightbox} />
                </div>
            );
        }
        if (attachment.type === 'application/pdf') {
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
};

Attachment.propTypes = {
    /** Object within which the attachment is to be displayed */
    context: PropTypes.object.isRequired,
    /** Attachment object to display */
    attachment: PropTypes.object,
    /** CSS class name to add to image element; '-img' added to it */
    className: PropTypes.string,
    /** False to just display image preview without link or lightbox */
    showLink: PropTypes.bool,
};

Attachment.defaultProps = {
    attachment: null,
    className: '',
    showLink: true,
};


const Image = (props) => (
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
    const { award } = props;
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
