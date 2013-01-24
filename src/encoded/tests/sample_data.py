ANTIBODIES = [
    {'name': 'Antibody1'},
    {'name': 'Antibody2'},
    {'name': 'Antibody3'},
]


def load_antibodies(testapp):
    for item in ANTIBODIES:
        testapp.post_json('/antibodies/', item, status=201)
