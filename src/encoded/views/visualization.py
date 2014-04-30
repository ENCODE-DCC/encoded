from pyramid.view import view_config
from ..contentbase import Item
from ..validation import ValidationFailure


class ExperimentWithFiles(Item):
    """ Item base class with attachment blob
    """
    download_property = 'attachment'

    @classmethod
    def _process_downloads(cls, properties, sheets):
        return properties, sheets

    @classmethod
    def create(cls, parent, uuid, properties, sheets=None):
        properties, sheets = cls._process_downloads(properties, sheets)
        item = super(ExperimentWithFiles, cls).create(
            parent, uuid, properties, sheets)
        return item

    def update(self, properties, sheets=None):
        prop_name = self.download_property
        attachment = properties.get(prop_name, {})
        href = attachment.get('href', None)
        if href is not None:
            if href.startswith('@@visualize/'):
                try:
                    existing = self.properties[prop_name]['href']
                except KeyError:
                    existing = None
                if existing != href:
                    msg = "Expected data uri or existing uri."
                    raise ValidationFailure('body', [prop_name, 'href'], msg)
            else:
                properties, sheets = self._process_downloads(
                    properties, sheets)

        super(ExperimentWithFiles, self).update(properties, sheets)


@view_config(name='visualize', context=ExperimentWithFiles, request_method='GET',
             permission='view', subpath_segments=2)
def visualize(context, request):
    pass
