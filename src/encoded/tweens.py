from pkg_resources import resource_string


def html_wrapper_tween_factory(handler, registry):

    index_html = resource_string('encoded', 'index.html')

    def html_wrapper_tween(request):
        '''Wrap the returned json with the single page html
        '''

        response = handler(request)
        if response.content_type == 'application/json':
            ## Later include the json in the page
            # json_string = response.body
            response.body = index_html
            response.content_type = 'text/html; charset=utf-8'

        return response

    return html_wrapper_tween
