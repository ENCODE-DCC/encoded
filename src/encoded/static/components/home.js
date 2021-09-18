import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';
import { Panel, PanelBody } from '../libs/ui/panel';
import Tooltip from '../libs/ui/tooltip';


// Main page component to render the home page
export default class Home extends React.Component {
    constructor(props) {
        super(props);

        // Set initial React state.
        this.state = {
            organisms: [], // create empty array of selected tabs
            assayCategory: '',
            socialHeight: 0,
        };

        // Required binding of `this` to component methods or else they can't see `this`.
        this.handleAssayCategoryClick = this.handleAssayCategoryClick.bind(this);
    }

    handleAssayCategoryClick(assayCategory) {
        if (this.state.assayCategory === assayCategory) {
            this.setState({ assayCategory: '' });
        } else {
            this.setState({ assayCategory });
        }
    }

    render() {
        const adminUser = !!(this.context.session_properties && this.context.session_properties.admin);

        return (
            <Panel>
                <HomeContent />
            </Panel>
        );
    }
}

Home.contextTypes = {
    session_properties: PropTypes.object,
};


// Component to allow clicking boxes on classic image
class HomeContent extends React.Component {
    constructor(props) {
        super(props);
    }

    render() {
        return (
            <div>
                <div className="overall-classic homepage">
                    <div className="header">
                        <h1>Lattice</h1>
                        <img src="static/img/lattice-cells.png" alt="Lattice DB" className="logo" />
		                </div>

                    <div className="site-banner main-content">
                        <div className="site-banner__intro text-side">
                            <p>Lattice are the Data Coordination Center for the Human Cell Atlas <a href="https://chanzuckerberg.com/science/programs-resources/humancellatlas/seednetworks/" target="_blank">Seed Networks</a> and <a href="https://chanzuckerberg.com/science/programs-resources/single-cell-biology/pediatric-networks/" target="_blank">Pediatric Networks</a>.</p>
                            <p>The Lattice team collaborates with researchers in each of the 38 Seed Networks and 17 Pediatric Networks to represent sample acquisition, experimental procedures, and data processing steps in structured metadata [<a href="/data-organization">learn more about our Data Organization</a>]. We wrangle metadata, raw data, and analysis outputs into the Lattice database which provides contributors the opportunity for intra- and inter-Network data sharing prior to data release.</p>
    		                    <p>As stewards for the Seed Network and Pediatric Network data, the Lattice team actively seeks out opportunities to maximize the value of the data through enhanced findability and reuse. We collaborate with other single-cell data centers to migrate the standardized data corpus from the Lattice database to their open data resources, allowing for data to be easily integrated with community tools and data collections.</p>
                        </div>
                        <div className="img-side">
                            <img src="static/img/lattice-banner.png" alt="Lattice DB" />
                        </div>
                    </div>

                    <div className="site-banner main-content">
                        <div className="img-side">
                            <img src="static/img/tabula_sapiens_cxg.png" alt="CXG UMAP" />
                        </div>
                        <div className="site-banner__intro text-side">
                            <p>Lattice are also the Lead Curation Team for <a href="https://cellxgene.cziscience.com/" target="_blank">cellxgene</a>.</p>
                            <p>Lattice work with cellxgene developers and computational bioologists at the Chan Zuckerberg Initiative to develop a cell-based schema that captures and standardizes key biological and technical variables that impact single-cell data.</p>
                            <p>We facilitate the submission of data as a means to enhance the data sharing and exploration of a each dataset, individually, while ensuring a harmonized data corpus that can be readily searched, filtered, and integrated.</p>
                            <p>Image to the left is from the <a href="https://cellxgene.cziscience.com/e/53d208b0-2cfd-4366-9866-c3c6114081bc.cxg/" target="_blank">Tabula Sapiens dataset</a>.</p>
                        </div>
                    </div>
                    <div className="site-banner__intro contact">
                        <p className="email-us">Contact the Lattice team at <a href="mailto:lattice-info@lists.stanford.edu"> lattice-info@lists.stanford.edu</a></p>
                    </div>
                    <div className="site-banner__intro credits">
                        <p>The Lattice team consists of data wranglers & software developers within the Cherry Lab at the Stanford University Department of Genetics. <a href="https://cherrylab.stanford.edu/people/human-cell-atlas/grid" target="_bank">Meet the team</a></p>
                        <p className="italic">Lattice is funded by the Chan Zuckerberg Initiative (CZI).</p>
                        <p className="italic">Lattice logo by Idan Gabdank, Ph.D.</p>
                    </div>
                </div>
            </div>
        );
    }
}
