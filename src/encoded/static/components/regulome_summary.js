import React from 'react';
import PropTypes from 'prop-types';
import url from 'url';
import { BrowserSelector } from './objectutils';
import { Panel, PanelBody } from '../libs/bootstrap/panel';
// import { FacetList, Listing, ResultBrowser } from './search';
// import { FetchedData, Param } from './fetched';
import * as globals from './globals';
// import _ from 'underscore';
import { SortTablePanel, SortTable } from './sorttable';


const SNPSummary = (props) => {

    const snps = props.context.summaries;

    const snpsColumns = {
        chrom: {
            title: 'Chromosome location',
            display: (item) => {
                let href_score = '../regulome-search/?region='+item.chrom+':'+item.start+'-'+item.end+'&genome=GRCh37';
                return <a href={href_score}>{item.chrom+":"+item.start+".."+item.end}</a>;
            },
        },
        rsids: {
            title: 'dbSNP IDs',
            display: (item) => {
                let href_score = '../regulome-search/?region='+item.chrom+':'+item.start+'-'+item.end+'&genome=GRCh37';
                return <a href={href_score}>{item.rsids.join(', ')}</a>;
            },
        },
        regulome_score: {
            title: 'Regulome score',
            display: (item) => {
                if (item.regulome_score !== "N/A" && item.regulome_score !== null){
                    let href_score = '../regulome-search/?region='+item.chrom+':'+item.start+'-'+item.end+'&genome=GRCh37';
                    return <a href={href_score}>{item.regulome_score}</a>;
                } else {
                    let href_score = '../regulome-search/?region='+item.chrom+':'+item.start+'-'+item.end+'&genome=GRCh37';
                    return <a href={href_score}>See related experiments</a>;
                }
            },
        },
    };
    return (
        <div>
            <SortTablePanel title="Summary of SNP analysis">
                <SortTable list={snps} columns={snpsColumns} />
            </SortTablePanel>
        </div>
    );
 }

class RegulomeSummary extends React.Component {

    render() {
        const context = this.props.context;
        const summaries = context.summaries;
        const notifications = context.notifications;
        const coordinates = context.coordinates;

        let snp_count = 0;
        summaries.forEach(summary => {
            snp_count += summary.rsids.length;
        })

        return (
            <div>
                <div className="lead-logo"><a href="/"><img src="/static/img/RegulomeLogoFinal.gif"></img></a></div>

                <div className="results-summary">
                    <p>This search has evaluated {context.notifications.length} input lines and found {snp_count} SNP(s).</p>
                    {notifications.map((notification,idx) => {
                        if (notification[coordinates[idx]] !== "Success") {
                            return (<p key={idx}>Region {coordinates[idx]} {notification[coordinates[idx]]}</p>)
                        }
                    })}

                </div>

                <div className="summary-table-hoverable">
                    <SNPSummary {...this.props} />
                </div>

            </div>
        );
    }
}

RegulomeSummary.propTypes = {
    context: PropTypes.object.isRequired,
    currentRegion: PropTypes.func,
    region: PropTypes.string,
};

RegulomeSummary.defaultProps = {
    currentRegion: null,
    region: null,
};

RegulomeSummary.contextTypes = {
    location_href: PropTypes.string,
    navigate: PropTypes.func,
};

globals.contentViews.register(RegulomeSummary, 'regulome-summary');
