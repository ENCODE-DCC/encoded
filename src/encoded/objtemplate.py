import inspect
__all__ = ['ObjectTemplate']
_marker = object()
TEMPLATE_NAMES = ('$templated', '$repeat', '$condition', '$value')


class ObjectTemplate(object):
    """ Templates for JSON structures.

    An ObjectTemplate
    """
    def __init__(self, template):
        self.template = template

    def __call__(self, namespace):
        result, = list(object_template(self.template, namespace))
        return result


def string_template(template, namespace):
    return unicode(template).format(**namespace)


def list_template(template, namespace):
    result = type(template)()
    for value in template:
        result.extend(object_template(value, namespace))
    return result


def dict_template(template, namespace):
    templated = template.get('$templated', [])
    if isinstance(templated, basestring):
        templated = templated.split()
    condition = template.get('$condition', _marker)
    if condition is not _marker:
        arg = None
        if isinstance(condition, basestring):
            if ':' in condition:
                condition, arg = condition.split(':', 1)
            condition = namespace.get(condition, _marker)
            if condition is _marker:
                return
        if callable(condition):
            if arg is not None:
                condition = condition(arg)
            else:
                condition = exec_with_namespace(condition, namespace)
        if not condition:
            return
    value = template.get('$value', _marker)
    repeat = template.get('$repeat', _marker)
    if repeat is not _marker:
        repeat_name, repeater = repeat.split()
        for repeat_value in namespace[repeater]:
            repeat_namespace = namespace.copy()
            repeat_namespace[repeat_name] = repeat_value
            if value is not _marker:
                results = list(object_template(value, repeat_namespace, templated))
                if not results:
                    return
                result, = results
            else:
                result = type(template)()
                for key, tmpl_value in template.items():
                    if key in TEMPLATE_NAMES:
                        continue
                    tmpl_string = templated is True or key in templated
                    results = list(object_template(tmpl_value, repeat_namespace, tmpl_string))
                    if not results:
                        continue
                    result[key], = results
            yield result
    else:
        if value is not _marker:
            results = list(object_template(value, namespace, templated))
            if not results:
                return
            result, = results
        else:
            result = type(template)()
            for key, tmpl_value in template.items():
                if key in TEMPLATE_NAMES:
                    continue
                tmpl_string = templated is True or key in templated
                results = list(object_template(tmpl_value, namespace, tmpl_string))
                if not results:
                    continue
                result[key], = results
        yield result


def object_template(template, namespace, _template_top_string=False):
    # bools are ints
    if template is None or isinstance(template, (int, float)):
        yield template
    elif isinstance(template, basestring):
        if _template_top_string:
            yield string_template(template, namespace)
        else:
            yield template
    elif isinstance(template, dict):
        for result in dict_template(template, namespace):
            yield result
    elif isinstance(template, list):
        yield list_template(template, namespace)
    elif callable(template):
        yield exec_with_namespace(template, namespace)
    else:
        raise TypeError('Unsupported type for: %r' % template)


def exec_with_namespace(template, namespace):
    argspec = inspect.getargspec(template)
    if argspec.keywords:
        return template(**namespace)

    args = {}
    defaults = dict(zip(reversed(argspec.args), reversed(argspec.defaults or ())))
    for name in argspec.args:
        try:
            args[name] = namespace[name]
        except KeyError:
            if name not in defaults:
                raise
            args[name] = defaults[name]

    return template(**args)
