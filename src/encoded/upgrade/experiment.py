from pyramid.traversal import find_root
from uuid import UUID
from ..migrator import upgrade_step
import re
from ..views.views import ENCODE2_AWARDS


@upgrade_step('experiment', '4', '5')
def experiment_4_5(value, system):

	# http://redmine.encodedcc.org/issues/1393
    if value.get('biosample_type') == 'primary cell line':
        value['biosample_type'] = 'primary cell'
