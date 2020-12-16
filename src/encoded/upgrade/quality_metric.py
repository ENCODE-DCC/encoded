from pyramid.traversal import find_root
from uuid import UUID
from snovault import upgrade_step
import re
from .shared import ENCODE2_AWARDS, REFERENCES_UUID

@upgrade_step('bismark_quality_metric', '8', '9')
@upgrade_step('chipseq_filter_quality_metric', '7', '8')
@upgrade_step('complexity_xcorr_quality_metric', '7', '8')
@upgrade_step('correlation_quality_metric', '7', '8')
@upgrade_step('cpg_correlation_quality_metric', '7', '8')
@upgrade_step('duplicates_quality_metric', '6', '7')
@upgrade_step('edwbamstats_quality_metric', '7', '8')
@upgrade_step('filtering_quality_metric', '7', '8')
@upgrade_step('gencode_category_quality_metric', '1', '2')
@upgrade_step('generic_quality_metric', '7', '8')
@upgrade_step('histone_chipseq_quality_metric', '1', '2')
@upgrade_step('hotspot_quality_metric', '7', '8')
@upgrade_step('idr_quality_metric', '6', '7')
@upgrade_step('idr_summary_quality_metric', '7', '8')
@upgrade_step('long_read_rna_mapping_quality_metric', '1', '2')
@upgrade_step('long_read_rna_quantification_quality_metric', '1', '2')
@upgrade_step('mad_quality_metric', '6', '7')
@upgrade_step('micro_rna_mapping_quality_metric', '1', '2')
@upgrade_step('micro_rna_quantification_quality_metric', '1', '2')
@upgrade_step('samtools_flagstats_quality_metric', '7', '8')
@upgrade_step('samtools_stats_quality_metric', '7', '8')
@upgrade_step('star_quality_metric', '7', '8')
@upgrade_step('trimming_quality_metric', '7', '8')
def quality_metric_0_1(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-4711
    if value.get('assay_term_name'):
	    if value.get('assay_term_name') == 'single-nuclei ATAC-seq':
	        value['assay_term_name'] = 'single-nucleus ATAC-seq'