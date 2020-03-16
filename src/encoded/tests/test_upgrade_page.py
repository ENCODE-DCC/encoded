import pytest


def test_page_upgrade_keep(upgrader, page_1_0):
    value = upgrader.upgrade('page', page_1_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['news_keywords'] == ['RNA binding', 'DNA methylation', 'Conferences']


def test_page_upgrade_empty(upgrader, page_2_0):
    value = upgrader.upgrade('page', page_2_0, target_version='2')
    assert value['schema_version'] == '2'
    assert value['news_keywords'] == []


def test_page_upgrade_none(upgrader, page_3_0):
    value = upgrader.upgrade('page', page_3_0, target_version='2')
    assert value['schema_version'] == '2'
    assert 'news_keywords' not in value
