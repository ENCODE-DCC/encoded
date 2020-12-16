from snovault import (
    CONNECTION,
    upgrade_step,
)


@upgrade_step('hotspot_quality_metric', '3', '4')
def hotspot_quality_metric_3_4(value, system):
    return


@upgrade_step('hotspot_quality_metric', '4', '5')
def hotspot_quality_metric_4_5(value, system):
    # http://redmine.encodedcc.org/issues/2491
    if 'assay_term_id' in value:
        del value['assay_term_id']

    if 'notes' in value:
        if value['notes']:
            value['notes'] = value['notes'].strip()
        else:
            del value['notes']

@upgrade_step('hotspot_quality_metric', '5', '6')
def hotspot_quality_metric_5_6(value, system):
    # http://redmine.encodedcc.org/issues/4845

    if 'SPOT score' in value:
        value['SPOT2 score'] = value['SPOT score']
        del value['SPOT score']

    # http://redmine.encodedcc.org/issues/4748
    aliases = []
    if 'aliases' in value and value['aliases']:
        aliases = value['aliases']
    else:
        return

    aliases_to_remove = []
    for i in range(0, len(aliases)):
        new_alias = ''
        if 'roadmap-epigenomics' in aliases[i]:
            if '||' in aliases[i]:
                scrub_parts = aliases[i].split('||')
                date_split = scrub_parts[1].split(' ')
                date = "-".join([date_split[1].strip(), date_split[2].strip(), date_split[5].strip()])
                scrubbed_list = [scrub_parts[0].strip(), date.strip(), scrub_parts[2].strip()]
                if len(scrub_parts) == 4:
                    scrubbed_list.append(scrub_parts[3].strip())
                new_alias = '_'.join(scrubbed_list)
        parts = aliases[i].split(':') if not new_alias else new_alias.split(':')
        namespace = parts[0]
        if namespace in ['ucsc_encode_db', 'UCSC_encode_db', 'versionof']:
            # Remove the alias with the bad namespace
            aliases_to_remove.append(aliases[i])
            namespace = 'encode'
        if namespace in ['CGC']:
            namespace = namespace.lower()

        rest = '_'.join(parts[1:]).strip()
        # Remove or substitute bad characters and multiple whitespaces
        
        import re
        if '"' or '#' or '@' or '!' or '$' or '^' or '&' or '|' or '~'  or ';' or '`' in rest:
            rest = re.sub(r'[\"#@!$^&|~;`\/\\]', '', rest)
            rest = ' '.join(rest.split())
        if '%' in rest:
            rest = re.sub(r'%', 'pct', rest)
        if '[' or '{' in rest:
            rest = re.sub('[\[{]', '(', rest)
        if ']' or '}' in rest:
            rest = re.sub('[\]}]', ')', rest)
        
        new_alias = ':'.join([namespace, rest])
        if new_alias not in aliases:
            aliases[i] = new_alias
    
    if aliases_to_remove and aliases:
        for a in aliases_to_remove:
            if a in aliases:
                aliases.remove(a)

@upgrade_step('hotspot_quality_metric', '8', '9')
def hotspot_quality_metric_8_9(value, system):
    # https://encodedcc.atlassian.net/browse/ENCD-5306
    if 'SPOT1 score' in value:
        value['spot1_score'] = value['SPOT1 score']
        del value['SPOT1 score']

    if 'SPOT2 score' in value:
        value['spot2_score'] = value['SPOT2 score']
        del value['SPOT2 score']

    if 'hotspot count' in value:
        value['hotspot_count'] = value['hotspot count']
        del value['hotspot count']

    if 'peaks count' in value:
        value['peaks_count'] = value['peaks count']
        del value['peaks count']

    if 'total tags' in value:
        value['total_tags'] = value['total tags']
        del value['total tags']

    if 'hotspot tags' in value:
        value['hotspot_tags'] = value['hotspot tags']
        del value['hotspot tags']
