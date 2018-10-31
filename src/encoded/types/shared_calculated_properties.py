from snovault import calculated_property
from snovault.util import ensurelist
from .assay_data import assay_terms
from urllib.parse import urljoin
from ..vis_defines import (
    vis_format_url,
    browsers_available
    )


class CalculatedBiosampleSlims:
    @calculated_property(condition='biosample_term_id', schema={
        "title": "Organ slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def organ_slims(self, registry, biosample_term_id):
        biosample_term_id = ensurelist(biosample_term_id)
        slims = set()
        for term_id in biosample_term_id:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id]['organs'])
        return list(slims)

    @calculated_property(condition='biosample_term_id', schema={
        "title": "System slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def system_slims(self, registry, biosample_term_id):
        biosample_term_id = ensurelist(biosample_term_id)
        slims = set()
        for term_id in biosample_term_id:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id]['systems'])
        return list(slims)

    @calculated_property(condition='biosample_term_id', schema={
        "title": "Developmental slims",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def developmental_slims(self, registry, biosample_term_id):
        biosample_term_id = ensurelist(biosample_term_id)
        slims = set()
        for term_id in biosample_term_id:
            if term_id in registry['ontology']:
                slims.update(registry['ontology'][term_id]['developmental'])
        return list(slims)


class CalculatedBiosampleSynonyms:
    @calculated_property(condition='biosample_term_id', schema={
        "title": "Biosample synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def biosample_synonyms(self, registry, biosample_term_id):
        biosample_term_id = ensurelist(biosample_term_id)
        syns = set()
        for term_id in biosample_term_id:
            if term_id in registry['ontology']:
                syns.update(registry['ontology'][term_id]['synonyms'])
        return list(syns)


class CalculatedAssaySynonyms:
    @calculated_property(condition='assay_term_id', schema={
        "title": "Assay synonyms",
        "type": "array",
        "items": {
            "type": "string",
        },
    })
    def assay_synonyms(self, registry, assay_term_id):
        assay_term_id = ensurelist(assay_term_id)
        syns = set()
        for term_id in assay_term_id:
            if term_id in registry['ontology']:
                syns.update(registry['ontology'][term_id]['synonyms'] + [
                    registry['ontology'][term_id]['name'],
                ])
        return list(syns)


class CalculatedFileSetBiosample:
    @calculated_property(condition='related_files', schema={
        "title": "Biosample term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_term_name(self, request, related_files):
        return request.select_distinct_values(
            'dataset.biosample_term_name', *related_files)

    @calculated_property(define=True, condition='related_files', schema={
        "title": "Biosample term id",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_term_id(self, request, related_files):
        return request.select_distinct_values(
            'dataset.biosample_term_id', *related_files)

    @calculated_property(condition='related_files', schema={
        "title": "Biosample type",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_type(self, request, related_files):
        return request.select_distinct_values(
            'dataset.biosample_type', *related_files)

    @calculated_property(condition='related_files', schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Organism"
        },
    })
    def organism(self, request, related_files):
        return request.select_distinct_values(
            'replicate.library.biosample.organism', *related_files)


class CalculatedFileSetAssay:
    @calculated_property(define=True, condition='related_files', schema={
        "title": "Assay term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_name(self, request, related_files):
        return request.select_distinct_values(
            'dataset.assay_term_name', *related_files)

    @calculated_property(define=True, condition='assay_term_name', schema={
        "title": "Assay term id",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_id(self, request, assay_term_name):
        return [
            assay_terms.get(x)
            for x in assay_term_name
            if assay_terms.get(x)
        ]


class CalculatedSeriesAssay:
    @calculated_property(condition='related_datasets', schema={
        "title": "Assay term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_name(self, request, related_datasets):
        return request.select_distinct_values(
            'assay_term_name', *related_datasets)

    @calculated_property(define=True, condition='related_datasets', schema={
        "title": "Assay term id",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def assay_term_id(self, request, related_datasets):
        return request.select_distinct_values(
            'assay_term_id', *related_datasets)


class CalculatedSeriesBiosample:
    @calculated_property(condition='related_datasets', schema={
        "title": "Biosample term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_term_name(self, request, related_datasets):
        return request.select_distinct_values(
            'biosample_term_name', *related_datasets)

    @calculated_property(define=True, condition='related_datasets', schema={
        "title": "Biosample term id",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_term_id(self, request, related_datasets):
        return request.select_distinct_values(
            'biosample_term_id', *related_datasets)

    @calculated_property(condition='related_datasets', schema={
        "title": "Biosample type",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def biosample_type(self, request, related_datasets):
        return request.select_distinct_values(
            'biosample_type', *related_datasets)

    @calculated_property(condition='related_datasets', schema={
        "title": "Organism",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Organism"
        },
    })
    def organism(self, request, related_datasets):
        return request.select_distinct_values(
            'replicates.library.biosample.organism', *related_datasets)


class CalculatedSeriesTreatment:
    @calculated_property(condition='related_datasets', schema={
        "title": "Treatment term name",
        "type": "array",
        "items": {
            "type": 'string',
        },
    })
    def treatment_term_name(self, request, related_datasets):
        return request.select_distinct_values(
            'replicates.library.biosample.treatments.treatment_term_name',
            *related_datasets)


class CalculatedSeriesTarget:
    @calculated_property(condition='related_datasets', schema={
        "title": "Target",
        "type": "array",
        "items": {
            "type": 'string',
            "linkTo": "Target",
        },
    })
    def target(self, request, related_datasets):
        return request.select_distinct_values('target', *related_datasets)


class CalculatedAssayTermID:
    @calculated_property(condition='assay_term_name', schema={
        "title": "Assay ID",
        "description": "OBI (Ontology for Biomedical Investigations) ontology identifier for the assay.",
        "type": "string",
        "comment": "Calculated based on the choice of assay_term_name"
    })
    def assay_term_id(self, request, assay_term_name):
        term_id = None
        if assay_term_name in assay_terms:
            term_id = assay_terms.get(assay_term_name)
        return term_id

class CalculatedVisualize:
    @calculated_property(condition='hub', category='page', schema={
        "title": "Visualize Data",
        "type": "string",
    })
    def visualize(self, request, hub, accession, assembly, status, files):
        hub_url = urljoin(request.resource_url(request.root), hub)
        viz = {}
        vis_assembly = set()
        viewable_file_formats = ['bigWig', 'bigBed']
        viewable_file_status = ['released', 'in progress']
        vis_assembly = {
            properties['assembly']
            for properties in files
            if properties.get('file_format') in viewable_file_formats
            if properties.get('status') in viewable_file_status
            if 'assembly' in properties
        }
        for assembly_name in vis_assembly:
            if assembly_name in viz:
                continue
            browsers = browsers_available(status, [assembly_name],
                                          self.base_types, self.item_type,
                                          files, accession, request)
            if len(browsers) == 0:
                continue
            browser_urls = {}
            if 'ucsc' in browsers:
                ucsc_url = vis_format_url("ucsc", hub_url, assembly_name)
                if ucsc_url is not None:
                    browser_urls['UCSC'] = ucsc_url
            if 'ensembl' in browsers:
                ensembl_url = vis_format_url("ensembl", hub_url, assembly_name)
                if ensembl_url is not None:
                    browser_urls['Ensembl'] = ensembl_url
            if 'quickview' in browsers:
                quickview_url = vis_format_url("quickview", request.path, assembly_name)
                if quickview_url is not None:
                    browser_urls['Quick View'] = quickview_url
            if browser_urls:
                viz[assembly_name] = browser_urls
        if viz:
            return viz
        else:
            return None

