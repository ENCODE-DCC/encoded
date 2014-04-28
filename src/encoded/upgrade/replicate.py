from ..migrator import upgrade_step


@upgrade_step('replicate', '', '3')
def replicate_0_3(value, system):
    # http://redmine.encodedcc.org/issues/1354
   
    if 'paired_ended' in value and 'read_length' not in value:
        del value['paired_ended']