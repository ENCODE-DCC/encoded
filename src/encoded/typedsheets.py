def parse_array(value):
    if value is None:
        return []
    return [v.strip() for v in value.decode('utf-8').split(';') if v]


def decode_utf8(value):
    return value.decode('utf-8')


def ignore(value):
    return None


TYPE_BY_NAME = {
    'string': decode_utf8,
    'float': float,
    'boolean': bool,
    'integer': int,
    'array': parse_array,
    'ignore': ignore,
}


def convert(name, value):
    """ fieldname:<cast>, value -> fieldname, cast(value)
    """
    parts = name.rsplit(':', 1)
    name = parts[0]
    if len(parts) == 2:
        type_name = parts[1]
    else:
        type_name = 'string'
    if value.upper() == 'NULL':
        return name, None
    cast = TYPE_BY_NAME[type_name]
    value = cast(value)
    return name, value


def cast_rows(dictrows):
    """ Wrapper generator for typing csv.DictReader rows 
    """
    for row in dictrows:
        yield dict(convert(name, value) for name, value in row.iteritems())


def remove_nulls(dictrows):
    for row in dictrows:
        yield dict(
            (name, value) for name, value in row.iteritems()
            if value is not None and name
        )
