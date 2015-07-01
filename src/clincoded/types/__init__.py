from contentbase.attachment import ItemWithAttachment
from contentbase.schema_utils import (
    load_schema,
)
from contentbase import (
    calculated_property,
    collection,
)
from pyramid.traversal import find_root
from .base import (
    Item,
    paths_filtered_by_status,
)


def includeme(config):
    config.scan()

### new collections added for handling curation data, 06/19/2015

@collection(
    name='genes',
    unique_key='gene:symbol',
    properties={
        'title': 'HGNC Genes',
        'description': 'List of HGNC genes',
    })
class Gene(Item):
    item_type = 'gene'
    schema = load_schema('clincoded:schemas/gene.json')
    name_key = 'symbol'

@collection(
    name='diseases',
    unique_key='orphaPhenotype:orphaNumber',
    properties={
        'title': 'Orphanet Diseases',
        'description': 'List of Orphanet diseases (phenotypes)',
    })
class OrphaPhenotype(Item):
    item_type = 'orphaPhenotype'
    schema = load_schema('clincoded:schemas/orphaPhenotype.json')
    name_key = 'orphaNumber'

@collection(
    name='articles',
    unique_key='article:pmid',
    properties={
        'title': 'Articles',
        'description': 'List of PubMed articles stored locally',
    })
class Article(Item):
    item_type = 'article'
    schema = load_schema('clincoded:schemas/article.json')
    name_key = 'pmid'

@collection(
    name='gdm',
    unique_key='gdm:gdmid',
    properties={
        'title': 'Gene:Disease:Mode',
        'description': 'List of Gene:Disease:Mode pairs',
    })
class Gdm(Item):
    item_type = 'gdm'
    schema = load_schema('clincoded:schemas/gdm.json')
    name_key = 'gdmid'
    embedded = [
        'geneSymbol',
        'orphaNumber',
        'annotations',
        'annotations.article',
        'annotations.groups',
        'annotations.groups.commonDiagnosis',
        'annotations.groups.otherGenes',
        'annotations.groups.familyIncluded',
        'annotations.groups.familyIncluded.commonDiagnosis',
        'annotations.groups.familyIncluded.individualIncluded',
        'annotations.groups.familyIncluded.individualIncluded.diagnosis',
        'annotations.groups.individualIncluded',
        'annotations.groups.individualIncluded.diagnosis',
        'annotations.families',
        'annotations.families.commonDiagnosis',
        'annotations.families.individualIncluded',
        'annotations.families.individualIncluded.diagnosis',
        'annotations.individuals',
        'annotations.groups.individuals.diagnosis',
    ]

@collection(
    name='evidences',
    unique_key='annotation:annotationid',
    properties={
        'title': 'Evidences',
        'description': 'List of evidences in all G:D:M pairs',
    })
class Annotation(Item):
    item_type = 'annotation'
    schema = load_schema('clincoded:schemas/annotation.json')
    name_key = 'annotationid'
    embedded = [
        'article',
        'groups',
        'groups.commonDiagnosis',
        'groups.otherGenes',
        'groups.familyIncluded',
        'groups.familyIncluded.commonDiagnosis',
        'group.familyIncluded.individualIncluded',
        'group.familyIncluded.individualIncluded.diagnosis',
        'groups.individualIncluded',
        'groups.individualIncluded.diagnosis',
        'families',
        'families.commonDiagnosis',
        'families.individualIncluded',
        'families.individualIncluded.diagnosis',
        'individuals',
        'individuals.diagnosis',
    ]

@collection(
    name='groups',
    unique_key='group:groupid',
    properties={
        'title': 'Groups',
        'description': 'List of groups in the evidence',
    })
class Group(Item):
    item_type = 'group'
    schema = load_schema('clincoded:schemas/group.json')
    name_key = 'groupid'
    embedded = [
        'commonDiagnosis',
        'otherGenes',
        'familyIncluded',
        'familyIncluded.commonDiagnosis',
        'familyIncluded.individualIncluded',
        'familyIncluded.individualIncluded.diagnosis',
        'individualIncluded',
        'individualIncluded.diagnosis'
    ]

@collection(
    name='families',
    unique_key='family:familyid',
    properties={
        'title': 'Families',
        'description': 'List of families in the evidence/group',
    })
class Family(Item):
    item_type = 'family'
    schema = load_schema('clincoded:schemas/family.json')
    name_key = 'familyid'
    embedded = [
        'commonDiagnosis',
        'individualIncluded',
        'individualIncluded.diagnosis'
    ]

@collection(
    name='individuals',
    unique_key='individual:individualid',
    properties={
        'title': 'Individuals',
        'description': 'List of individuals in the evidence, group, and/or family in the gene:disease:mode pair',
    })
class Individual(Item):
    item_type = 'individual'
    schema = load_schema('clincoded:schemas/individual.json')
    name_key = 'individualid'
    embedded = ['diagnosis']

### end of new collections for curation data


@collection(
    name='labs',
    unique_key='lab:name',
    properties={
        'title': 'Labs',
        'description': 'Listing of ENCODE DCC labs',
    })
class Lab(Item):
    item_type = 'lab'
    schema = load_schema('clincoded:schemas/lab.json')
    name_key = 'name'
    embedded = ['awards']


@collection(
    name='awards',
    unique_key='award:name',
    properties={
        'title': 'Awards (Grants)',
        'description': 'Listing of awards (aka grants)',
    })
class Award(Item):
    item_type = 'award'
    schema = load_schema('clincoded:schemas/award.json')
    name_key = 'name'


@collection(
    name='organisms',
    unique_key='organism:name',
    properties={
        'title': 'Organisms',
        'description': 'Listing of all registered organisms',
    })
class Organism(Item):
    item_type = 'organism'
    schema = load_schema('clincoded:schemas/organism.json')
    name_key = 'name'


@collection(
    name='sources',
    unique_key='source:name',
    properties={
        'title': 'Sources',
        'description': 'Listing of sources and vendors for ENCODE material',
    })
class Source(Item):
    item_type = 'source'
    schema = load_schema('clincoded:schemas/source.json')
    name_key = 'name'


@collection(
    name='documents',
    properties={
        'title': 'Documents',
        'description': 'Listing of Biosample Documents',
    })
class Document(ItemWithAttachment, Item):
    item_type = 'document'
    schema = load_schema('clincoded:schemas/document.json')
    embedded = ['lab', 'award', 'submitted_by']


@collection(
    name='publications',
    unique_key='publication:identifier',
    properties={
        'title': 'Publications',
        'description': 'Publication pages',
    })
class Publication(Item):
    item_type = 'publication'
    schema = load_schema('clincoded:schemas/publication.json')
    embedded = ['datasets']

    def unique_keys(self, properties):
        keys = super(Publication, self).unique_keys(properties)
        if properties.get('identifiers'):
            keys.setdefault('alias', []).extend(properties['identifiers'])
        return keys

    @calculated_property(condition='date_published', schema={
        "title": "Publication year",
        "type": "string",
    })
    def publication_year(self, date_published):
        return date_published.partition(' ')[0]


@collection(
    name='software',
    unique_key='software:name',
    properties={
        'title': 'Software',
        'description': 'Software pages',
    })
class Software(Item):
    item_type = 'software'
    schema = load_schema('clincoded:schemas/software.json')
    name_key = 'name'
    embedded = [
        'references',
        'versions'
    ]
    rev = {
        'versions': ('software_version', 'software')
    }

    @calculated_property(schema={
        "title": "Versions",
        "type": "array",
        "items": {
            "type": "string",
            "linkTo": "software_version",
        },
    })
    def versions(self, request, versions):
        return paths_filtered_by_status(request, versions)


@collection(
    name='software-versions',
    properties={
        'title': 'Software version',
        'description': 'Software version pages',
    })
class SoftwareVersion(Item):
    item_type = 'software_version'
    schema = load_schema('clincoded:schemas/software_version.json')
    embedded = ['software', 'software.references']

    def __ac_local_roles__(self):
        # Use lab/award from parent software object for access control.
        properties = self.upgrade_properties()
        root = find_root(self)
        software = root.get_by_uuid(properties['software'])
        return software.__ac_local_roles__()
