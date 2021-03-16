import requests


class GenomicDataService():
    REGISTRY_DATA_SERVICE = 'genomic_data_service'

    RNA_GET_FILTERS = ['assayType', 'annotation']
    RNA_GET_ENDPOINT = '/expressions/bytes'

    def __init__(self, registry, default_search):
        self.path = registry.settings.get(GenomicDataService.REGISTRY_DATA_SERVICE)
        self.default_search = default_search

    def rna_get(self, genes, sort, units='tpm', page=1, filters=[]):
        params = []

        search = self.default_search
        if genes:
            search = ",".join([gene.strip() for gene in genes.split(",")])

        params.append(f"featureIDList={search}")

        if units:
            params.append(f"units={units}")

        if sort:
            params.append(f"sort={sort}")

        if page:
            params.append(f"page={page}")

        for filter_ in GenomicDataService.RNA_GET_FILTERS:
            if filters.get(filter_):
                params.append(f"{filter_}={filters.get(filter_)}")

        url = self.path + GenomicDataService.RNA_GET_ENDPOINT + '?format=json&' + '&'.join(params)

        results = requests.get(url, timeout=3).json()

        return results['expressions'], results['facets'], results['total']
