from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('trimming_quality_metric', '3', '4')
def trimming_quality_metric_3_4(value, system):
    return
