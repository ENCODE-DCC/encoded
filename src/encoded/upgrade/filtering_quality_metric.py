from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('filtering_quality_metric', '3', '4')
def filtering_quality_metric_3_4(value, system):
    return
