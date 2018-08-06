from encoded.vis_defines import vis_format_url


def format_results(request, hits, result=None):
    """
    Loads results to pass onto UI
    """
    fields_requested = request.params.getall('field')
    if fields_requested:
        frame = 'embedded'
    else:
        frame = request.params.get('frame')

    # Request originating from metadata generation will skip to
    # partion of the code that adds audit  object to result items
    if request.__parent__ and '/metadata/' in request.__parent__.url:
        frame = ''

    any_released = False  # While formatting, figure out if any are released.

    if frame in ['embedded', 'object']:
        for hit in hits:
            if not any_released and hit['_source'][frame].get('status', 'released') == 'released':
                any_released = True
            yield hit['_source'][frame]
    else:
        # columns
        for hit in hits:
            item = hit['_source']['embedded']
            if not any_released and item.get('status', 'released') == 'released':
                any_released = True # Not exp? 'released' to do the least harm
            if 'audit' in hit['_source']:
                item['audit'] = hit['_source']['audit']
            if 'highlight' in hit:
                item['highlight'] = {}
                for key in hit['highlight']:
                    item['highlight'][key[9:]] = list(set(hit['highlight'][key]))
            yield item

    # After all are yielded, it may not be too late to change this result setting
    #if not any_released and result is not None and 'batch_hub' in result:
    #    del result['batch_hub']
    if not any_released and result is not None and 'visualize_batch' in result:
        del result['visualize_batch']

def format_facets(es_results, facets, used_filters, schemas, total, principals):
    result = []
    # Loading facets in to the results
    if 'aggregations' not in es_results:
        return result

    aggregations = es_results['aggregations']
    used_facets = set()
    exists_facets = set()
    for field, options in facets:
        used_facets.add(field)
        agg_name = field.replace('.', '-')
        if agg_name not in aggregations:
            continue
        all_buckets_total = aggregations[agg_name]['doc_count']
        if not all_buckets_total > 0:
            continue
        # internal_status exception. Only display for admin users
        if field == 'internal_status' and 'group.admin' not in principals:
            continue
        facet_type = options.get('type', 'terms')
        terms = aggregations[agg_name][agg_name]['buckets']
        if facet_type == 'exists':
            terms = [
                {'key': 'yes', 'doc_count': terms['yes']['doc_count']},
                {'key': 'no', 'doc_count': terms['no']['doc_count']},
            ]
            exists_facets.add(field)
        result.append({
            'type': facet_type,
            'field': field,
            'title': options.get('title', field),
            'terms': terms,
            'total': all_buckets_total
        })

    # Show any filters that aren't facets as a fake facet with one entry,
    # so that the filter can be viewed and removed
    for field, values in used_filters.items():
        if field not in used_facets and field.rstrip('!') not in exists_facets:
            title = field
            for schema in schemas:
                if field in schema['properties']:
                    title = schema['properties'][field].get('title', field)
                    break
            result.append({
                'field': field,
                'title': title,
                'terms': [{'key': v} for v in values],
                'total': total,
            })

    return result

def search_result_actions(request, doc_types, es_results, position=None):
    actions = {}
    aggregations = es_results['aggregations']

    # generate batch hub URL for experiments
    # TODO we could enable them for Datasets as well here, but not sure how well it will work
    if doc_types == ['Experiment'] or doc_types == ['Annotation']:
        viz = {}
        for bucket in aggregations['assembly']['assembly']['buckets']:
            if bucket['doc_count'] > 0:
                assembly = bucket['key']
                if assembly in viz:  # mm10 and mm10-minimal resolve to the same thing
                    continue
                search_params = request.query_string.replace('&', ',,')
                if not request.params.getall('assembly') \
                or assembly in request.params.getall('assembly'):
                    # filter  assemblies that are not selected
                    hub_url = request.route_url('batch_hub', search_params=search_params,
                                                txt='hub.txt')
                    browser_urls = {}
                    pos = None
                    if 'region-search' in request.url and position is not None:
                        pos = position
                    ucsc_url = vis_format_url("ucsc", hub_url, assembly, pos)
                    if ucsc_url is not None:
                        browser_urls['UCSC'] = ucsc_url
                    ensembl_url = vis_format_url("ensembl", hub_url, assembly, pos)
                    if ensembl_url is not None:
                        browser_urls['Ensembl'] = ensembl_url
                    if browser_urls:
                        viz[assembly] = browser_urls
                        #actions.setdefault('visualize_batch', {})[assembly] =\
                                #browser_urls  # formerly 'batch_hub'
        if viz:
            actions.setdefault('visualize_batch', viz)

    # generate batch download URL for experiments
    # TODO we could enable them for Datasets as well here, but not sure how well it will work
    # batch download disabled for region-search results
    if '/region-search/' not in request.url:
        #if (doc_types == ['Experiment'] or doc_types == ['Annotation']) and any(
        if (doc_types == ['Experiment']) and any(
                bucket['doc_count'] > 0
                for bucket in aggregations['files-file_type']['files-file_type']['buckets']):
            actions['batch_download'] = request.route_url(
                'batch_download',
                search_params=request.query_string
            )

    return actions
