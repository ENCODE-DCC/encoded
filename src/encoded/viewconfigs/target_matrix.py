"""
# Matrix View
Some Desc

## Inheritance
TargetMatrixView<-BaseView

### BaseView function dependencies
- _format_facets
"""
from pyramid.httpexceptions import HTTPBadRequest  # pylint: disable=import-error
from encoded.viewconfigs.matrix import MatrixView

from encoded.helpers.helper import (
    search_result_actions,
    View_Item)

from snovault.helpers.helper import (  # pylint: disable=import-error
    get_filtered_query,
    get_search_fields,
    set_filters,
    set_facets,
)
from snovault.viewconfigs.base_view import BaseView  # pylint: disable=import-error


class TargetMatrixView(MatrixView):  #pylint: disable=too-few-public-methods
    '''Matrix View'''
    _view_name = 'targetmatrix'
    _factory_name = 'target_matrix'
    _filter_exclusion = [
        'type', 'limit', 'y.limit', 'x.limit', 'mode', 'annotation',
        'format', 'frame', 'datastore', 'field', 'region', 'genome',
        'sort', 'from', 'referrer',
    ]
    def __init__(self, context, request):
        super(TargetMatrixView, self).__init__(
            context,
            request,
            page_name='target matrix',
            filters=[{
                'remove': '/targetmatrix/?type=Experiment&target.investigated_as%21=control',
                'term': 'ChIP-seq',
                'field': 'assay_title'
            }, {
                'remove': '/targetmatrix/?type=Experiment&assay_title=ChIP-seq',
                'term': 'control',
                'field': 'target.investigated_as!'
            }],
        )
        self._view_item = View_Item(request, self._search_base)
        self._facets = []
        self._schema = None
