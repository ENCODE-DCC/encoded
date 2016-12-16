from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('bigwigcorrelate_quality_metric', '3', '4')
def bigwigcorrelate_quality_metric_3_4(value, system):
    return
