from ..migrator import upgrade_step


@upgrade_step('lab', '', '2')
def lab_0_2(value, system):
    # http://redmine.encodedcc.org/issues/1295
    # http://redmine.encodedcc.org/issues/1307

    if 'status' in value:
    	value['status'] = value['status'].lower()
    	