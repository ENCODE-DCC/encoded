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
            // For dbxrefs in targets, use the symbol of the first gene in target.genes instead of the dbxref value.
            if (context['@type'][0] === 'Target' && context.genes && context.genes.length > 0) {
                return { altValue: context.genes[0].symbol };
            }
            // If a gene displays its dbxrefs, use HGNC URL as NCBI Entrez does.
            if (context['@type'][0] === 'Gene') {
                return { altUrlPattern: 'https://www.genenames.org/cgi-bin/gene_symbol_report?hgnc_id={0}' };
            }
            return {};
        },
    },
    ENSEMBL: {
        pattern: 'http://www.ensembl.org/Homo_sapiens/Gene/Summary?g={0}',
        preprocessor: (context) => {
            // The URL is for human by default for ENSEMBL dbxrefs.
            if (context.organism && context.organism.scientific_name === 'Mus musculus') {
                return { altUrlPattern: 'http://www.ensembl.org/Mus_musculus/Gene/Summary?g={0}' };
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
    FactorBook: {
        pattern: 'https://factorbook.org/experiment/{0}',
        preprocessor: (context, dbxref) => {
            // For dbxrefs in targets use an alternate URL for human targets.
            const value = dbxref.split(':');
            if (context['@type'][0] === 'Target' && context.organism && context.organism.scientific_name === 'Homo sapiens') {
                return { altUrlPattern: 'https://factorbook.org/tf/human/{0}/function' };
            }
            // For dbxrefs in targets use an alternate URL and alternate value for mouse targets.
            if (context['@type'][0] === 'Target' && context.organism && context.organism.scientific_name === 'Mus musculus') {
                return { altValue: value[1].charAt(0) + value[1].slice(1).toLowerCase(),
                    altUrlPattern: 'https://factorbook.org/tf/mouse/{0}/function' };
            }
            return {};
        },
    },
    FlyBase: {
        pattern: 'http://flybase.org/search/symbol/{0}',
        preprocessor: (context) => {
            // If a target displays its dbxrefs, use the fly stock URL.
            if (context['@type'][0] !== 'Target') {
                return { altUrlPattern: 'http://flybase.org/reports/{0}.html' };
            }
            return {};
        },
    },
    BDSC: {
        pattern: 'http://flystocks.bio.indiana.edu/stocks/{0}',
    },
    WormBase: {
        pattern: 'http://www.wormbase.org/species/c_elegans/gene/{0}',
        preprocessor: (context) => {
            // If a target or gene displays its dbxrefs, use the worm stock URL.
            if (context['@type'][0] !== 'Target' && context['@type'][0] !== 'Gene') {
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
    MGI: {
        pattern: 'http://www.informatics.jax.org/marker/MGI:{0}',
    },
    RBPImage: {
        pattern: 'http://rnabiology.ircm.qc.ca/RBPImage/gene.php?cells={1}&targets={0}',
        postprocessor: (context, dbxref, urlPattern) => (
            // Experiments with RBPImage need to replace one urlPattern element with
            // BiosampleType term_name.
            (context['@type'][0] === 'Experiment' ? urlPattern.replace(/\{1\}/g, context.biosample_ontology.term_name) : urlPattern)
        ),
    },
    RefSeq: {
        pattern: 'https://www.ncbi.nlm.nih.gov/nuccore/{0}',
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
        pattern: 'https://doi.org/doi:{0}',
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
    TRiP: {
        pattern: 'http://www.flyrnai.org/cgi-bin/DRSC_gene_lookup.pl?gname={0}',
    },
    DGGR: {
        pattern: 'https://kyotofly.kit.jp/cgi-bin/stocks/search_res_det.cgi?DB_NUM=1&DG_NUM={0}',
    },
    MIM: {
        pattern: 'https://www.ncbi.nlm.nih.gov/omim/{0}',
    },
    Vega: {
        pattern: 'http://vega.sanger.ac.uk/id/{0}',
    },
    miRBase: {
        pattern: 'http://www.mirbase.org/cgi-bin/mirna_entry.pl?acc={0}',
    },
    GO: {
        pattern: 'http://amigo.geneontology.org/amigo/term/GO:{0}',
    },
    GOGene: {
        pattern: 'http://amigo.geneontology.org/amigo/gene_product/{0}',
    },
    'IMGT/GENE-DB': {
        pattern: 'http://www.imgt.org/IMGT_GENE-DB/GENElect?species=Homo+sapiens&query=2+{0}',
    },
    SRA: {
        pattern: 'http://www.ncbi.nlm.nih.gov/Traces/sra/?run={0}',
    },
    '4DN': {
        pattern: 'https://data.4dnucleome.org/experiment-set-replicates/{0}',
    },
    DepMap: {
        pattern: 'https://depmap.org/portal/cell_line/{0}',
    },
    GeneCards: {
        pattern: 'http://www.genecards.org/cgi-bin/carddisp.pl?gene={0}',
    },
    VISTA: {
        pattern: 'https://enhancer.lbl.gov/cgi-bin/imagedb3.pl?form=presentation&show=1&experiment_id={0}&organism_id=1',
        preprocessor: (context, dbxref) => {
            const value = dbxref.split(':');
            // Check to see if the first two characters of the VISTA value is "hs"
            if (value[1] && value[1].substr(0, 2) === 'hs') {
                return { altValue: value[1].substr(2) };
            }
            // If the first two characters of the VISTA value is "mm" then we need to use a
            // different URL pattern.
            if (value[1] && value[1].substr(0, 2) === 'mm') {
                return { altUrlPattern: 'https://enhancer.lbl.gov/cgi-bin/imagedb3.pl?form=presentation&show=1&experiment_id={0}&organism_id=2', altValue: value[1].substr(2) };
            }
            return {};
        },
    },
    'SCREEN-GRCh38': {
        pattern: 'https://screen.encodeproject.org/search?q={0}&assembly=GRCh38',
    },
    'SCREEN-mm10': {
        pattern: 'https://screen.encodeproject.org/search?q={0}&assembly=mm10',
    },
};


/**
 * Convert a dbxref identifier to a URL. Consider the context optional if you know your particular
 * dbxref doesn't require it.
 * @param {string} dbxref Dbxref identifier including the prefix
 * @param {string} context Object containing the dbxref. Optional in some cases
 *
 * @return {string} URL that the given identifier maps to; empty string if identifier not supported
 */
export function dbxrefHref(dbxref, context) {
    let url = '';
    const prefix = dbxref.split(':', 1)[0];
    let value = dbxref.slice(prefix.length + 1);

    // Using the dbxref prefix, find the corresponding URL pattern, if any.
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
        url = urlPattern.replace(/\{0\}/g, encodeURIComponent(value));

        // If, after replacing the {0} with the value, the URL needs further modification, call the
        // caller-provided post-processor with the given dbxref and the generated URL.
        if (urlProcessor.postprocessor) {
            url = urlProcessor.postprocessor(context, dbxref, url);
        }
    }
    return url;
}


/**
 * Display one dbxref, generating either a link with the URL for the given dbxref and the dbxref
 * itself as the link text, or just the dbxref in
 * a <span> if we don't have that dbxref in `dbxrefPrefixMap`.
 */
export const DbxrefItem = ({ dbxref, context, title }) => {
    const displayTitle = title || dbxref;

    const url = dbxrefHref(dbxref, context);
    return url
        ? <a href={url}>{displayTitle}</a>
        : <span>{dbxref}</span>;
};

DbxrefItem.propTypes = {
    /** dbxref identifier */
    dbxref: PropTypes.string.isRequired,
    /** Object that contains the dbxref */
    context: PropTypes.object.isRequired,
    /** title string displayed instead of dbxref string */
    title: PropTypes.string,
};

DbxrefItem.defaultProps = {
    title: '',
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
 * @prop {title} title - String that is displayed instead of Dbxref string. Optional.
 */
export const DbxrefList = (props) => {
    const { dbxrefs, context, addClasses, title } = props;

    return (
        <ul className={addClasses}>
            {dbxrefs.map((dbxref, i) => (
                <li key={i}><DbxrefItem dbxref={dbxref} context={context} title={title} /></li>
            ))}
        </ul>
    );
};

DbxrefList.propTypes = {
    dbxrefs: PropTypes.array.isRequired, // Array of dbxref values to display
    context: PropTypes.object.isRequired, // Object containing the dbxref
    addClasses: PropTypes.string, // CSS class to apply to dbxref list
    title: PropTypes.string, // title string displayed instead of dbxref string
};

DbxrefList.defaultProps = {
    addClasses: '',
    title: '',
};
