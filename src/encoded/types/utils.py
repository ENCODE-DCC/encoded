

def try_to_get_field_from_item_with_skip_calculated_first(request, field, at_id_of_item):
    item = request.embed(at_id_of_item, '@@object?skip_calculated=true')
    if field not in item:
        item = request.embed(
            at_id_of_item,
            '@@object_with_select_calculated_properties?field={}'.format(field)
        )
    return item.get(field)


def ensure_list(values):
    if not isinstance(values, list):
        values = [values]
    return [
        v
        for v in values
        if v
    ]


def take_one_or_return_none(values):
    if isinstance(values, list) and len(values) == 1:
        return values[0]

