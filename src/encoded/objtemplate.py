__all__ = ['ObjectTemplate']
TEMPLATE_NAMES = ('templated', 'repeat')


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
    return template.format(**namespace)


def list_template(template, namespace):
    result = type(template)()
    for value in template:
        result.extend(object_template(value, namespace))
    return result


def dict_template(template, namespace):
    templated = template.get('templated', [])
    if isinstance(templated, basestring):
        templated = templated.split()
    repeat = template.get('repeat', None)
    if repeat is not None:
        repeat_name, repeater = repeat.split()
        for repeat_value in namespace[repeater]:
            repeat_namespace = namespace.copy()
            repeat_namespace[repeat_name] = repeat_value
            result = type(template)()
            for key, value in template.items():
                if key in TEMPLATE_NAMES:
                    continue
                if isinstance(value, basestring) \
                    and (templated is True or key in templated):
                    result[key] = string_template(value, repeat_namespace)
                else:
                    result[key], = list(object_template(value,
                                                        repeat_namespace))
            yield result
    else:
        result = type(template)()
        for key, value in template.items():
            if key in TEMPLATE_NAMES:
                continue
            if isinstance(value, basestring) \
                and (templated is True or key in templated):
                result[key] = string_template(value, namespace)
            else:
                result[key], = list(object_template(value, namespace))
        yield result


def object_template(template, namespace):
    # bools are ints
    if template is None or isinstance(template, (basestring, int, float)):
        yield template
    elif isinstance(template, dict):
        for result in dict_template(template, namespace):
            yield result
    elif isinstance(template, list):
        yield list_template(template, namespace)
    else:
        raise TypeError('Unsupported type for: %r' % template)
