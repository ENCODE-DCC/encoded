import pytest


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


def test_page_upgrade_keep(upgrader, page_1):
    value = upgrader.upgrade('page', page_1, target_version='2')
    assert value['schema_version'] == '2'
    assert value['news_keywords'] == ['RNA binding', 'DNA methylation', 'Conferences']


def test_page_upgrade_empty(upgrader, page_2):
    value = upgrader.upgrade('page', page_2, target_version='2')
    assert value['schema_version'] == '2'
    assert value['news_keywords'] == []


def test_page_upgrade_none(upgrader, page_3):
    value = upgrader.upgrade('page', page_3, target_version='2')
    assert value['schema_version'] == '2'
    assert 'news_keywords' not in value
