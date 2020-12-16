import pytest


@pytest.fixture
def software_0():
    return{
        "name": "star",
        "title": "STAR",
        "description": "STAR (Spliced Transcript Alignment to a Reference)."
    }


@pytest.fixture
def software_1(software_0):
    item = software_0.copy()
    item.update({
        'schema_version': '1',
    })
    return item


@pytest.fixture
def software(testapp, award, lab):
    item = {
        "name": "fastqc",
        "title": "FastQC",
        "description": "A quality control tool for high throughput sequence data.",
        "award": award['@id'],
        "lab": lab['@id'],
    }
    return testapp.post_json('/software', item).json['@graph'][0]
