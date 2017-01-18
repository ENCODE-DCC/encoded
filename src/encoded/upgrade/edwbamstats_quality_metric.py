from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('edwbamstats_quality_metric', '3', '4')
def edwbamstats_quality_metric_3_4(value, system):
    return
