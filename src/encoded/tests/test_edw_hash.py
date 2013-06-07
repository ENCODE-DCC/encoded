import pytest

TEST_HASHES = {
    "test": "Jnh+8wNnELksNFVbxkya8RDrxJNL13dUWTXhp5DCx/quTM2/cYn7azzl2Uk3I2zc",
    "test2": "sh33L5uQeLr//jJULb7mAnbVADkkWZrgcXx97DCacueGtEU5G2HtqUv73UTS0EI0",
    "testing100" * 10: "5rznDSIcDPd/9rjom6P/qkJGtJSV47y/u5+KlkILROaqQ6axhEyVIQTahuBYerLG",
}


@pytest.mark.parametrize(('password', 'pwhash'), TEST_HASHES.items())
def test_edw_hash(password, pwhash):
    from encoded.edw_hash import EDWHash
    assert EDWHash.encrypt(password) == pwhash
