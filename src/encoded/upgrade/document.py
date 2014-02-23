from ..migrator import upgrade_step


def fix_reference(value):
    if not isinstance(value, basestring):
        raise ValueError(value)
    return value.replace('PUBMED:', 'PMID:').replace(' ', '')


@upgrade_step('document', '', '1')
def document_0_1(value, system):
    # http://redmine.encodedcc.org/issues/1259
    
    if 'references' in value:
        value['references'] = [fix_reference(v) for v in value['references']]
