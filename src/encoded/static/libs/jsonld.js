/**
 * converts ENCODE @context object into a JSON-LD object for browsers to crawl
 */


let baseUrl = 'https://www.encodeproject.org/'; // may change

const _addPublisher = (context) => {
    if (!context) {
        return {};
    }

    return {
        '@type': 'Organization',
        sameAs: baseUrl,
        url: baseUrl,
        description: 'The ENCODE Data Coordination Center (DCC)\'s primary task is to curate, uniformly process and validate the data generated and submitted by ENCODE Consortium members in preparation for release to the scientific community.',
        email: 'encode-help@lists.stanford.edu',
        name: 'The ENCODE Data Coordination Center',
        legalName: 'The Encyclopedia of DNA Elements Data Coordination Center',
        memberOf: {
            '@type': 'EducationalOrganization',
            sameAs: baseUrl,
            legalName: 'Leland Stanford Junior University',
            name: 'Stanford Univeristy',
        },
    };
};

const _mapContextToDistribution = (context, measurementTechnique) => {
    if (!context) {
        return {};
    }

    return {
        name: context.accession,
        contentUrl: `${baseUrl}${context['@id']}`,
        sameAs: `${baseUrl}${context['@id']}`,
        url: `${baseUrl}${context['@id']}`,
        identifier: context.uuid,
        encodingFormat: 'text',
        measurementTechnique,
    };
};

const _mapSourceToSourceOrganization = (source) => {
    if (!source) {
        return {};
    }

    return {
        name: source.title,
        sameAs: source.url,
        description: source.description,
        url: `${baseUrl}${source['@id']}`,
        identifier: source.uuid,
    };
};

const _mapSubmitterToCreator = (submittedBy) => {
    if (!submittedBy) {
        return {};
    }

    return {
        '@type': 'Person',
        identifier: submittedBy.uuid,
        name: submittedBy.title,
        worksFor: {
            '@type': 'EducationalOrganization',
            sameAs: `${baseUrl}${submittedBy.lab}`,
            url: `${baseUrl}${submittedBy.lab}`,
        },
        memberOf: !submittedBy.submits_for ? [] : submittedBy.submits_for.map(submitsFor => ({
            '@type': 'EducationalOrganization',
            url: `${baseUrl}${submitsFor}`,
        })),
    };
};

const jsonldFormatter = (context, url) => {
    baseUrl = url || baseUrl;
    let measurementTechnique = '';

    // set technique
    if (context.target_label) {
        measurementTechnique = context.target_label;
    } else if (context.assay_title) {
        measurementTechnique = `${context.assay_title} (${context.assay_term_id})`;
    } else if (context.annotation_type) {
        measurementTechnique = context.annotation_type;
    }

    const mappedData = {
        '@context': 'http://schema.org/',
        '@type': 'Dataset',
        url: `${baseUrl}${context['@id']}`,
        dateCreated: context.date_created,
        license: `${baseUrl}/help/citing-encode/`,
        name: context.accession, // required by Google data set
        isAccessibleForFree: true,
        isFamilyFriendly: true,
        identifier: context.uuid,
        version: context.schema_version,
        publisher: _addPublisher(context),
        distribution: _mapContextToDistribution(context, measurementTechnique),
        keywords: [...context.internal_tags, ...[measurementTechnique, context.accession, context.uuid, 'ENCODE', 'ENCODED', 'DCC', 'Encyclopedia of DNA Elements']],
        measurementTechnique,
        includedInDataCatalog: {
            '@type': 'DataCatalog',
            name: 'ENCODE: Encyclopedia of DNA Elements',
            url: `${baseUrl}`,
        },
    };

    // set description
    if (context['@type'].some(type => type.toLowerCase() === 'annotation')) {
        mappedData.description = context.annotation_type;
    } else if (context['@type'].some(type => type.toLowerCase() === 'experiment' || type.toLowerCase() === 'functionalcharacterizationexperiment')) {
        mappedData.description = context.target_label ?
        `[${context.target_label}] ${context.assay_title} ${context.biosample_summary}`.trim() :
        `${context.assay_title} ${context.biosample_summary}`.trim();
    } else {
        mappedData.description = context.summary || context.description;
    }

    if (context.source) {
        mappedData.sourceOrganization = _mapSourceToSourceOrganization(context.source);
    }

    if (context.submitted_by) {
        mappedData.creator = _mapSubmitterToCreator(context.submitted_by);
    }

    return mappedData;
};

export default jsonldFormatter;
