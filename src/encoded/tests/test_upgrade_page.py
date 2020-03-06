import pytest


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
