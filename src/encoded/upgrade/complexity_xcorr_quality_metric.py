from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('complexity_xcorr_quality_metric', '3', '4')
def complexity_xcorr_quality_metric_3_4(value, system):
    return
