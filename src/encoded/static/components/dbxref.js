import React from 'react';
import PropTypes from 'prop-types';


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
// They both use the "GEO" prefix but map to different URL patterns depending on the following
// value. To handle this, dbxrefPrefixMap includes a preprocess for GEO that examines the dbxref
// value and returns a different URL if it detects the "SAMN" string at the start.
//
// The preprocessor callback takes the given `context` and `dbxref` string, and returns an object
// with zero, one, or both of these properties:
//
// {
//     altUrlPattern: String with the alternate URL pattern to use instead of the default one.
//     altValue: Dbxref value to use instead of the one in the dbxref string
// }
//
// `altUrlPattern` is a URL *pattern*, so it probably should include {0} so that this component
// replaces that with the value. You could even provide some other replacement pattern, like {1}
// maybe, that the postprocessor can replace if needed.
//
// Postprocessor
// ------------
// Sometimes the generated URL needs modification, like maybe it needs a second value placed
// somewhere in it. The postprocessor can do this. It receives the given `context`, `dbxref`, and
// the URL pattern after substitution. We normally call this *after* value substitution has taken
// place, so we have a URL, not a URL pattern. But the postprocessor can do its own value
// substitution by putting something like {1}, {2} etc. which gets preserved for the postprocessor
// to do its own substitution.
//

export const dbxrefPrefixMap = {
    UniProtKB: {
        pattern: 'http://www.uniprot.org/uniprot/{0}',
    },
    HGNC: {
        pattern: 'http://www.genecards.org/cgi-bin/carddisp.pl?gene={0}',
        preprocessor: (context) => {
            // For dbxrefs in targets, use target.gene_name instead of the dbxref value.
            if (context['@type'][0] === 'Target' && context.gene_name) {
                return { altValue: context.gene_name };
            }
            return {};
        },
    },
    ENSEMBL: {
        pattern: 'http://www.ensembl.org/Homo_sapiens/Gene/Summary?g={0}',
    },
    GeneID: {
        pattern: 'https://www.ncbi.nlm.nih.gov/gene/{0}',
    },
    GEO: {
        pattern: 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}',
        preprocessor: (context, dbxref) => {
            // If the first four characters of the GEO value is "SAMN" then we need to use a
            // different URL pattern.
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
        pattern: 'https://web.expasy.org/cellosaurus/{0}',
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
            // If a target displays its dbxrefs, use the worm stock URL.
            if (context['@type'][0] !== 'Target') {
                return { altUrlPattern: 'http://www.wormbase.org/species/c_elegans/strain/{0}' };
            }
            return {};
        },
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
    RefSeq: {
        pattern: 'https://www.ncbi.nlm.nih.gov/gene/?term={0}',
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
    PGP: {
        pattern: 'https://my.pgp-hms.org/profile_public?hex={0}',
    },
};


/**
 * Convert a dbxref prefix and value to a URL using the same URL patterns as the <DbxrefList>
 * component below. This function does no pre- nor post-processing, so the given prefix and value
 * have to map to a real URL by themselves.
 *
 * @param {string} prefix - dbxref prefix string, like 'HGNC'
 * @param {string} value - String value you'd normally see after the colon in a dbxref
 * @return {string} - URL that the given prefix and value map to, or null if the mapping table doesn't include the given prefix.
 */
export function dbxrefHref(prefix, value) {
    const urlProcessor = dbxrefPrefixMap[prefix];
    if (urlProcessor) {
        return urlProcessor.pattern.replace(/\{0\}/g, encodeURIComponent(value));
    }
    return null;
}


/**
 * Internal component to display one dbxref as a string. It handles calling the pre- and post-
 * processor from `dbxrefPrefixMap` above, and looking up the URL for the given dbxref. It
 * generates either a link with the generated URL for the given dbxref and the dbxref itself as the
 * link text, o just the dbxref in a <span> if we don't have that dbxref in `dbxrefPrefixMap`.
 *
 * @prop {string} dbxref - String containing one dbxref string.
 * @prop {object} context - Object (Experiment, HumanDonor, etc.) containing the dbxref being
 *     displayed.
 */
const DbxrefUrl = (props) => {
    const { dbxref, context } = props;

    // Standard dbxref pattern: {prefix}:{value}. If the dbxref has more than one colon, only the
    // first colon splits the dbxref into `prefix` and `value`. The other colons get included as
    // part of the value. If the dbxref has no colons at all, prefix gets the whole dbxref string
    // and `value` gets the empty string.
    const prefix = dbxref.split(':', 1)[0];
    let value = dbxref.slice(prefix.length + 1);

    // Using the prefix, find the corresponding URL pattern, if any.
    const urlProcessor = dbxrefPrefixMap[prefix];
    if (urlProcessor) {
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
        let url = urlPattern.replace(/\{0\}/g, encodeURIComponent(value));

        // If, after replacing the {0} withx the value, the URL needs further modification, call the
        // caller-provided post-processor with the given dbxref and the generated URL.
        if (urlProcessor.postprocessor) {
            url = urlProcessor.postprocessor(context, dbxref, url);
        }

        // Return the final dbxref as a link.
        return <a href={url}>{dbxref}</a>;
    }

    // The dbxref prefix didn't map to anything we know about, so just display the dbxref as
    // unlinked text.
    return <span>{dbxref}</span>;
};

DbxrefUrl.propTypes = {
    dbxref: PropTypes.string.isRequired, // dbxref string
    context: PropTypes.object.isRequired, // Object that contains the dbxref
};


/**
 * Display a list of dbxrefs as comma-separated links to external sites. The links appear within a
 * <ul><li> list which work within a <dl><dt><dd> list.
 *
 * @prop {array} dbxrefs - Array of dbxref strings. You normally pass the dbxref, external_id,
 *     etc. property here directly.
 * @prop {object} context - Object (Experiment, HumanDonor, etc.) being displayed that contains the
 *     array of dbxrefs. Some dbxref links rely on information in this object, so for consistency
 *     this property is always required though probably rarely used.
 * @prop {string} addClasses - String with space-separated classes that gets added to the <ul> that
 *     contains the displayed list of dbxrefs. Optional.
 */
export const DbxrefList = (props) => {
    const { dbxrefs, context, addClasses } = props;

    return (
        <ul className={addClasses}>
            {dbxrefs.map((dbxref, i) =>
                <li key={i}><DbxrefUrl dbxref={dbxref} context={context} /></li>
            )}
        </ul>
    );
};

DbxrefList.propTypes = {
    dbxrefs: PropTypes.array.isRequired, // Array of dbxref values to display
    context: PropTypes.object.isRequired, // Object containing the dbxref
    addClasses: PropTypes.string, // CSS class to apply to dbxref list
};

DbxrefList.defaultProps = {
    addClasses: '',
};
