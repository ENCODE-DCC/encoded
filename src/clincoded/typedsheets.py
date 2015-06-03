from pyramid.settings import asbool


def parse_array(types, value):
    return [cast(types, v) for v in value.split(';') if v.strip()]


def parse_object(types, value):
    items = (part.split(':', 1) for part in value.split(',') if value.strip())
    return {k.strip(): cast(types, v) for k, v in items}


def parse_string(types, value):
    assert not types
    return value


def parse_ignore(types, value):
    return None


def parse_number(types, value):
    assert not types
    try:
        return int(value)
    except ValueError:
        return float(value)


def parse_integer(types, value):
    assert not types
    return int(value)


def parse_boolean(types, value):
    assert not types
    return asbool(value)


TYPE_BY_NAME = {
    'string': parse_string,
    'number': parse_number,
    'boolean': parse_boolean,
    'integer': parse_integer,
    'ignore': parse_ignore,
    'array': parse_array,
    'object': parse_object,
}


def cast(types, value):
    types = list(types) or ['string']
    type_name = types.pop()
    value = value.strip()
    if value.lower() == 'null':
        return None
    if value == '' and type_name != 'string':
        return None
    parse = TYPE_BY_NAME[type_name]
    return parse(types, value)


def convert(name, value):
    """ fieldname:<cast>[:<cast>...], value -> fieldname, cast(value)
    """
    parts = name.split(':')
    return parts[0], cast(parts[1:], value)


def cast_row_values(dictrows):
    """ Wrapper generator for typing csv.DictReader rows
    """
    for row in dictrows:
        yield dict(convert(name, value or '') for name, value in row.items())


def remove_nulls(dictrows):
    for row in dictrows:
        yield {
            name: value for name, value in row.items()
            if value is not None and name
        }
