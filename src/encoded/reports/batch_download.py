from encoded.reports.constants import BATCH_DOWNLOAD_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import SERIES_BATCH_DOWNLOAD_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import NEW_SERIES_BATCH_DOWNLOAD_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import METADATA_LINK
from encoded.reports.constants import AT_IDS_AS_JSON_DATA_LINK
from encoded.reports.metadata import MetadataReport
from encoded.reports.metadata import PublicationDataMetadataReport
from encoded.reports.metadata import SeriesMetadataReport
from encoded.reports.metadata import NewSeriesMetadataReport
from encoded.reports.constants import METADATA_ALLOWED_TYPES
from encoded.reports.constants import METADATA_SERIES_TYPES
from encoded.reports.decorators import allowed_types
from pyramid.view import view_config
from snosearch.parsers import QueryString


def includeme(config):
    config.add_route('batch_download', '/batch_download{slash:/?}')
    config.scan(__name__)


class BatchDownloadMixin:

    DEFAULT_PARAMS = [
        ('limit', 'all'),
        ('field', 'files.@id'),
        ('field', 'files.href'),
        ('field', 'files.restricted'),
        ('field', 'files.no_file_available'),
        ('field', 'files.file_format'),
        ('field', 'files.file_format_type'),
        ('field', 'files.status'),
        ('field', 'files.assembly'),
    ]
    CONTENT_TYPE = 'text/plain'
    CONTENT_DISPOSITION = 'attachment; filename="files.txt"'

    def _build_header(self):
        for column in self._get_column_to_fields_mapping():
            self.header.append(column)

    def _get_column_to_fields_mapping(self):
        return BATCH_DOWNLOAD_COLUMN_TO_FIELDS_MAPPING

    def _should_add_json_elements_to_metadata_link(self):
        conditions = [
            self._get_json_elements_or_empty_list(),
            not self.query_string.get_key_filters(key='cart')
        ]
        return all(conditions)

    def _maybe_add_json_elements_to_metadata_link(self, metadata_link):
        if self._should_add_json_elements_to_metadata_link():
            return metadata_link + AT_IDS_AS_JSON_DATA_LINK.format(
                ', '.join(
                    (
                        f'"{at_id}"'
                        for at_id in self._get_json_elements_or_empty_list()
                    )
                )
            )
        return metadata_link

    def _get_metadata_link(self):
        metadata_link = METADATA_LINK.format(
            self.request.host_url,
            self.query_string._get_original_query_string()
        )
        return self._maybe_add_json_elements_to_metadata_link(
            metadata_link
        )

    def _get_encoded_metadata_link_with_newline(self):
        return f'{self._get_metadata_link()}\n'.encode('utf-8')


class BatchDownload(BatchDownloadMixin, MetadataReport):

    def _generate_rows(self):
        yield self._get_encoded_metadata_link_with_newline()
        for experiment in self._get_search_results_generator():
            for file_ in experiment.get('files', []):
                if self._should_not_report_file(file_):
                    continue
                file_data = self._get_file_data(file_)
                yield self.csv.writerow(
                    self._output_sorted_row({}, file_data)
                )


class SeriesBatchDownload(BatchDownloadMixin, SeriesMetadataReport):

    DEFAULT_PARAMS = [
        ('field', 'related_datasets.files.@id'),
        ('field', 'related_datasets.files.href'),
        ('field', 'related_datasets.files.restricted'),
        ('field', 'related_datasets.files.no_file_available'),
        ('field', 'related_datasets.files.file_format'),
        ('field', 'related_datasets.files.file_format_type'),
        ('field', 'related_datasets.files.preferred_default'),
        ('field', 'related_datasets.files.status'),
        ('field', 'related_datasets.files.assembly'),
        ('field', 'related_datasets.files.related_datasets'),
        ('limit', 'all'),
    ]
    FILES_PREFIX = 'related_datasets.files.'

    def _get_column_to_fields_mapping(self):
        return SERIES_BATCH_DOWNLOAD_COLUMN_TO_FIELDS_MAPPING

    def _generate_rows(self):
        yield self._get_encoded_metadata_link_with_newline()
        for series in self._get_search_results_generator():
            for related_dataset in series.get('related_datasets', []):
                for file_ in related_dataset.get('files', []):
                    if self._should_not_report_file(file_):
                        continue
                    file_data = self._get_file_data(file_)
                    yield self.csv.writerow(
                        self._output_sorted_row({}, file_data)
                    )


class NewSeriesBatchDownload(NewSeriesMetadataReport):

    _multireports = [
        SeriesBatchDownload,
        BatchDownload,
    ]

    def _get_column_to_fields_mapping(self):
        return NEW_SERIES_BATCH_DOWNLOAD_COLUMN_TO_FIELDS_MAPPING


class PublicationDataBatchDownload(BatchDownloadMixin, PublicationDataMetadataReport):

    DEFAULT_PARAMS = [
        ('limit', 'all'),
        ('field', 'files')
    ]

    def _generate_rows(self):
        yield self._get_encoded_metadata_link_with_newline()
        for experiment in self._get_search_results_generator():
            self.file_at_ids = experiment.get('files', [])
            if not self.file_at_ids:
                continue
            for file_ in self._get_file_search_results_generator():
                if self._should_not_report_file(file_):
                    continue
                file_data = self._get_file_data(file_)
                yield self.csv.writerow(
                    self._output_sorted_row({}, file_data)
                )


def _get_batch_download(context, request):
    batch_download = BatchDownload(request)
    return batch_download.generate()


def _get_publication_data_batch_download(context, request):
    publication_data_batch_download = PublicationDataBatchDownload(request)
    return publication_data_batch_download.generate()


def _get_series_batch_download(context, request):
    new_series_batch_download = NewSeriesBatchDownload(request)
    return new_series_batch_download.generate()


def batch_download_factory(context, request):
    qs = QueryString(request)
    specified_type = qs.get_one_value(
            params=qs.get_type_filters()
    )
    if specified_type == 'PublicationData':
        return _get_publication_data_batch_download(context, request)
    elif specified_type in METADATA_SERIES_TYPES:
        return _get_series_batch_download(context, request)
    else:
        return _get_batch_download(context, request)


@view_config(route_name='batch_download', request_method=['GET', 'POST'])
@allowed_types(METADATA_ALLOWED_TYPES)
def batch_download(context, request):
    return batch_download_factory(context, request)
