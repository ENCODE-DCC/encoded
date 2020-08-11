from encoded.reports.constants import BATCH_DOWNLOAD_COLUMN_TO_FIELDS_MAPPING
from encoded.reports.constants import METADATA_LINK
from encoded.reports.constants import AT_IDS_AS_JSON_DATA_LINK
from encoded.reports.metadata import MetadataReport


class BatchDownloadMixin:

    DEFAULT_PARAMS = [
        ('limit', 'all'),
        ('field', 'files.href'),
        ('field', 'files.restricted'),
        ('field', 'files.file_format'),
        ('field', 'files.file_format_type'),
        ('field', 'files.status'),
        ('field', 'files.assembly'),
    ]

    def _build_header(self):
        for column in self._get_column_to_fields_mapping():
            if column not in self.EXCLUDED_COLUMNS:
                self.header.append(column)

    def _get_column_to_fields_mapping(self):
        return BATCH_DOWNLOAD_COLUMN_TO_FIELDS_MAPPING

    def _maybe_add_json_elements_to_metadata_link(self, metadata_link):
        at_ids = self._get_json_elements_or_empty_list()
        if at_ids:
            return metadata_link + AT_IDS_AS_JSON_DATA_LINK.format(
                ', '.join(
                    (
                        f'"{at_id}"'
                        for at_id in at_ids
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


class BatchDownload(MetadataReport, BatchDownloadMixin):

    def _generate_rows(self):
        yield self.csv.writerow(self._get_metadata_link())
        for experiment in self._get_search_results_generator()['@graph']:
            if not experiment.get('files', []):
                continue
            for file_ in experiment.get('files', []):
                if self._should_not_report_file(file_):
                    continue
                file_data = self._get_file_data(file_)
                yield self.csv.writerow(
                    self._output_sorted_row({}, file_data)
                )
