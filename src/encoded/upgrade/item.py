from snovault import upgrade_step
import re


@upgrade_step('experiment', '10', '11')
@upgrade_step('human_donor', '6', '7')
@upgrade_step('mouse_donor', '6', '7')
@upgrade_step('analysis_step', '4', '5')
@upgrade_step('antibody_lot', '6', '7')
@upgrade_step('award', '3', '4')
@upgrade_step('biosample', '14', '15')
@upgrade_step('document', '6', '7')
@upgrade_step('genetic_modification', '3', '4')
@upgrade_step('lab', '3', '4')
@upgrade_step('library', '6', '7')
@upgrade_step('organism', '2', '3')
@upgrade_step('platform', '4', '5')
@upgrade_step('publication', '3', '4')
@upgrade_step('software', '3', '4')
@upgrade_step('software_version', '2', '3')
@upgrade_step('source', '3', '4')
@upgrade_step('target', '4', '5')
@upgrade_step('treatment', '6', '7')
@upgrade_step('user', '4', '5')
def item_alias_tighten(value, system):
    # http://redmine.encodedcc.org/issues/4925
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
                date = "-".join(
                    [date_split[1].strip(), date_split[2].strip(), date_split[5].strip()])
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

        if '"' or '#' or '@' or '^' or '&' or '|' or \
           '~' or '<' or '>' or '?' or '=' or ';' or '`' in rest:
            rest = re.sub(r'[\"#@^&|~<>?=;`\/\\]', '', rest)
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


@upgrade_step('document', '7', '8')
@upgrade_step('genetic_modification', '4', '5')
@upgrade_step('page', '2', '3')
@upgrade_step('image', '1', '2')
@upgrade_step('software', '4', '5')
@upgrade_step('software_version', '3', '4')
@upgrade_step('treatment', '7', '8')
@upgrade_step('user', '5', '6')
@upgrade_step('platform', '5', '6')
@upgrade_step('organism', '3', '4')
@upgrade_step('lab', '4', '5')
@upgrade_step('award', '4', '5')
@upgrade_step('source', '4', '5')
def item_shared_statuses(value, system):
    # http://redmine.encodedcc.org/issues/5050

    if value.get('status') == 'replaced':
        value['status'] = 'deleted'
