from snovault.elasticsearch.searches.parsers import QueryString


class BatchedSearchGenerator:

    SEARCH_PATH = '/search/'
    DEFAULT_PARAMS = [
        ('limit', 'all')
    ]

    def __init__(self, request, batch_field='@id', batch_size=5000):
        self.request = request
        self.batch_field = batch_field
        self.batch_size = batch_size
        self.query_string = QueryString(request)
        self.param_list = self.query_string.group_values_by_key()
        self.batch_param_values = self.param_list.get(batch_field, []).copy()

    def _make_batched_values_from_batch_param_values(self):
        end = len(self.batch_param_values)
        for start in range(0, end, self.batch_size):
            yield self.batch_param_values[start:min(start + self.batch_size, end)]

    def _make_batched_params_from_batched_values(self, batched_values):
        return [
            (self.batch_field, batched_value)
            for batched_value in batched_values
        ]

    def _build_new_request(self, batched_params):
        self.query_string.drop('limit')
        self.query_string.drop(self.batch_field)
        self.query_string.extend(
            batched_params + self.DEFAULT_PARAMS
        )
        request = self.query_string.get_request_with_new_query_string()
        request.path_info = self.SEARCH_PATH
        request.registry = self.request.registry
        return request

    def results(self):
        if not self.batch_param_values:
            yield from search_generator(self._build_new_request([]))['@graph']
        for batched_values in self._make_batched_values_from_batch_param_values():
            batched_params = self._make_batched_params_from_batched_values(batched_values)
            request = self._build_new_request(batched_params)
            yield from search_generator(request)['@graph']
