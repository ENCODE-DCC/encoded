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

                    <div className="site-banner__intro main-content">
                       <p>Lattice is the acting Data Coordination Center for the CZI Seed Networks.</p>
                       <div className="quote">
                          <i>"The Seed Networks for the Human Cell Atlas projects bring together experimental scientists, computational biologists, software engineers, and physicians to support the continued development of the Human Cell Atlas (HCA), an international effort to map all cells in the human body as a resource for better understanding health and disease." <br />- <a href="https://chanzuckerberg.com/science/programs-resources/humancellatlas/seednetworks/" target="_blank">Human Cell Atlas Seed Networks</a></i>
                        </div>
                     </div>
                     <div className="site-banner main-content">
                        <div className="site-banner__intro text-side">
                            <p>The Lattice team collaborates with researchers in each of the 38 Seed Networks to represent sample acquisition, experimental procedures, and data processing steps in structured metadata [<a href="/data-organization">learn more about our Data Organization</a>]. We wrangle metadata, raw data, and analysis outputs into the Lattice database which provides Seed Network contributors the opportunity for intra- and inter-Seed Network data sharing prior to data release. Through tight collaboration with the computational biologists in the Seed Networks, Lattice ensures essential information is captured to facilitate the generation of a reference atlas of the cells in the human body.</p>
		            <p>As stewards for the Seed Network data, the Lattice team actively seeks out opportunities to maximize the value of the data through enhanced findability and reuse. We collaborate with other single-cell data centers to migrate the standardized data corpus from the Lattice database to their open data resources, allowing for Seed Network data to be easily integrated with community tools and data collections.</p>
                        </div>
                        <div className="img-side">
                            <img src="static/img/lattice-banner.png" alt="Lattice DB" />
                        </div>
                    </div>

                    <div className="contacts">
                        <div className="site-banner__intro contact">
                           <div className="contact-group">
                              <p className="call-contact">Seed Network researchers</p>
                              <p>Do you have data to submit?</p>
                              <p>Have questions about metadata collection?</p>
                           </div>
                           <div className="contact-group">
                              <p className="call-contact">Community data resources</p>
                              <p>Interested in integrating Seed Network data?</p>
                              <p>Have questions about the Lattice data model & schema?</p>
                           </div>
                        </div>
                        <div className="site-banner__intro contact">
                           <p className="email-us">Contact the Lattice team at <a href="mailto:lattice-info@lists.stanford.edu"> lattice-info@lists.stanford.edu</a></p>
                        </div>
                    </div>
                    <div className="site-banner__intro credits">
                        <p>The Lattice team consists of data wranglers & software developers within the Cherry Lab at the Stanford University Department of Genetics. <a href="https://cherrylab.stanford.edu/people/human-cell-atlas/grid" target="_bank">Meet the team</a></p>
                        <p className="italic">Lattice is funded by the Chan Zuckerberg Initiative (CZI).</p>
                        <p className="italic">Lattice logo adapted from the <a href="https://www.humancellatlas.org/" target="_blank">Human Cell Atlas</a> by Idan Gabdank, Ph.D.</p>
                    </div>
                </div>
            </div>
        );
    }
}
