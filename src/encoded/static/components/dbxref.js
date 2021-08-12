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
    AR: {
        pattern: 'http://antibodyregistry.org/search.php?q={0}',
    },
    ArrayExpress: {
        pattern: 'https://www.ebi.ac.uk/arrayexpress/experiments/{0}',
    },
    BioProject: {
        pattern: 'https://www.ncbi.nlm.nih.gov/bioproject/{0}',
    },
    BioSample: {
        pattern: 'https://www.ncbi.nlm.nih.gov/biosample/{0}',
    },
    BioStudies: {
        pattern: 'https://www.ebi.ac.uk/biostudies/studies/{0}',
    },
    Cellosaurus: {
        pattern: 'https://web.expasy.org/cellosaurus/{0}',
    },
    ComplexPortal: {
        pattern: 'https://www.ebi.ac.uk/complexportal/complex/{0}',
    },
    dbGaP: {
        pattern: 'https://www.ncbi.nlm.nih.gov/projects/gap/cgi-bin/study.cgi?study_id={0}',
    },
    doi: {
        pattern: 'https://doi.org/doi:{0}',
    },
    EGA: {
        pattern: 'https://www.ebi.ac.uk/ega/datasets/{0}',
    },
    ENA: {
        pattern: 'https://www.ebi.ac.uk/ena/browser/view/{0}',
    },
    ENSEMBL: {
        pattern: 'http://www.ensembl.org/Homo_sapiens/Gene/Summary?g={0}',
        preprocessor: (context) => {
            // The URL is for human by default for ENSEMBL dbxrefs.
            if (context.assembly && context.assembly === 'mm10') {
                return { altUrlPattern: 'http://www.ensembl.org/Mus_musculus/Gene/Summary?g={0}' };
            }
            return {};
        },
    },
    GEO: {
        pattern: 'https://www.ncbi.nlm.nih.gov/geo/query/acc.cgi?acc={0}',
    },
    HGNC: {
        pattern: 'https://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id={0}',
    },
    MGI: {
        pattern: 'http://www.informatics.jax.org/marker/MGI:{0}',
    },
    PMID: {
        pattern: 'https://www.ncbi.nlm.nih.gov/pubmed/?term={0}',
    },
    RefSeq: {
        pattern: 'https://www.ncbi.nlm.nih.gov/nuccore/{0}',
    },
    SRA: {
        pattern: 'https://www.ncbi.nlm.nih.gov/sra?term={0}',
        preprocessor: (context, dbxref) => {
            const value = dbxref.split(':');
            if (value[1] && value[1].substr(0, 3) === 'SRR') {
                return { altUrlPattern: 'http://www.ncbi.nlm.nih.gov/Traces/sra/?run={0}' };
            }
            return {};
        },
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
export function dbxrefHref(prefix, value, context) {
    const urlProcessor = dbxrefPrefixMap[prefix];
    if (urlProcessor) {
        let urlPattern = urlProcessor.pattern;
        if (urlProcessor.preprocessor) {
            const { altUrlPattern, altValue } = urlProcessor.preprocessor(context);
            urlPattern = altUrlPattern || urlPattern;
            value = altValue || value;
        }
        return urlPattern.replace(/\{0\}/g, encodeURIComponent(value));
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
