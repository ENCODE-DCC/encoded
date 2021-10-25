import requests


REGISTRY_DATA_SERVICE = 'genomic_data_service'
REGION_SEARCH = '/region-search'

RNAGET_SEARCH_URL = 'https://rnaget.encodeproject.org/rnaget-search/'
RNAGET_REPORT_URL = 'https://rnaget.encodeproject.org/rnaget-report/'


def remote_get(url, **kwargs):
    return requests.get(
        url,
        **kwargs,
    )


def set_status_and_parse_json(response_field, results):
    status_code = results.status_code
    response_field.get_request().response.status_code = status_code
    return results.json()


class GenomicDataService():

    def __init__(self, registry, request):
        self.path = registry.settings.get(REGISTRY_DATA_SERVICE)
        self.request = request

    def region_search(self, assembly, query=None, chrom=None, start=None, end=None, expand_kb=0):
        params = {
            'assembly': assembly,
            'query': query,
            'expand': expand_kb,
            'files_only': True
        }

        if chrom and start and end:
            params.pop('query')
            params['chr']   = chrom
            params['start'] = start
            params['end']   = end

        query_params = '&'.join([f'{k}={params[k]}' for k in params.keys()])

        url = f'{self.path}{REGION_SEARCH}?{query_params}'

        results = requests.get(url, timeout=10).json()

        return results
