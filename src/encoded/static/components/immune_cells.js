import React from 'react';
import PropTypes from 'prop-types';
import _ from 'underscore';
import { Panel, PanelBody } from '../libs/ui/panel';
import { MATRIX_VISUALIZE_LIMIT } from './matrix';
import { MatrixBadges } from './objectutils';
import { SearchControls } from './search';
import * as globals from './globals';
import drawTree from '../libs/ui/node_graph';

const fullHeight = 700;
const margin = { top: 70, right: 0, bottom: 60, left: 0 };

/**
 * Render the area above the matrix itself, including the page title.
 *
 * @param {object} { context }
 * @returns
 */
const MatrixHeader = ({ context }) => {
    const visualizeDisabledTitle = context.total > MATRIX_VISUALIZE_LIMIT ? `Filter to ${MATRIX_VISUALIZE_LIMIT} to visualize` : '';

    return (
        <div className="matrix-header">
            <div className="matrix-header__title">
                <div className="matrix-title-badge">
                    <h1>{context.title}</h1>
                    <MatrixBadges context={context} />
                </div>
                <div className="matrix-description">
                    <div className="matrix-description__text">
                        Project data of the epigenomic profiles of cell types differentiated from the H9 cell line provided by the Southeast Stem Cell Consortium (SESCC).
                    </div>
                </div>
            </div>
            <div className="matrix-header__controls">
                <div className="matrix-header__search-controls-sescc">
                    <SearchControls context={context} visualizeDisabledTitle={visualizeDisabledTitle} hideBrowserSelector showDownloadButton={false} />
                </div>
            </div>
        </div>
    );
};

MatrixHeader.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


MatrixHeader.contextTypes = {
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};

/**
 * Presentation
 *
 * @class MatrixPresentation
 * @extends {React.Component}
 */
class MatrixPresentation extends React.Component {
    constructor(props) {
        super(props);

        const immuneCells = require('./node_graph_data/immune_cells.json');

        this.state = {
            windowWidth: 0,
            selectedNodes: [],
        };

        this.immuneCells = immuneCells[0];
        this.updateWindowWidth = this.updateWindowWidth.bind(this);
        this.setSelectedNodes = this.setSelectedNodes.bind(this);
    }

    componentDidMount() {
        this.updateWindowWidth();
        window.addEventListener('resize', this.updateWindowWidth);

        require.ensure(['d3'], (require) => {
            this.d3 = require('d3');

            const chartWidth = this.state.windowWidth;
            drawTree(this.d3, '.vertical-node-graph', this.immuneCells, chartWidth, fullHeight, margin, this.state.selectedNodes, this.setSelectedNodes);
        });
    }

    // componentDidUpdate() {
    //     console.log(this.state.selectedNodes);
    // }

    setSelectedNodes(newNode) {
        this.setState((prevState) => {
            const newSelection = newNode.replace(/\s/g, '').toLowerCase();
            if (prevState.selectedNodes.indexOf(newSelection) > -1 && prevState.selectedNodes.length > 1) {
                return { selectedNodes: prevState.selectedNodes.filter((s) => s !== newSelection) };
            }
            if (prevState.selectedNodes.indexOf(newSelection) > -1) {
                return { selectedNodes: [] };
            }
            return { selectedNodes: [...prevState.selectedNodes, newSelection] };
        });
    }

    updateWindowWidth() {
        this.setState({
            windowWidth: document.getElementById('immune_cells_wrapper').offsetWidth,
        });
    }

    render() {
        return (
            <div className="matrix__presentation" id="immune_cells_wrapper">
                <div className="sescc_matrix__graph-region">
                    <div className="vertical-node-graph" />
                </div>
            </div>
        );
    }
}

MatrixPresentation.contextTypes = {
    navigate: PropTypes.func,
    fetch: PropTypes.func,
};


/**
 * Render the area containing the matrix.
 */
const MatrixContent = ({ context }) => (
    <div className="matrix__content matrix__content--reference-epigenome">
        <MatrixPresentation context={context} />
    </div>
);

MatrixContent.propTypes = {
    /** Matrix search result object */
    context: PropTypes.object.isRequired,
};


const ImmuneCells = ({ context }) => {
    const itemClass = globals.itemClass(context, 'view-item');

    return (
        <Panel addClasses={itemClass}>
            <PanelBody>
                <MatrixHeader context={context} />
                <MatrixContent context={context} />
            </PanelBody>
        </Panel>
    );
};

ImmuneCells.propTypes = {
    context: PropTypes.object.isRequired,
};

ImmuneCells.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

globals.contentViews.register(ImmuneCells, 'ImmuneCells');
