from snovault import upgrade_step


@upgrade_step('gene', '1', '2')
def gene_1_2(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5005
    # go_annotations are replaced by a link on UI to GO
    value.pop('go_annotations', None)
