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
    UniProtKB: {
        pattern: 'http://www.uniprot.org/uniprot/{0}',
    },
    HGNC: {
        pattern: 'http://www.genecards.org/cgi-bin/carddisp.pl?gene={0}',
        preprocessor: (context) => {
            if (context['@type'][0] === 'Target' && context.gene_name) {
                return { altValue: context.gene_name };
            }
            return {};
        },
    },
    GeneID: {
        pattern: 'https://www.ncbi.nlm.nih.gov/gene/{0}',
    },
    GEO: {
        pattern: 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}',
        preprocessor: (context, dbxref) => {
            // If the first four characters of the GEO value is "SAMN" then we need
            // to use a different URL pattern.
            const value = dbxref.split(':');
            if (value[1] && value[1].substr(0, 4) === 'SAMN') {
                return { altUrlPattern: 'https://www.ncbi.nlm.nih.gov/biosample/{0}' };
            }
            return {};
        },
    },
    IHEC: {
        pattern: 'http://www.ebi.ac.uk/vg/epirr/view/{0}',
    },
    Cellosaurus: {
        pattern: 'http://web.expasy.org/cellosaurus/{0}',
    },
    FlyBase: {
        pattern: 'http://flybase.org/cgi-bin/quicksearch_solr.cgi?caller=quicksearch&tab=basic_tab&data_class=FBgn&species=Dmel&search_type=all&context={0}',
        preprocessor: (context) => {
            // If a target displays its dbxrefs, use the fly stock URL.
            if (context['@type'][0] !== 'Target') {
                return { altUrlPattern: 'http://flybase.org/reports/{0}.html' };
            }
            return {};
        },
    },
    BDSC: {
        pattern: 'http://flystocks.bio.indiana.edu/Reports/{0}',
    },
    WormBase: {
        pattern: 'http://www.wormbase.org/species/c_elegans/gene/{0}',
        preprocessor: (context) => {
            // If a target displays its dbxrefs, use the fly stock URL.
            if (context['@type'][0] !== 'Target') {
                return { altUrlPattern: 'http://www.wormbase.org/species/c_elegans/strain/{0}' };
            }
            return {};
        },
    },
    WormBaseStock: {
        pattern: 'http://www.wormbase.org/species/c_elegans/strain/{0}',
    },
    NBP: {
        pattern: 'http://shigen.nig.ac.jp/c.elegans/mutants/DetailsSearch?lang=english&seq={0}',
    },
    CGC: {
        pattern: 'https://cgc.umn.edu/strain/{0}',
    },
    DSSC: {
        pattern: 'https://stockcenter.ucsd.edu/index.php?action=view&q={0}&table=Species&submit=Search',
    },
    'MGI.D': {
        pattern: 'http://www.informatics.jax.org/inbred_strains/mouse/docs/{0}.shtml',
    },
    RBPImage: {
        pattern: 'http://rnabiology.ircm.qc.ca/RBPImage/gene.php?cells={1}&targets={0}',
        postprocessor: (context, dbxref, urlPattern) => (
            // Experiments with RBPImage need to replace one urlPattern element with
            // biosample_term_name.
            (context['@type'][0] === 'Experiment' ? urlPattern.replace(/\{1\}/g, context.biosample_term_name) : urlPattern)
        ),
    },
    JAX: {
        pattern: 'https://www.jax.org/strain/{0}',
    },
    NBRP: {
        pattern: 'https://shigen.nig.ac.jp/c.elegans/mutants/DetailsSearch?lang=english&seq={0}',
    },
    'UCSC-ENCODE-mm9': {
        pattern: 'http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=mm9&hgt_mdbVal1={0}',
    },
    'UCSC-ENCODE-hg19': {
        pattern: 'http://genome.ucsc.edu/cgi-bin/hgTracks?tsCurTab=advancedTab&tsGroup=Any&tsType=Any&hgt_mdbVar1=dccAccession&hgt_tSearch=search&hgt_tsDelRow=&hgt_tsAddRow=&hgt_tsPage=&tsSimple=&tsName=&tsDescr=&db=hg19&hgt_mdbVal1={0}',
    },
    'UCSC-ENCODE-cv': {
        pattern: 'http://genome.cse.ucsc.edu/cgi-bin/hgEncodeVocab?ra=encode%2Fcv.ra&term=%22{0}%22',
    },
    'UCSC-GB-mm9': {
        pattern: 'http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=mm9&g={0}',
    },
    'UCSC-GB-hg19': {
        pattern: 'http://genome.cse.ucsc.edu/cgi-bin/hgTrackUi?db=hg19&g={0}',
    },
    PMID: {
        pattern: 'https://www.ncbi.nlm.nih.gov/pubmed/?term={0}',
    },
    PMCID: {
        pattern: 'https://www.ncbi.nlm.nih.gov/pmc/articles/{0}',
    },
    doi: {
        pattern: 'http://dx.doi.org/doi:{0}',
    },
    AR: {
        pattern: 'http://antibodyregistry.org/search.php?q={0}',
    },
    NIH: {
        pattern: 'https://search.usa.gov/search?utf8=%E2%9C%93&affiliate=grants.nih.gov&query={0}',
    },
};


const DbxrefUrl = (props) => {
    const { dbxref, context } = props;

    // Standard dbxref pattern: {prefix}:{value}. If the dbxref has more than one colon, only the
    // first colon splits the dbxref into `prefix` and `value`. The other colons get included as
    // part of the value. If the dbxref has no colons at all, prefix gets the whole dbxref string
    // and `value` gets the empty string.
    const prefix = dbxref.split(':', 1)[0];
    let value = dbxref.slice(prefix.length + 1);

    // Using the prefix, find the corresponding URL pattern.
    const urlProcessor = dbxrefPrefixMap[prefix];

    // Get the urlPattern for the dbxref prefix. This pattern can be replaced by the preprocessor
    // during the next step.
    let urlPattern = urlProcessor.pattern;

    // Call the preprocessor if it exists to replace either the URL pattern, the value, or both.
    // Normally, the contents of the context object determines if a URL or value should change.
    if (urlProcessor.preprocessor) {
        const { altUrlPattern, altValue } = urlProcessor.preprocessor(context, dbxref);
        urlPattern = altUrlPattern || urlPattern;
        value = altValue || value;
    }

    // Now replace the {0} in the URL pattern with the value we extracted to form the final URL,
    // then display that as a link.
    if (urlPattern) {
        let url = urlPattern.replace(/\{0\}/g, encodeURIComponent(value));

        // If, after replacing the {0} with the value, the URL needs further modification, call the
        // caller-provided post-processor with the given dbxref and the generated URL.
        if (urlProcessor.postprocessor) {
            url = urlProcessor.postprocessor(context, dbxref, url);
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
    context: PropTypes.object.isRequired, // Object that contains the dbxref
};


export const DbxrefListNew = (props) => {
    const { dbxrefs, preprocessor, context, addClasses } = props;

    return (
        <ul className={addClasses}>
            {dbxrefs.map((dbxref, i) =>
                <li key={i}><DbxrefUrl dbxref={dbxref} preprocessor={preprocessor} context={context} /></li>
            )}
        </ul>
    );
};

DbxrefListNew.propTypes = {
    dbxrefs: PropTypes.array.isRequired, // Array of dbxref values to display
    preprocessor: PropTypes.func, // Preprocessor callback
    context: PropTypes.object.isRequired, // Object containing the dbxref
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
