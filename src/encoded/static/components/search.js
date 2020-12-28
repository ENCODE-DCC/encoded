import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import url from 'url';
import { Panel, PanelBody } from '../libs/ui/panel';
import QueryString from '../libs/query_string';
import { auditDecor } from './audit';
import { CartToggle, CartSearchControls } from './cart';
import FacetRegistry from './facets';
import * as globals from './globals';
import {
    DisplayAsJson,
    BiosampleType,
    requestSearch,
    DocTypeTitle,
    singleTreatment,
} from './objectutils';
import { DbxrefList } from './dbxref';
import Status from './status';
import { BiosampleSummaryString, BiosampleOrganismNames } from './typeutils';
import { BatchDownloadControls, ViewControls } from './view_controls';
import { BrowserSelector } from './vis_defines';


// Should really be singular...
const types = {
    patient: { title: 'Patients' },
    surgery: { title: 'Surgery and Pathology Reports' },
    annotation: { title: 'Annotation file set' },
    biospecimen: { title: 'Biospecimens' },
    // bioexperiment: { title: 'Bioexperiments' },
    // bioseries: { title: 'Series File set' },
    // biofileSet: { title: 'File set' },
    // bioexperimentSeries: { title: 'Experiment Series'},
    biodataset: { title: 'Biodatasets' },
    bioexperiment: { title: 'Bioexperiments' },
    bioseries: { title: 'Bioserieses' },
    biofileSet: { title: 'BiofileSets' },
    bioexperimentSeries:{title:'BioexperimentSereieses'},
    image: { title: 'Images' },
    publication: { title: 'Publications' },
    page: { title: 'Web page' },
    bioproject: { title: 'Project file set' },
    publication_data: { title: 'Publication file set' },
    bioreference: { title: 'Reference file set' },
};

const datasetTypes = {
};

const biodatasetTypes = {
    Biodataset: types.biodataset.title,
    Bioproject: types.bioproject.title,
    Bioreference: types.bioreference.title,
    Bioseries: types.bioseries.title,
    BiofileSet: types.biofileSet.title,
    BioexperimentSeries:types.bioexperimentSeries.title

}

const getUniqueTreatments = treatments => _.uniq(treatments.map(treatment => singleTreatment(treatment)));

// session storage used to preserve opened/closed facets
const FACET_STORAGE = 'FACET_STORAGE';

// marker for determining user just opened the page
const MARKER_FOR_NEWLY_LOADED_FACET_PREFIX = 'MARKER_FOR_NEWLY_LOADED_FACETS_';

/**
 * Maximum  downloadable result count
 */
const MAX_DOWNLOADABLE_RESULT = 500;

// You can use this function to render a listing view for the search results object with a couple
// options:
//   1. Pass a search results object directly in props. listing returns a React component that you
//      can render directly.
//
//   2. Pass an object of the form:
//      {
//          context: context object to render
//          ...any other props you want to pass to the panel-rendering component
//      }
//
// Note: this function really doesn't do much of value, but it does do something and it's been
// around since the beginning of encoded, so it stays for now.

export function Listing(reactProps) {
    // XXX not all panels have the same markup
    let context;
    let viewProps = reactProps;
    if (reactProps['@id']) {
        context = reactProps;
        viewProps = { context, key: context['@id'] };
    }
    const ListingView = globals.listingViews.lookup(viewProps.context);
    return <ListingView {...viewProps} />;
}


/**
 * Generate a CSS class for the <li> of a search result table item.
 * @param {object} item Displayed search result object
 *
 * @return {string} CSS class for this type of object
 */
export const resultItemClass = item => `result-item--type-${item['@type'][0]}`;

export const PickerActions = ({ context }, reactContext) => {
    if (reactContext.actions && reactContext.actions.length > 0) {
        return (
            <div className="result-item__picker">
                {reactContext.actions.map(action => React.cloneElement(action, { key: context.name, id: context['@id'] }))}
            </div>
        );
    }

    // No actions; don't render anything.
    return null;
};

PickerActions.propTypes = {
    context: PropTypes.object.isRequired,
};

PickerActions.contextTypes = {
    actions: PropTypes.array,
};


const ItemComponent = ({ context: result, auditIndicators, auditDetail }, reactContext) => {
    const title = globals.listingTitles.lookup(result)({ context: result });
    const itemType = result['@type'][0];
    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">{title}</a>
                    <div className="result-item__data-row">
                        {result.description}
                    </div>
                </div>
                {result.accession ?
                    <div className="result-item__meta">
                        <div className="result-item__meta-title">{itemType}: {` ${result.accession}`}</div>
                        {auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
                    </div>
                : null}
                <PickerActions context={result} />
            </div>
            {auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, except: result['@id'], forcedEditLink: true })}
        </li>
    );
};

ItemComponent.propTypes = {
    context: PropTypes.object.isRequired, // Component to render in a listing view
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

ItemComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Item = auditDecor(ItemComponent);

globals.listingViews.register(Item, 'Item');

/* eslint-disable react/prefer-stateless-function */
const TargetComponent = ({ context: result, auditIndicators, auditDetail }, reactContext) => (
    <li className={resultItemClass(result)}>
        <div className="result-item">
            <div className="result-item__data">
                <a href={result['@id']} className="result-item__link">
                    {result.label} ({result.organism && result.organism.scientific_name ? <i>{result.organism.scientific_name}</i> : <span>{result.investigated_as[0]}</span>})
                </a>
                <div className="result-item__target-external-resources">
                    <p>External resources:</p>
                    {result.dbxrefs && result.dbxrefs.length > 0 ?
                        <DbxrefList context={result} dbxrefs={result.dbxrefs} />
                    : <em>None submitted</em> }
                </div>
            </div>
            <div className="result-item__meta">
                <div className="result-item__meta-title">Target</div>
                {auditIndicators(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, search: true })}
            </div>
            <PickerActions context={result} />
        </div>
        {auditDetail(result.audit, result['@id'], { session: reactContext.session, sessionProperties: reactContext.session_properties, except: result['@id'], forcedEditLink: true })}
    </li>
);

TargetComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

TargetComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
    session_properties: PropTypes.object,
};

const Target = auditDecor(TargetComponent);

globals.listingViews.register(Target, 'Target');


/* eslint-disable react/prefer-stateless-function */
class PatientComponent extends React.Component {
    render() {
        const { cartControls } = this.props;
        const result = this.props.context;
        let age = result.diagnosis.age;
        const hasAge = (age != "Unknown") ? true : false;
        const ageUnit = (result.diagnosis.age_unit && hasAge && age != "90 or above") ? ` ${result.diagnosis.age_unit}` : '';

        return (
            <li className={resultItemClass(result)}>
                <div className="result-item">
                    <div className="result-item__data">
                        <a href={result['@id']} className="result-item__link">
                            {`${result.accession}`}
                            {hasAge && `(${age}${ageUnit})`}
                        </a>
                        <div className="result-item__data-row">
                            <div><strong>Sex: </strong>{result.sex}</div>
                            <div><strong>Ethnicity: </strong>{result.ethnicity}</div>
                            <div><strong>Race: </strong>{result.race}</div>
                        </div>
                    </div>
                    <div className="result-item__meta">
                        <div className="result-item__meta-title">Patient</div>
                        <div className="result-item__meta-id">{` ${result.accession}`}</div>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}

                    </div>
                    <PickerActions {...this.props} />
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

PatientComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    cartControls: PropTypes.bool, // True if displayed in active cart
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

PatientComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Patient = auditDecor(PatientComponent);

globals.listingViews.register(Patient, 'Patient');

class PathologyComponent extends React.Component {
    render() {
        const result = this.props.context;

        return (
            <li className={resultItemClass(result)}>
                <div className="result-item">
                    <div className="result-item__data">
                        <a href={result['@id']} className="result-item__link">
                            {`${result.accession} `}
                        </a>
                        <div className="result-item__data-row">
                            <div><strong>Tumor Size Range:</strong>{result.tumor_size}{result.tumor_size_units}</div>
                            <div><strong>Histologic Subtype: </strong>{result.histology}</div>
                            <div><strong>Tumor Grade: </strong>{result.grade}</div>
                            <div><strong>pT stage: </strong>{result.ajcc_p_stage}</div>
                            <div><strong>AJCC TNM Stage: </strong>{result.ajcc_tnm_stage}</div>
                            <div><strong>Laterality: </strong>{result.laterality}</div>
                        </div>
                    </div>
                    <div className="result-item__meta">
                        <div className="result-item__meta-title">Pathology Report</div>
                        <div className="result-item__meta-id">{` ${result.accession}`}</div>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <PickerActions {...this.props} />    
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

PathologyComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

PathologyComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const PathologyReport = auditDecor(PathologyComponent);

globals.listingViews.register(PathologyReport, 'PathologyReport');

class SurgeryComponent extends React.Component {
    render() {
        const result = this.props.context;
        const surgeryProcedure = result.surgery_procedure;
        let type1 = [];
        for (let i = 0; i < surgeryProcedure.length; i++) {
            type1.push(<div><strong>Surgery Procedure: </strong>{surgeryProcedure[i].procedure_type}</div>);
        }
        return (
            < li className={resultItemClass(result)}>
                <div className="result-item">
                    <div className="result-item__data">
                        <a href={result['@id']} className="result-item__link">
                            {`${result.accession} `}
                        </a>
                        <div className="result-item__data-row">
                            <div><strong>Surgery Date: </strong>{result.date}</div>
                            <div><strong>Hospital Location: </strong>{result.hospital_location} </div>
                            {type1}
                        </div>
                    </div>
                    <div className="result-item__meta">
                        <div className="result-item__meta-title">Surgery</div>
                        <div className="result-item__meta-id">{` ${result.accession}`}</div>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <PickerActions {...this.props} />
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li >
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

SurgeryComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

SurgeryComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Surgery = auditDecor(SurgeryComponent);

globals.listingViews.register(Surgery, 'Surgery');

/* eslint-disable react/prefer-stateless-function */
class BiofileComponent extends React.Component {
    render() {
        const result = this.props.context;
        return (
            <li>
                <div className="clearfix">
                    <PickerActions {...this.props} />
                    <div className="pull-right search-meta">
                        <p className="type meta-title">Biofile</p>
                        <p className="type">{` ${result.accession}`}</p>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}
                    </div>
                    <div className="accession">
                        <a href={result['@id']}>
                            {`${result.accession} `}

                        </a>
                    </div>
                    <div className="data-row">
                        <div><strong>File format: </strong>{result.file_format}</div>
                        <div><strong>Output type: </strong>{result.output_type}</div>
                    </div>
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }
}
/* eslint-enable react/prefer-stateless-function */

BiofileComponent.propTypes = {
    context: PropTypes.object.isRequired, // Target search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BiofileComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Biofile = auditDecor(BiofileComponent);

globals.listingViews.register(Biofile, 'Biofile');

/* eslint-disable react/prefer-stateless-function */
class BiospecimenComponent extends React.Component {
    render() {
        const result = this.props.context;
        const tissueType = (result.tissue_type && result.sample_type == 'Tissue') ? ` ${result.tissue_type}` : '';
        const anatomicSite = (result.anatomic_site && result.sample_type == 'Tissue') ? ` ${result.anatomic_site}` : '';

        return (
            <li className={resultItemClass(result)}>
                <div className="result-item">
                    <div className="result-item__data">
                        <a href={result['@id']} className="result-item__link">
                            {`${result.accession} `}
                        </a>
                        <div className="result-item__data-row">
                            <div><strong>Sample type: </strong>{result.sample_type}</div>
                            <div><strong>Tissue derivatives: </strong>{result.tissue_derivatives}</div>
                            <div><strong>Tissue type: </strong>{result.tissue_type}</div>
                            <div><strong>Anatomic site: </strong>{result.anatomic_site}</div>
                        </div>
                    </div>
                    <div className="result-item__meta">
                        <div className="result-item__meta-title">Biospecimen</div>
                        <div className="result-item__meta-id">{` ${result.accession}`}</div>
                        <Status item={result.status} badgeSize="small" css="result-table__status" />
                        {this.props.auditIndicators(result.audit, result['@id'], { session: this.context.session, search: true })}

                    </div>
                    <PickerActions {...this.props} />
                    
                </div>
                {this.props.auditDetail(result.audit, result['@id'], { session: this.context.session, except: result['@id'], forcedEditLink: true })}
            </li>
        );
    }

}
/* eslint-enable react/prefer-stateless-function */

BiospecimenComponent.propTypes = {
    context: PropTypes.object.isRequired, // Biosample search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BiospecimenComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Biospecimen = auditDecor(BiospecimenComponent);

globals.listingViews.register(Biospecimen, 'Biospecimen');

const Image = (props) => {
    const result = props.context;

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">{result['@id']}</a>
                    <div className="attachment">
                        <div className="file-thumbnail">
                            <img src={result.thumb_nail} alt="thumbnail" />
                        </div>
                    </div>
                    {result.caption}
                </div>
                <div className="result-item__meta">
                    <p className="type meta-title">Image</p>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                </div>
                <PickerActions context={result} />
            </div>
        </li>
    );
};

Image.propTypes = {
    context: PropTypes.object.isRequired, // Image search results
};

globals.listingViews.register(Image, 'Image');



const BioexperimentComponent = (props, reactContext) => {
    const { cartControls } = props;
    const result = props.context;

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
                            {result.assay_term_name ?
                                <span>{result.assay_term_name}</span> : null
                            }
                    </a>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">Bioexperiment</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, search: true })}
                </div>
                {cartControls ?
                    <div className="result-item__cart-control">
                        <CartToggle element={result} />
                    </div>
                : null}
                <PickerActions {...props} />
            </div>
            { props.auditDetail(result.audit, result['@id'], { session: reactContext.session, except: result['@id'], forcedEditLink: true }) }
        </li >
    );
};

BioexperimentComponent.propTypes = {
    context: PropTypes.object.isRequired, // Experiment search results
    cartControls: PropTypes.bool, // True if displayed in active cart
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired,
};

BioexperimentComponent.defaultProps = {
    cartControls: false,
};

BioexperimentComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Bioexperiment = auditDecor(BioexperimentComponent);

globals.listingViews.register(Bioexperiment, 'Bioexperiment');

const BiodatasetComponent = (props, reactContext) => {
    const result = props.context;
    let biosampleTerm;

    // Determine whether the dataset is a series or not
    const seriesDataset = result['@type'].indexOf('Bioseries') >= 0;
console.log("seriesDataset", seriesDataset);
    // Get the biosample info for Series types if any. Can be string or array. If array, only use iff 1 term name exists
    if (seriesDataset) {
        biosampleTerm = (result.assay_term_name) ? result.assay_term_name : '';
        // biosampleTerm = (result.biospecimen && Array.isArray(result.biospecimen) && result.biospecimen.length === 1 && result.biospecimen[0].sample_type) ? result.biospecimen[0].sample_type : ((result.biospecimen && result.biospecimen.sample_type) ? result.biospecimen.sample_type : '');


    }

    const haveSeries = result['@type'].indexOf('Bioseries') >= 0;
    const haveFileSet = result['@type'].indexOf('BiofileSet') >= 0;
    console.log("haveSeries", result['@type'].indexOf('Bioseries'));

    return (
        <li className={resultItemClass(result)}>
            <div className="result-item">
                <div className="result-item__data">
                    <a href={result['@id']} className="result-item__link">
                            {biodatasetTypes[result['@type'][0]]}
                            {seriesDataset ?
                                <span>
                                    {biosampleTerm ? <span>{` in ${biosampleTerm}`}</span> : null}

                                </span>
                                :
                                <span>{result.description ? <span>{`: ${result.description}`}</span> : null}</span>
                            }
                    </a>
                </div>
                <div className="result-item__meta">
                    <div className="result-item__meta-title">{haveSeries ? 'Bioseries' : (haveFileSet ? 'BiofileSet' : 'Biodataset')}</div>
                    <div className="result-item__meta-id">{` ${result.accession}`}</div>
                    <Status item={result.status} badgeSize="small" css="result-table__status" />
                    {props.auditIndicators(result.audit, result['@id'], { session: reactContext.session, search: true })}
                </div>
                <PickerActions {...props} />
            </div>
            {props.auditDetail(result.audit, result['@id'], { session: reactContext.session, except: result['@id'], forcedEditLink: true })}
        </li>
    );
};

BiodatasetComponent.propTypes = {
    context: PropTypes.object.isRequired, // Dataset search results
    auditIndicators: PropTypes.func.isRequired, // Audit decorator function
    auditDetail: PropTypes.func.isRequired, // Audit decorator function
};

BiodatasetComponent.contextTypes = {
    session: PropTypes.object, // Login information from <App>
};

const Biodataset = auditDecor(BiodatasetComponent);

globals.listingViews.register(Biodataset, 'Biodataset');

/**
 * Entry field for filtering the results list when search results appear in edit forms.
 *
 * @export
 * @class TextFilter
 * @extends {React.Component}
 */
export class TextFilter extends React.Component {
    constructor() {
        super();

        // Bind `this` to non-React component methods.
        this.performSearch = this.performSearch.bind(this);
        this.onKeyDown = this.onKeyDown.bind(this);
    }

    /**
    * Keydown event handler
    *
    * @param {object} e Key down event
    * @memberof TextFilter
    * @private
    */
    onKeyDown(e) {
        if (e.keyCode === 13) {
            this.performSearch(e);
            e.preventDefault();
        }
    }

    getValue() {
        const filter = this.props.filters.filter(f => f.field === 'searchTerm');
        return filter.length > 0 ? filter[0].term : '';
    }

    /**
    * Makes call to do search
    *
    * @param {object} e Event
    * @memberof TextFilter
    * @private
    */
    performSearch(e) {
        let searchStr = this.props.searchBase.replace(/&?searchTerm=[^&]*/, '');
        const value = e.target.value;
        if (value) {
            searchStr += `searchTerm=${e.target.value}`;
        } else {
            searchStr = searchStr.substring(0, searchStr.length - 1);
        }
        this.props.onChange(searchStr);
    }

    shouldUpdateComponent(nextProps) {
        return (this.getValue(this.props) !== this.getValue(nextProps));
    }

    /**
    * Provides view for @see {@link TextFilter}
    *
    * @returns {object} @see {@link TextFilter} React's JSX object
    * @memberof TextFilter
    * @public
    */
    render() {
        return (
            <div className="facet">
                <input
                    type="search"
                    className="search-query"
                    placeholder="Enter search term(s)"
                    defaultValue={this.getValue(this.props)}
                    onKeyDown={this.onKeyDown}
                    data-test="filter-search-box"
                />
            </div>
        );
    }
}

TextFilter.propTypes = {
    filters: PropTypes.array.isRequired,
    searchBase: PropTypes.string.isRequired,
    onChange: PropTypes.func.isRequired,
};


// Displays the entire list of facets. It contains a number of <Facet> components.
export const FacetList = (props) => {
    const { context, facets, filters, mode, orientation, hideTextFilter, addClasses, docTypeTitleSuffix, supressTitle, onFilter, isExpandable } = props;

    const [expandedFacets, setExpandFacets] = React.useState(new Set());

    // Get facets from storage that need to be expanded
    React.useEffect(() => {
        const facetsStorage = sessionStorage.getItem(FACET_STORAGE);
        const facetList = new Set(facetsStorage ? facetsStorage.split(',') : []);

        sessionStorage.setItem(FACET_STORAGE, facetList.size !== 0 ? [...facetList].join(',') : []);
        setExpandFacets(facetList); // initalize facet collapse-state
    }, []);

    // Only on initialize load, get facets from facet-section and schema that need to be expanded
    React.useEffect(() => {
        const facetsStorage = sessionStorage.getItem(FACET_STORAGE);
        const facetList = new Set(facetsStorage ? facetsStorage.split(',') : []);

        facets.forEach((facet) => {
            const field = facet.field;
            const newlyLoadedFacetStorage = `${MARKER_FOR_NEWLY_LOADED_FACET_PREFIX}${field}`;
            const isFacetNewlyLoaded = sessionStorage.getItem(newlyLoadedFacetStorage);

            const relevantFilters = context && context.filters.filter(filter => (
                filter.field === facet.field || filter.field === `${facet.field}!`
            ));

            // auto-open facets based on selected terms (see url) or it set in the schema (open_on_load)
            if (!isFacetNewlyLoaded && ((relevantFilters && relevantFilters.length > 0) || facet.open_on_load === true)) {
                sessionStorage.setItem(newlyLoadedFacetStorage, field); // ensure this is not called again on this active session storage
                facetList.add(facet.field);
            }
        });

        sessionStorage.setItem(FACET_STORAGE, facetList.size !== 0 ? [...facetList].join(',') : []);
        setExpandFacets(facetList); // initalize facet collapse-state
    }, [context, facets]);

    if (facets.length === 0 && mode !== 'picker') {
        return <div />;
    }

    const parsedUrl = context && context['@id'] && url.parse(context['@id']);

    /**
     * Handlers opening or closing a tab
     *
     * @param {event} e React synthetic event
     * @param {bool} status True for open, false for closed
     * @param {string} field Tab name
     */
    const handleExpanderClick = (e, status, field) => {
        let facetList = null;

        if (e.altKey) {
            // user has held down option-key (alt-key in Windows and Linux)
            sessionStorage.removeItem(FACET_STORAGE);
            facetList = new Set(status ? [] : facets.map(f => f.field));
        } else {
            facetList = new Set(expandedFacets);
            facetList[status ? 'delete' : 'add'](field);
        }

        sessionStorage.setItem(FACET_STORAGE, [...facetList].join(',')); // replace rather than update memory
        setExpandFacets(facetList); // controls open/closed facets
    };

    /**
     * Called when user types a key while focused on a facet term. If the user types a space or
     * return we call the term click handler -- needed for a11y because we have a <div> acting as a
     * button instead of an actual <button>.
     *
     * @param {event} e React synthetic event
     * @param {bool} status True for open, false for closed
     * @param {string} field Tab name
    */
    const handleKeyDown = (e, status, field) => {
        if (e.keyCode === 13 || e.keyCode === 32) {
            // keyCode: 13 = enter-key. 32 = spacebar
            e.preventDefault();
            handleExpanderClick(e, status, field);
        }
    };

    // See if we need the Clear filters link based on combinations of query-string parameters.
    let clearButton = false;
    const searchQuery = parsedUrl && parsedUrl.search;
    if (!supressTitle && searchQuery) {
        const querySearchTerm = new QueryString(parsedUrl.query);
        const queryType = querySearchTerm.clone();

        // We have a Clear Filters button if we have "searchTerm" or "advancedQuery" and *anything*
        // else.
        const hasSearchTerm = querySearchTerm.queryCount('searchTerm') > 0 || querySearchTerm.queryCount('advancedQuery') > 0;
        if (hasSearchTerm) {
            querySearchTerm.deleteKeyValue('searchTerm').deleteKeyValue('advancedQuery');
            clearButton = querySearchTerm.queryCount() > 0;
        }

        // If no Clear Filters button yet, do the same check with `type` in the query string.
        if (!clearButton) {
            // We have a Clear Filters button if we have "type" and *anything* else.
            const hasType = queryType.queryCount('type') > 0;
            if (hasType) {
                queryType.deleteKeyValue('type');
                clearButton = queryType.queryCount() > 0;
            }
        }
    }

    return (
        <div className="search-results__facets">
            <div className={`box facets${addClasses ? ` ${addClasses}` : ''}`}>
                <div className={`orientation${orientation === 'horizontal' ? ' horizontal' : ''}`} data-test="facetcontainer">
                    {(!supressTitle || clearButton) ?
                        <div className="search-header-control">
                            <DocTypeTitle searchResults={context} wrapper={children => <h1>{children} {docTypeTitleSuffix}</h1>} />
                            {context.clear_filters ?
                                <ClearFilters searchUri={context.clear_filters} enableDisplay={clearButton} />
                            : null}
                        </div>
        : null}
                    {mode === 'picker' && !hideTextFilter ? <TextFilter {...props} filters={filters} /> : ''}
                    <div className="facet-wrapper">
                        {facets.map((facet) => {
                            // Filter the filters to just the ones relevant to the current facet,
                            // matching negation filters too.
                            const relevantFilters = context && context.filters.filter(filter => (
                                filter.field === facet.field || filter.field === `${facet.field}!`
                            ));

                            // Look up the renderer registered for this facet and use it to render this
                            // facet if a renderer exists. A non-existing renderer supresses the
                            // display of a facet.
                            const FacetRenderer = FacetRegistry.Facet.lookup(facet.field);
                            const isExpanded = expandedFacets.has(facet.field);
                            return FacetRenderer && <FacetRenderer
                                key={facet.field}
                                facet={facet}
                                results={context}
                                mode={mode}
                                relevantFilters={relevantFilters}
                                pathname={parsedUrl.pathname}
                                queryString={parsedUrl.query}
                                onFilter={onFilter}
                                isExpanded={isExpanded}
                                handleExpanderClick={handleExpanderClick}
                                handleKeyDown={handleKeyDown}
                                isExpandable={isExpandable}
                            />;
                        })}
                    </div>
                </div>
            </div>
        </div>
    );
};

FacetList.propTypes = {
    context: PropTypes.object.isRequired,
    facets: PropTypes.oneOfType([
        PropTypes.array,
        PropTypes.object,
    ]).isRequired,
    filters: PropTypes.array.isRequired,
    mode: PropTypes.string,
    orientation: PropTypes.string,
    hideTextFilter: PropTypes.bool,
    docTypeTitleSuffix: PropTypes.string,
    addClasses: PropTypes.string, // CSS classes to use if the default isn't needed.
    /** True to supress the display of facet-list title */
    supressTitle: PropTypes.bool,
    /** Special facet-term click handler for edit forms */
    onFilter: PropTypes.func,
    /** True if the collapsible, false otherwise  */
    isExpandable: PropTypes.bool,
};

FacetList.defaultProps = {
    mode: '',
    orientation: 'vertical',
    hideTextFilter: false,
    addClasses: '',
    docTypeTitleSuffix: 'search',
    supressTitle: false,
    onFilter: null,
    isExpandable: true,
};

FacetList.contextTypes = {
    session: PropTypes.object,
    session_properties: PropTypes.object,
};


/**
 * Display the "Clear filters" link.
 */
export const ClearFilters = ({ searchUri, enableDisplay }) => (
    <div className="clear-filters-control">
        {enableDisplay ? <div><a href={searchUri}>Clear Filters <i className="icon icon-times-circle" /></a></div> : null}
    </div>
);

ClearFilters.propTypes = {
    /** URI for the Clear Filters link */
    searchUri: PropTypes.string.isRequired,
    /** True to display the link */
    enableDisplay: PropTypes.bool,
};

ClearFilters.defaultProps = {
    enableDisplay: true,
};


/**
 * Display and react to controls at the top of search result output, like the search and matrix
 * pages.
 */
export const SearchControls = ({ context, visualizeDisabledTitle, showResultsToggle, onFilter, hideBrowserSelector, activeFilters, showDownloadButton }, reactContext) => {
    const results = context['total'];
    const searchBase = url.parse(reactContext.location_href).search || '';
    let trimmedSearchBase = ''
    if (searchBase.indexOf("&limit=") !== -1 || searchBase.indexOf("?limit=") !== -1 ) {
        console.log("has limit")
        if (searchBase.indexOf("limit=all") !== -1) {
            trimmedSearchBase =searchBase.replace(/[?|&]limit=all/, '')
        } else {
            trimmedSearchBase =searchBase.replace(/[?|&]limit=\d*/, '')
        }
    }else{
        trimmedSearchBase = searchBase
    }
    const canDownload = context.total <= MAX_DOWNLOADABLE_RESULT;
    const modalText = canDownload ?
        <>
            <p>
                Click the &ldquo;Download&rdquo; button below to download a &ldquo;files.txt&rdquo; file that contains a list of URLs to a file containing all the experimental metadata and links to download the file.
                The first line of the file has the URL or command line to download the metadata file.
            </p>
            <p>
                Further description of the contents of the metadata file are described in the <a href="/help/batch-download/">Batch Download help doc</a>.
            </p>
            <p>
                The &ldquo;files.txt&rdquo; file can be copied to any server.<br />
                The following command using cURL can be used to download all the files in the list:
            </p>
            <code>xargs -L 1 curl -O -J -L &lt; files.txt</code><br />
        </> :
        <>
            <p>
                This search is too large (&gt;{MAX_DOWNLOADABLE_RESULT} datasets) to automatically generate a manifest or metadata file.  We are currently working on methods to download from large searches.
            </p>
            <p>
                You can directly access the files in AWS: <a href="https://registry.opendata.aws/encode-project/" target="_blank" rel="noopener noreferrer">https://registry.opendata.aws/encode-project/</a>
            </p>
        </>;

    let resultsToggle = null;
    const buttonStyle = {
        marginRight: '5px',
    };



    resultsToggle = (

            <div className="btn-attached">
                {results > 25 &&
                <a
                className="btn btn-info btn-sm"
                style={buttonStyle}
                href={trimmedSearchBase || '/search/'}
                onClick={onFilter}
                >
                    View 25
                </a>}
                {results > 50 &&
                <a
                className="btn btn-info btn-sm"
                style={buttonStyle}
                href={trimmedSearchBase ? `${trimmedSearchBase}&limit=50` : '/search/?limit=50'}
                onClick={onFilter}
                >
                    View 50
                </a>}
                {results > 100 &&
                <a
                    className="btn btn-info btn-sm"
                    style={buttonStyle}
                    href={trimmedSearchBase ? `${trimmedSearchBase}&limit=100` : '/search/?limit=100'}
                    onClick={onFilter}
                >
                    View 100
                </a>}
                {results > 25 &&
                <a
                rel="nofollow"
                className="btn btn-info btn-sm"
                style={buttonStyle}
                href={trimmedSearchBase ? `${trimmedSearchBase}&limit=all` : '?limit=all'}
                onClick={onFilter}
                >
                    View All
                </a>
                }

            </div>
    );
    return (
        <div className="results-table-control">
            <div className="results-table-control__main">
                <ViewControls results={context} activeFilters={activeFilters} />
                {Boolean(context['title'] == "Search") && resultsToggle}
                {showDownloadButton ? <BatchDownloadControls results={context} modalText={modalText} canDownload={canDownload} /> : ''}
                {!hideBrowserSelector ?
                    <BrowserSelector results={context} disabledTitle={visualizeDisabledTitle} activeFilters={activeFilters} />
                : null}
            </div>
            <div className="results-table-control__json">
                <DisplayAsJson />
            </div>
        </div>
    );
};

SearchControls.propTypes = {
    /** Search results object that generates this page */
    context: PropTypes.object.isRequired,
    /** True to disable Visualize button */
    visualizeDisabledTitle: PropTypes.string,
    /** True to show View All/View 25 control */
    showResultsToggle: (props, propName, componentName) => {
        if (props[propName] && typeof props.onFilter !== 'function') {
            return new Error(`"onFilter" prop to ${componentName} required if "showResultsToggle" is true`);
        }
        return null;
    },
    /** Function to handle clicks in links to toggle between viewing all and limited */
    onFilter: (props, propName, componentName) => {
        if (props.showResultsToggle && typeof props[propName] !== 'function') {
            return new Error(`"onFilter" prop to ${componentName} required if "showResultsToggle" is true`);
        }
        return null;
    },
    /** True to hide the Visualize button */
    hideBrowserSelector: PropTypes.bool,
    /** Add filters to search links if needed */
    activeFilters: PropTypes.array,
    /** Determines whether or not download button is displayed */
    showDownloadButton: PropTypes.bool,
};

SearchControls.defaultProps = {
    visualizeDisabledTitle: '',
    showResultsToggle: false,
    onFilter: null,
    hideBrowserSelector: false,
    activeFilters: [],
    showDownloadButton: true,
};

SearchControls.contextTypes = {
    location_href: PropTypes.string,
};


// Maximum number of selected items that can be visualized.
const VISUALIZE_LIMIT = 100;


export class ResultTable extends React.Component {
    constructor(props) {
        super(props);

        // Bind `this` to non-React moethods.
        this.onFilter = this.onFilter.bind(this);
    }

    getChildContext() {
        return {
            actions: this.props.actions,
        };
    }

    onFilter(e) {
        const searchStr = e.currentTarget.getAttribute('href');
        this.props.onChange(searchStr);
        e.stopPropagation();
        e.preventDefault();
    }

    render() {
        const { context, searchBase, actions } = this.props;
        const { facets } = context;
        const results = context['@graph'];
        const total = context.total;
        const columns = context.columns;
        const filters = context.filters;
        const label = 'results';
        const visualizeDisabledTitle = context.total > VISUALIZE_LIMIT ? `Filter to ${VISUALIZE_LIMIT} to visualize` : '';

        return (
            <div className="search-results">
                <FacetList
                    {...this.props}
                    facets={facets}
                    filters={filters}
                    searchBase={searchBase ? `${searchBase}&` : `${searchBase}?`}
                    onFilter={this.onFilter}
                />
                {context.notification === 'Success' ?
                    <div className="search-results__result-list">
                        <h4>Showing {results.length} of {total} {label}</h4>
                        <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} onFilter={this.onFilter} showResultsToggle />
                        {!(actions && actions.length > 0) ?
                            <CartSearchControls searchResults={context} />
                        : null}
                        <ResultTableList results={results} columns={columns} cartControls />
                    </div>
                :
                    <h4>{context.notification}</h4>
                }
            </div>
        );
    }
}

ResultTable.propTypes = {
    context: PropTypes.object.isRequired,
    actions: PropTypes.array,
    searchBase: PropTypes.string,
    onChange: PropTypes.func.isRequired,
    currentRegion: PropTypes.func,
};

ResultTable.defaultProps = {
    actions: [],
    searchBase: '',
    currentRegion: null,
};

ResultTable.childContextTypes = {
    actions: PropTypes.array,
};

ResultTable.contextTypes = {
    session: PropTypes.object,
};



// Display the list of search results. `mode` allows for special displays, and supports:
//     picker: Results displayed in an edit form object picker
//     cart-view: Results displayed in the Cart View page.
export const ResultTableList = ({ results, columns, cartControls, mode }) => (
    <ul className="result-table" id="result-table">
        {results.length > 0 ?
            results.map(result => Listing({ context: result, columns, key: result['@id'], cartControls, mode }))
        : null}
    </ul>
);

ResultTableList.propTypes = {
    results: PropTypes.array.isRequired, // Array of search results to display
    columns: PropTypes.object, // Columns from search results
    cartControls: PropTypes.bool, // True if items should display with cart controls
    mode: PropTypes.string, // Special search-result modes, e.g. "picker"
};

ResultTableList.defaultProps = {
    columns: null,
    cartControls: false,
    mode: '',
};


export class Search extends React.Component {
    constructor() {
        super();

        // Bind `this` to non-React methods.
        this.currentRegion = this.currentRegion.bind(this);
    }

    currentRegion(assembly, region) {
        if (assembly && region) {
            this.lastRegion = {
                assembly,
                region,
            };
        }
        return Search.lastRegion;
    }

    render() {
        const context = this.props.context;
        const notification = context.notification;
        const searchBase = url.parse(this.context.location_href).search || '';
        const facetdisplay = context.facets && context.facets.some(facet => facet.total > 0);

        if (facetdisplay) {
            return (
                <Panel>
                    <PanelBody>
                        <ResultTable {...this.props} searchBase={searchBase} onChange={this.context.navigate} currentRegion={this.currentRegion} />
                    </PanelBody>
                </Panel>
            );
        }

        return <h4>{notification}</h4>;
    }
}

Search.propTypes = {
    context: PropTypes.object.isRequired,
};

Search.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

// optionally make a persistent region
Search.lastRegion = {
    assembly: PropTypes.string,
    region: PropTypes.string,
};

globals.contentViews.register(Search, 'Search');


