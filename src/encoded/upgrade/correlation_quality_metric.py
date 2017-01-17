from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('correlation_quality_metric', '3', '4')
def correlation_quality_metric_3_4(value, system):
    return
