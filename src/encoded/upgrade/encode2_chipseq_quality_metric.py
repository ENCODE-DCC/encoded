from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('encode2_chipseq_quality_metric', '3', '4')
def encode2_chipseq_quality_metric_3_4(value, system):
    return
