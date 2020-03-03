def collect_audit_errors(result, error_types=None):
    errors = result.json['audit']
    errors_list = []
    if error_types:
        for error_type in error_types:
            errors_list.extend(errors[error_type])
    else:
        for error_type in errors:
            errors_list.extend(errors[error_type])
    return errors_list

RED_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAUA
AAAFCAYAAACNbyblAAAAHElEQVQI12P4//8/w38GIAXDIBKE0DHxgljNBAAO
9TXL0Y4OHwAAAABJRU5ErkJggg=="""

BLUE_DOT = """data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAA
oAAAAKAQMAAAC3/F3+AAAACXBIWXMAAA7DAAAOwwHHb6hkAA
AAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAgY0hSTQ
AAeiYAAICEAAD6AAAAgOgAAHUwAADqYAAAOpgAABdwnLpRPA
AAAANQTFRFALfvPEv6TAAAAAtJREFUCB1jYMAHAAAeAAEBGN
laAAAAAElFTkSuQmCC"""