import pytest


@pytest.fixture
def page_0_0():
    return{
        'name': 'Fake Page',
    }


@pytest.fixture
def page_1_0(page_0_0):
    item = page_0_0.copy()
    item.update({
        'schema_version': '1',
        'news_keywords': ['RNA binding', 'Experiment', 'DNA methylation', 'promoter-like regions', 'Conferences'],
    })
    return item


@pytest.fixture
def page_2_0(page_0_0):
    item = page_0_0.copy()
    item.update({
        'schema_version': '1',
        'news_keywords': ['Experiment', 'promoter-like regions'],
    })
    return item


@pytest.fixture
def page_3_0(page_0_0):
    item = page_0_0.copy()
    item.update({
        'schema_version': '1',
    })
    return item
