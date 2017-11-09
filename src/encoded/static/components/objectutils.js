import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Modal, ModalHeader, ModalBody, ModalFooter } from '../libs/bootstrap/modal';
import * as globals from './globals';


// Display a summary sentence for a single treatment.
export function singleTreatment(treatment) {
    let treatmentText = '';

    if (treatment.amount) {
        treatmentText += `${treatment.amount}${treatment.amount_units ? ` ${treatment.amount_units}` : ''} `;
    }
    treatmentText += `${treatment.treatment_term_name}${treatment.treatment_term_id ? ` (${treatment.treatment_term_id})` : ''} `;
    if (treatment.duration) {
        treatmentText += `for ${treatment.duration} ${treatment.duration_units ? treatment.duration_units : ''}`;
    }
    return treatmentText;
}


// Display a treatment definition list.
export function treatmentDisplay(treatment) {
    const treatmentText = singleTreatment(treatment);
    return (
        <dl key={treatment.uuid} className="key-value">
            <div data-test="treatment">
                <dt>Treatment</dt>
                <dd>{treatmentText}</dd>
            </div>

            <div data-test="type">
                <dt>Type</dt>
                <dd>{treatment.treatment_type}</dd>
            </div>
        </dl>
    );
}


// Do a search of an arbitrary query string passed in the `query` parameter, and return a promise.
// If, for whatever reason, no results could be had, an empty object gets returned from the
// promise.
export function requestSearch(query) {
    return fetch(`/search/?${query}`, {
        method: 'GET',
        headers: {
            Accept: 'application/json',
        },
    }).then((response) => {
        // Convert the response to JSON.
        if (response.ok) {
            return response.json();
        }
        return Promise.resolve(null);
    }).then(responseJson => responseJson || {});
}


// Do a search of the specific objects whose @ids are listed in the `atIds` parameter. Because we
// have to specify the @id of each object in the URL of the GET request, the URL can get quite
// long, so if the number of `atIds` @ids goes beyond the `chunkSize` constant, we break thev
// searches into chunks, and the maximum number of @ids in each chunk is `chunkSize`. We
// then send out all the search GET requests at once, combine them into one array of
// files returned as a promise.
//
// You can also supply an array of objects in the filteringObjects parameter. Any file @ids in
// `atIds` that matches an object['@id'] in `filteringObjects` doesn't get included in the GET
// request.
//
// Note: this function calls `fetch`, so you can't call this function from code that runs on the
// server or it'll complain that `fetch` isn't defined. If called from a React component, make sure
// you only call it when you know the component is mounted, like from the componentDidMount method.
//
// atIds: array of file @ids.
// uri: Base URI specifying the type and statuses of the objects we want to get. The list of object
//      @ids gets added to this URI.
// filteringObjects: Array of files to filter out of the array of file @ids in the fileIds parameter.
export function requestObjects(atIds, uri, filteringObjects) {
    const chunkSize = 100; // Maximum # of files to search for at once
    const filteringFileIds = {}; // @ids of files we've searched for and don't need retrieval
    let filteredObjectIds = {}; // @ids of files we need to retrieve

    // Make a searchable object of file IDs for files to filter out of our list.
    if (filteringObjects && filteringObjects.length) {
        filteringObjects.forEach((filteringObject) => {
            filteringFileIds[filteringObject['@id']] = filteringObject;
        });

        // Filter the given file @ids to exclude those files we already have in data.@graph,
        // just so we don't use bandwidth getting things we already have.
        filteredObjectIds = atIds.filter(atId => !filteringFileIds[atId]);
    } else {
        // The caller didn't supply an array of files to filter out, so filtered files are just
        // all of them.
        filteredObjectIds = atIds;
    }

    // Break fileIds into an array of arrays of <= `chunkSize` @ids so we don't generate search
    // URLs that are too long for the server to handle.
    const objectChunks = [];
    for (let start = 0, chunkIndex = 0; start < filteredObjectIds.length; start += chunkSize, chunkIndex += 1) {
        objectChunks[chunkIndex] = filteredObjectIds.slice(start, start + chunkSize);
    }

    // Going to send out all search chunk GET requests at once, and then wait for all of them to
    // complete.
    return Promise.all(objectChunks.map((objectChunk) => {
        // Build URL containing file search for specific files for each chunk of files.
        const url = uri.concat(objectChunk.reduce((combined, current) => `${combined}&@id=${current}`, ''));
        return fetch(url, {
            method: 'GET',
            headers: {
                Accept: 'application/json',
            },
        }).then((response) => {
            // Convert each response response to JSON
            if (response.ok) {
                return response.json();
            }
            return Promise.resolve(null);
        });
    })).then((chunks) => {
        // All search chunks have resolved or errored. We get an array of search results in
        // `chunks` -- one per chunk. Now collect their files from their @graphs into one array of
        // files and return them as the promise result.
        if (chunks && chunks.length) {
            return chunks.reduce((objects, chunk) => (chunk && chunk['@graph'].length ? objects.concat(chunk['@graph']) : objects), []);
        }

        // Didn't get any good chucks back, so just return no results.
        return [];
    });
}


// Do a search of the specific files whose @ids are listed in the `fileIds` parameter.
//
// You can also supply an array of objects in the filteringFiles parameter. Any file @ids in
// `atIds` that matches an object['@id'] in `filteringFiles` doesn't get included in the GET
// request.
//
// Note: this function calls requestObjects which calls `fetch`, so you can't call this function
// from code that runs on the server or it'll complain that `fetch` isn't defined. If called from a
// React component, make sure you only call it when you know the component is mounted, like from
// the componentDidMount method.
//
// fileIds: array of file @ids.
// filteringFiles: Array of files to filter out of the array of file @ids in the fileIds parameter.
export function requestFiles(fileIds, filteringFiles) {
    return requestObjects(fileIds, '/search/?type=File&limit=all&status!=deleted&status!=revoked&status!=replaced', filteringFiles);
}


// Given a dataset (for now, only ReferenceEpigenome), return the donor diversity of that dataset.
export function donorDiversity(dataset) {
    let diversity = 'none';

    if (dataset.related_datasets && dataset.related_datasets.length) {
        // Get all non-deleted related experiments; empty array if none.
        const experiments = dataset.related_datasets.filter(experiment => experiment.status !== 'deleted');

        // From list list of non-deleted experiments, get all non-deleted replicates into one
        // array.
        if (experiments.length) {
            // Make an array of replicate arrays, one replicate array per experiment. Only include
            // non-deleted replicates.
            const replicatesByExperiment = experiments.map(experiment => (
                (experiment.replicates && experiment.replicates.length) ?
                    experiment.replicates.filter(replicate => replicate.status !== 'deleted')
                : []),
            );

            // Merge all replicate arrays into one non-deleted replicate array.
            const replicates = replicatesByExperiment.reduce((replicateCollection, replicatesForExperiment) => replicateCollection.concat(replicatesForExperiment), []);

            // Look at the donors in each replicate's biosample. If we see at least two different
            // donors, we know we have a composite. If only one unique donor after examining all
            // donors, we have a single. "None" if no donors found in all replicates.
            if (replicates.length) {
                const donorAtIdCollection = [];
                replicates.every((replicate) => {
                    if (replicate.library && replicate.library.status !== 'deleted' &&
                            replicate.library.biosample && replicate.library.biosample.status !== 'deleted' &&
                            replicate.library.biosample.donor && replicate.library.biosample.donor.status !== 'deleted') {
                        const donorAccession = replicate.library.biosample.donor.accession;

                        // If we haven't yet seen this donor @id, add it to our collection
                        if (donorAtIdCollection.indexOf(donorAccession) === -1) {
                            donorAtIdCollection.push(donorAccession);
                        }

                        // If we have two, we know have a composite, and we can exit the loop by
                        // returning false, which makes the replicates.every function end.
                        return donorAtIdCollection.length !== 2;
                    }

                    // No donor to examine in this replicate. Keep the `every` loop going.
                    return true;
                });

                // Now determine the donor diversity.
                if (donorAtIdCollection.length > 1) {
                    diversity = 'composite';
                } else if (donorAtIdCollection.length === 1) {
                    diversity = 'single';
                } // Else keep its original value of 'none'.
            }
        }
    }
    return diversity;
}


// Render the Download icon while allowing the hovering tooltip.
class DownloadIcon extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.onMouseEnter = this.onMouseEnter.bind(this);
        this.onMouseLeave = this.onMouseLeave.bind(this);
    }

    onMouseEnter() {
        this.props.hoverDL(true);
    }

    onMouseLeave() {
        this.props.hoverDL(false);
    }

    render() {
        const { file, adminUser } = this.props;

        return (
            <i className="icon icon-download" style={!file.restricted || adminUser ? {} : { opacity: '0.3' }} onMouseEnter={file.restricted ? this.onMouseEnter : null} onMouseLeave={file.restricted ? this.onMouseLeave : null}>
                <span className="sr-only">Download</span>
            </i>
        );
    }
}

DownloadIcon.propTypes = {
    hoverDL: PropTypes.func, // Function to call when hovering or stop hovering over the icon
    file: PropTypes.object, // File associated with this download button
    adminUser: PropTypes.bool, // True if logged-in user is an admin
};


// Render an accession as a button if clicking it sets a graph node, or just as text if not.
const FileAccessionButton = (props) => {
    const { file } = props;
    return <a href={file['@id']} title={`Go to page for ${file.title}`}>{file.title}</a>;
};

FileAccessionButton.propTypes = {
    file: PropTypes.object.isRequired, // File whose button is being rendered
};


// Display a button to open the file information modal.
class FileInfoButton extends React.Component {
    constructor() {
        super();

        // Bind this to non-React methods.
        this.onClick = this.onClick.bind(this);
    }

    onClick() {
        this.props.clickHandler(this.props.file);
    }

    render() {
        return (
            <button className="file-table-btn" onClick={this.onClick}>
                <i className="icon icon-info-circle">
                    <span className="sr-only">Open file information</span>
                </i>
            </button>
        );
    }
}

FileInfoButton.propTypes = {
    file: PropTypes.object.isRequired, // File whose information is to be displayed
    clickHandler: PropTypes.func, // Function to call when the info button is clicked
};


// Render a download button for a file that reacts to login state and admin status to render a
// tooltip about the restriction based on those things.
export class RestrictedDownloadButton extends React.Component {
    constructor() {
        super();

        // Set initial object variable values.
        this.timer = null;
        this.tipHovering = false;

        // Set initial React state.
        this.state = {
            tip: false, // True if tip is visible
        };

        // Bind this to non-React methods.
        this.hoverDL = this.hoverDL.bind(this);
        this.hoverTip = this.hoverTip.bind(this);
        this.hoverTipIn = this.hoverTipIn.bind(this);
        this.hoverTipOut = this.hoverTipOut.bind(this);
    }

    hoverDL(hovering) {
        if (hovering) {
            // Started hovering over the DL button; show the tooltip.
            this.setState({ tip: true });

            // If we happen to have a running timer, clear it so we don't clear the tooltip while
            // hovering over the DL button.
            if (this.timer) {
                clearTimeout(this.timer);
                this.timer = null;
            }
        } else {
            // No longer hovering over the DL button; start a timer that might hide the tooltip
            // after a second passes. It won't hide the tooltip if they're now hovering over the
            // tooltip itself.
            this.timer = setTimeout(() => {
                this.timer = null;
                if (!this.tipHovering) {
                    this.setState({ tip: false });
                }
            }, 1000);
        }
    }

    hoverTip(hovering) {
        if (hovering) {
            // Started hovering over the tooltip. This prevents the timer from hiding the tooltip.
            this.tipHovering = true;
        } else {
            // Stopped hovering over the tooltip. If the DL button hover time isn't running, hide
            // the tooltip here.
            this.tipHovering = false;
            if (!this.timer) {
                this.setState({ tip: false });
            }
        }
    }

    hoverTipIn() {
        this.hoverTip(true);
    }

    hoverTipOut() {
        this.hoverTip(false);
    }

    render() {
        const { file, adminUser } = this.props;
        const tooltipOpenClass = this.state.tip ? ' tooltip-open' : '';
        const buttonEnabled = !file.restricted || adminUser;

        // If the user provided us with a component for downloading files, add the download
        // properties to the component before rendering.
        const downloadComponent = this.props.downloadComponent ? React.cloneElement(this.props.downloadComponent, {
            file,
            href: file.href,
            download: file.href.substr(file.href.lastIndexOf('/') + 1),
            hoverDL: this.hoverDL,
            adminUser,
            buttonEnabled,
        }) : null;

        // Supply a default icon for the user to click to download, if the caller didn't supply one
        // in downloadComponent.
        const icon = (!downloadComponent ? <DownloadIcon file={file} adminUser={adminUser} hoverDL={this.hoverDL} /> : null);

        return (
            <div className="dl-tooltip-trigger">
                {buttonEnabled ?
                    <span>
                        {downloadComponent ?
                            <span>{downloadComponent}</span>
                        :
                            <a href={file.href} download={file.href.substr(file.href.lastIndexOf('/') + 1)} data-bypass="true">
                                {icon}
                            </a>
                        }
                    </span>
                :
                    <span>
                        {downloadComponent ?
                            <span>{downloadComponent}</span>
                        :
                            <span>{icon}</span>
                        }
                    </span>
                }
                {file.restricted ?
                    <div className={`tooltip right${tooltipOpenClass}`} role="tooltip" onMouseEnter={this.hoverTipIn} onMouseLeave={this.hoverTipOut}>
                        <div className="tooltip-arrow" />
                        <div className="tooltip-inner">
                            If you are a collaborator or owner of this file,<br />
                            please contact <a href="mailto:encode-help@lists.stanford.edu">encode-help@lists.stanford.edu</a><br />
                            to receive a copy of this file
                        </div>
                    </div>
                : null}
            </div>
        );
    }
}

RestrictedDownloadButton.propTypes = {
    file: PropTypes.object, // File containing `href` to use as download link
    adminUser: PropTypes.bool, // True if logged in user is admin
    downloadComponent: PropTypes.object, // Optional component to render the download button, insetad of default
};


export const DownloadableAccession = (props) => {
    const { file, clickHandler, loggedIn, adminUser } = props;
    return (
        <span className="file-table-accession">
            <FileAccessionButton file={file} />
            {clickHandler ? <FileInfoButton file={file} clickHandler={clickHandler} /> : null}
            <RestrictedDownloadButton file={file} loggedIn={loggedIn} adminUser={adminUser} />
        </span>
    );
};

DownloadableAccession.propTypes = {
    file: PropTypes.object.isRequired, // File whose accession to render
    buttonEnabled: PropTypes.bool, // True if accession should be a button
    clickHandler: PropTypes.func, // Function to call when button is clicked
    loggedIn: PropTypes.bool, // True if current user is logged in
    adminUser: PropTypes.bool, // True if current user is logged in and admin
};


// Return `true` if the given dataset is viewable by people not logged in, or people logged in
// but not as admin.
export function publicDataset(dataset) {
    return dataset.status === 'released' || dataset.status === 'archived' || dataset.status === 'revoked';
}


// Display a Visualize button that brings up a modal that lets you choose an assembly and a browser
// in which to display the visualization.
export class BrowserSelector extends React.Component {
    constructor() {
        super();

        // Set initial React state.
        this.state = { selectorOpen: false };
        this.openModal = this.openModal.bind(this);
        this.closeModal = this.closeModal.bind(this);
        this.handleClick = this.handleClick.bind(this);
    }

    // Called to open the browser-selection modal.
    openModal() {
        this.setState({ selectorOpen: true });
    }

    // Called to close the browser-seletino modal.
    closeModal() {
        this.setState({ selectorOpen: false });
    }

    // When the link to open a browser gets clicked, this gets called to close the modal in
    // addition to going to the link.
    handleClick() {
        this.closeModal();
    }

    render() {
        const { visualizeCfg, disabled, title } = this.props;
        const assemblyList = _(Object.keys(visualizeCfg)).sortBy(assembly => _(globals.assemblyPriority).indexOf(assembly));

        return (
            <div className="browser-selector__actuator">
                <button onClick={this.openModal} disabled={disabled} className="btn btn-info btn-sm" >{title ? <span>{title}</span> : <span>Visualize</span>}</button>
                {this.state.selectorOpen ?
                    <Modal closeModal={this.closeModal} addClasses="browser-selector__modal">
                        <ModalHeader title="Open visualization browser" closeModal={this.closeModal} />
                        <ModalBody>
                            <div className="browser-selector">
                                <div className="browser-selector__inner">
                                    <div className="browser-selector__title">
                                        <div className="browser-selector__assembly-title">
                                            Assembly
                                        </div>
                                        <div className="browser-selector__browsers-title">
                                            Visualize with browser…
                                        </div>
                                    </div>
                                    <hr />
                                    {assemblyList.map((assembly) => {
                                        const assemblyBrowsers = visualizeCfg[assembly];
                                        const browserList = _(Object.keys(assemblyBrowsers)).sortBy(browser => _(globals.browserPriority).indexOf(browser));

                                        return (
                                            <div key={assembly} className="browser-selector__assembly-option">
                                                <div className="browser-selector__assembly">
                                                    {assembly}:
                                                </div>
                                                <div className="browser-selector__browsers">
                                                    {browserList.map(browser =>
                                                        <div key={browser} className="browser-selector__browser">
                                                            <a href={assemblyBrowsers[browser]} onClick={this.handleClick} rel="noopener noreferrer" target="_blank">
                                                                {browser}
                                                                {browser === 'Quick View' ? <span className="beta-badge">BETA</span> : null}
                                                            </a>
                                                        </div>
                                                    )}
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </ModalBody>
                        <ModalFooter closeModal={<button className="btn btn-info" onClick={this.closeModal}>Close</button>} />
                    </Modal>
                : null}
            </div>
        );
    }
}

BrowserSelector.propTypes = {
    visualizeCfg: PropTypes.object.isRequired, // Assemblies, browsers, and browser URLs; visualize and visualize_batch contents
    disabled: PropTypes.bool, // `true` if button should be disabled; usually because more search results than we can handle
    title: PropTypes.string, // Title of Visualize button if "Visualize" isn't desired
};


// You can use this function to render a panel view for a context object with a couple options:
//   1. Pass an ENCODE context object (e.g. Biosample or Experiment) directly in props. PanelLookup
//      returns a React component that you can render directly.
//
//   2. Pass an object of the form:
//      {
//          context: context object to render
//          ...any other props you want to pass to the panel-rendering component
//      }
//
// Note: this function really doesn't do much of value, but it does do something and it's been
// around since the beginning of encoded, so it stays for now.

export function PanelLookup(properties) {
    let localProps;
    if (properties['@id']) {
        // `properties` is an ENCODE context object, so normalize it by making `props` an object
        // with the given context as an object property.
        localProps = { context: properties };
    } else {
        localProps = properties;
    }

    // `props` is an object with at least { context: ENCODE context object }.
    const PanelView = globals.panelViews.lookup(localProps.context);
    return <PanelView key={localProps.context.uuid} {...localProps} />;
}


// Display the alternate accessions, normally below the header line in objects.
export const AlternateAccession = (props) => {
    const { altAcc } = props;

    if (altAcc && altAcc.length) {
        return (
            <h4 className="repl-acc">
                {altAcc.length === 1 ?
                    <span>Alternate accession: {altAcc[0]}</span>
                :
                    <span>Alternate accessions: {altAcc.join(', ')}</span>
                }
            </h4>
        );
    }

    // No alternate accessions to display.
    return null;
};

AlternateAccession.propTypes = {
    altAcc: PropTypes.array, // Array of alternate accession strings
};
