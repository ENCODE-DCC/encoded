import pytest
from ..constants import *


@pytest.fixture
def page():
    return{
        'name': 'Fake Page',
    }


@pytest.fixture
def page_1(page):
    item = page.copy()
    item.update({
        'schema_version': '1',
        'news_keywords': ['RNA binding', 'Experiment', 'DNA methylation', 'promoter-like regions', 'Conferences'],
    })
    return item


@pytest.fixture
def page_2(page):
    item = page.copy()
    item.update({
        'schema_version': '1',
        'news_keywords': ['Experiment', 'promoter-like regions'],
    })
    return item


@pytest.fixture
def page_3(page):
    item = page.copy()
    item.update({
        'schema_version': '1',
    })
    return item

