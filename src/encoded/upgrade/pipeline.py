from contentbase.upgrader import upgrade_step


@upgrade_step('pipeline', '', '2')
def pipeline_0_2(value, system):
    # http://redmine.encodedcc.org/issues/3001

    value['lab'] = "/labs/encode-processing-pipeline/"
    value['award'] = "/awards/ENCODE3/"
