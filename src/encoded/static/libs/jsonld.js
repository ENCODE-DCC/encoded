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

    const distribution = {
        name: context.accession,
        contentUrl: `${baseUrl}${context['@id']}`,
        sameAs: `${baseUrl}${context['@id']}`,
        url: `${baseUrl}${context['@id']}`,
        identifier: context.uuid,
        encodingFormat: 'text',
    };

    if (measurementTechnique) {
        distribution.measurementTechnique = measurementTechnique;
    }

    return distribution;
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

const _mapAwardToCreator = (award) => {
    if (!award || !award.pi) {
        return {};
    }

    const { pi } = award;

    return {
        '@type': 'Person',
        identifier: award.uuid,
        name: pi.title,
        worksFor: {
            '@type': 'EducationalOrganization',
            sameAs: `${baseUrl}${pi.lab ? pi.lab['@id'] : ''}`,
            url: `${baseUrl}${pi.lab ? pi.lab['@id'] : ''}`,
        },
        memberOf: !pi.submits_for ? [] : pi.submits_for.map((submitsFor) => ({
            '@type': 'EducationalOrganization',
            url: `${baseUrl}${submitsFor}`,
        })),
    };
};

const jsonldFormatter = (context, url) => {
    if (!context) {
        return {};
    }

    baseUrl = url || baseUrl;
    const isAnnotationDataSet = context['@type'].some((type) => type.toLowerCase() === 'annotation');
    const measurementTechnique = !isAnnotationDataSet ? `${context.assay_title} (${context.assay_term_id})` : '';

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
        keywords: [...context.internal_tags, ...[context.accession, context.uuid, 'ENCODE', 'ENCODED', 'DCC', 'Encyclopedia of DNA Elements']],
        measurementTechnique,
        includedInDataCatalog: {
            '@type': 'DataCatalog',
            name: 'ENCODE: Encyclopedia of DNA Elements',
            url: `${baseUrl}`,
        },
    };

    const partialDescription = [context.award.project, context.award.name, context.lab.title].filter((d) => d !== '').join(' - ');

    // set description
    if (isAnnotationDataSet) {
        const annotationDescription = context.annotation_type !== context.description ?
            `${context.annotation_type} - ${context.description}` :
            context.annotation_type;
        mappedData.description = [annotationDescription, partialDescription].join(' - ');
    } else if (context['@type'].some((type) => type.toLowerCase() === 'experiment' || type.toLowerCase() === 'functionalcharacterizationexperiment')) {
        const targetLabel = context.target && context.target.label ? context.target.label : '';
        const assayTitle = context.assay_title || '';
        const biosampleSummary = context.biosample_summary || '';

        mappedData.description = [targetLabel, assayTitle, biosampleSummary, partialDescription].filter((d) => d !== '').join(' - ');
    } else {
        mappedData.description = `${context.summary || context.description} ${partialDescription}`;
    }

    if (context.source) {
        mappedData.sourceOrganization = _mapSourceToSourceOrganization(context.source);
    }

    if (context.award) {
        mappedData.creator = _mapAwardToCreator(context.award);
    }

    return mappedData;
};

export default jsonldFormatter;
