import React from 'react';
import PropTypes from 'prop-types';
import * as globals from './globals';


// DbxrefList
// ==========
// Display comma-separated list of linked external IDs/dbxrefs. For simplicity, I'll just call
// these "dbxrefs" from now. This uses a global array (dbxrefPrefixMap below) of possible dbxref
// URL patterns based on dbxref prefixes.
//
// Dbxrefs usually look like {prefix}:{value}, and this maps to a URL that includes the value in
// some way, maybe as a REST endpoint (https://abc.com/{value}) or as part of a query string
// (https://abc.com/?value={value}). The prefix selects which URL pattern to use.
//
// A URL pattern here is the URL to link to for each prefix, and with a "{0}" embedded in the
// pattern that shows where the {value} should go. For example, if we have a dbxref
// "UniProtKB:1234" then you can see from the dbxrefPrefixMap global that this maps to the URL
// pattern:
//
// http://www.uniprot.org/uniprot/{0}
//
// Because this is the simplest case that needs no more complex processing, the resulting link that
// <DbxrefList> generates for this example is:
//
// http://www.uniprot.org/uniprot/1234
//
// Preprocessor
// ------------
// Dbxrefs aren't always so simple and need some massaging before DbxrefList generates the URL. An
// example is:
//
//     "GEO:GSM1234" that should generate https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc=1234
//     "GEO:SAMN123" that should generate https://www.ncbi.nlm.nih.gov/biosample/1234
//
// They both use the "GEO" prefix but map to different URL patterns. For any objects that could
// include GEO dbxrefs, it must provide to <DbxrefList> a preprocessor callback that takes a string
// parameter with the entire dbxref, and gets called once for each given dbxref value. To have two
// diffferent URL patterns, dbxrefPrefixMap has one GEO entry with the first pattern, and one
// GEOSAMN entry with the second pattern. GEOSAMN isn't a real prefix, but it lets us select a
// distinct pattern.
//
// The preprocessor callback returns an object:
//
// {
//     altPrefix: String with the alternate prefix to select a URL pattern in dbxrefPrefixMap.
//     values: Array of values to use in the URL pattern.
// }
//
// Having the `values` property be an array allows for URL patterns with multiple values. An
// example could be the pattern:
//
// https://abc.com/tissue/{0}/?type={0}
//
// If the preprocessor returned ['1234', '5678'] in `values`, the resulting URL would be:
//
// https://abc.com/tissue/1234/?type=5678
//

export const dbxrefPrefixMap = {
    UniProtKB: 'http://www.uniprot.org/uniprot/{0}',
    HGNC: 'http://www.genecards.org/cgi-bin/carddisp.pl?gene={0}',
    ENSEMBL: 'http://www.ensembl.org/Homo_sapiens/Gene/Summary?g={0}',
    GeneID: 'https://www.ncbi.nlm.nih.gov/gene/{0}',
    GEO: 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}',
    GEOSAMN: 'https://www.ncbi.nlm.nih.gov/biosample/{0}',
    IHEC: 'http://www.ebi.ac.uk/vg/epirr/view/{0}',
    Cellosaurus: 'http://web.expasy.org/cellosaurus/{0}',
    FlyBase: 'http://flybase.org/cgi-bin/quicksearch_solr.cgi?caller=quicksearch&tab=basic_tab&data_class=FBgn&species=Dmel&search_type=all&context={0}',
    FlyBaseStock: 'http://flybase.org/reports/{0}.html',
    BDSC: 'http://flystocks.bio.indiana.edu/Reports/{0}',
    WormBase: 'http://www.wormbase.org/species/c_elegans/gene/{0}',
    WormBaseStock: 'http://www.wormbase.org/species/c_elegans/strain/{0}',
    NBP: 'http://shigen.nig.ac.jp/c.elegans/mutants/DetailsSearch?lang=english&seq={0}',
    CGC: 'https://cgc.umn.edu/strain/{0}',
    DSSC: 'https://stockcenter.ucsd.edu/index.php?action=view&q={0}&table=Species&submit=Search',
    'MGI.D': 'http://www.informatics.jax.org/inbred_strains/mouse/docs/{0}.shtml',
    RBPImage: 'http://rnabiology.ircm.qc.ca/RBPImage/gene.php?cells={1}&targets={0}',
    RefSeq: 'https://www.ncbi.nlm.nih.gov/gene/?term={0}',
    JAX: 'https://www.jax.org/strain/{0}',
    NBRP: 'https://shigen.nig.ac.jp/c.elegans/mutants/DetailsSearch?lang=english&seq={0}',
    'UCSC-ENCODE-mm9': 'http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=mm9&hgt_mdbVal1={0}',
    'UCSC-ENCODE-hg19': 'http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1={0}',
    'UCSC-ENCODE-cv': 'http://genome.cse.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&term=%22{0}%22',
    'UCSC-GB-mm9': 'http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=mm9&g={0}',
    'UCSC-GB-hg19': 'http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g={0}',
    PMID: 'https://www.ncbi.nlm.nih.gov/pubmed/?term={0}',
    PMCID: 'https://www.ncbi.nlm.nih.gov/pmc/articles/{0}',
    doi: 'http://dx.doi.org/doi:{0}',
    AR: 'http://antibodyregistry.org/search.php?q={0}',
    NIH: 'https://search.usa.gov/search?utf8=%E2%9C%93&affiliate=grants.nih.gov&query={0}',
};


const DbxrefUrl = (props) => {
    const { dbxref, preprocessor, postprocessor } = props;

    // Standard dbxref pattern: {prefix}:{value}. If the dbxref has more than one colon, only the
    // first colon splits the dbxref into `prefix` and `value`. The other colons get included as
    // part of the value. If the dbxref has no colons at all, prefix gets the whole dbxref string
    // and `value` gets the empty string.
    let prefix = dbxref.split(':', 1)[0];
    let value = dbxref.slice(prefix.length + 1);

    // If the caller provided a preprocessor, call it to override the prefix and/or value we
    // extracted above.
    if (preprocessor) {
        const { altPrefix, altValue } = preprocessor(dbxref);
        prefix = altPrefix || prefix;
        value = altValue || value;
    }

    // Using the prefix, find the corresponding URL pattern.
    const urlPattern = dbxrefPrefixMap[prefix];

    // Now replace the {0} in the URL pattern with the value we extracted to form the final URL,
    // then display that as a link.
    if (urlPattern) {
        let url = urlPattern.replace(/\{0\}/g, encodeURIComponent(value));

        // If, after replacing the {0} with the value, the URL needs further modification, call the
        // caller-provided post-processor with the given dbxref and the generated URL.
        if (postprocessor) {
            url = postprocessor(dbxref, url);
        }

        // Return the final dbxref as a link.
        return <a href={url}>{value}</a>;
    }

    // The dbxref prefix didn't map to anything we know about, so just display the dbxref as
    // unlinked text.
    return <span>{dbxref}</span>;
};

DbxrefUrl.propTypes = {
    dbxref: PropTypes.string.isRequired, // dbxref string
    preprocessor: PropTypes.func, // Callback to process dbxref before this does
    postprocessor: PropTypes.func, // Callback to process URL pattern after value substitution
};

DbxrefUrl.defaultProps = {
    preprocessor: null,
    postprocessor: null,
};


export const DbxrefListNew = (props) => {
    const { dbxrefs, preprocessor, postprocessor, addClasses } = props;

    return (
        <ul className={addClasses}>
            {dbxrefs.map((dbxref, i) =>
                <li key={i}><DbxrefUrl dbxref={dbxref} preprocessor={preprocessor} postprocessor={postprocessor} /></li>
            )}
        </ul>
    );
};

DbxrefListNew.propTypes = {
    dbxrefs: PropTypes.array.isRequired, // Array of dbxref values to display
    preprocessor: PropTypes.func, // Preprocessor callback
    postprocessor: PropTypes.func, // Postprocessor callback
    addClasses: PropTypes.string, // CSS class to apply to dbxref list
};

DbxrefListNew.defaultProps = {
    preprocessor: null,
    postprocessor: null,
    addClasses: '',
};


export function dbxrefold(attributes) {
    const value = attributes.value || '';
    const sep = value.indexOf(':');
    let prefix = attributes.prefix;
    let local;
    let id;

    if (prefix) {
        local = value;
    } else if (sep !== -1) {
        prefix = value.slice(0, sep);
        local = globals.encodedURIComponent(value.slice(sep + 1), '_');
    }

    // Handle two different kinds of GEO -- GSM/GSE vs SAMN
    if (prefix === 'GEO' && local.substr(0, 4) === 'SAMN') {
        prefix = 'GEOSAMN';
    }

    // Handle two different kinds of WormBase IDs -- Target vs Strain
    if (prefix === 'WormBase' && attributes.target_ref) {
        prefix = 'WormBaseTargets';
    }

    // Handle two different kinds of FlyBase IDs -- Target vs Stock
    if (prefix === 'FlyBase' && !attributes.target_ref) {
        prefix = 'FlyBaseStock';
    }

    const base = prefix && globals.dbxrefPrefixMap[prefix];
    if (!base) {
        return <span>{value}</span>;
    }
    if (prefix === 'HGNC') {
        local = attributes.target_gene;

    // deal with UCSC links
    } else if (prefix === 'UCSC-ENCODE-cv') {
        local = `"${local}"`;
    } else if (prefix === 'MGI') {
        local = value;
    } else if (prefix === 'MGI.D') {
        id = value.substr(sep + 1);
        local = `${id}.shtml`;
    } else if (prefix === 'DSSC') {
        id = value.substr(sep + 1);
        local = `${id}&table=Species&submit=Search`;
    } else if (prefix === 'RBPImage') {
        if (attributes.cell_line) {
            local = `${attributes.cell_line}&targets=${local}`;
        } else {
            return <span>{value}</span>;
        }
    }

    return <a href={base + local}>{value}</a>;
}

export const DbxrefList = props => (
    <ul className={props.className}>
        {props.values.map((value, index) =>
            <li key={index}>{dbxrefold({ value, prefix: props.prefix, target_gene: props.target_gene, target_ref: props.target_ref, cell_line: props.cell_line })}</li>
        )}
    </ul>
);

DbxrefList.propTypes = {
    values: PropTypes.array.isRequired, // Array of dbxref values to display
    className: PropTypes.string, // CSS class to apply to dbxref list
    cell_line: PropTypes.string,
};

DbxrefList.defaultProps = {
    className: '',
};
