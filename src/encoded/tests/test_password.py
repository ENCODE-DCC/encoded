def test_password_string():
    from ..password import check_password
    password = "dju6 ju6g u6gx 6gxf"
    stored = "{hmac-sha-256}lO3G_ed8dnurkwczz_Ya1lfzDhGLxc2hpykt6GCbSNmSvjo1Y-PniaJuIsMryElag9IDPjfrf-GzGjc0PEdHuw=="
    assert check_password(password, stored)


def test_password_unicode():
    from ..password import check_password
    password = u"dju6 ju6g u6gx 6gxf"
    stored = u"{hmac-sha-256}lO3G_ed8dnurkwczz_Ya1lfzDhGLxc2hpykt6GCbSNmSvjo1Y-PniaJuIsMryElag9IDPjfrf-GzGjc0PEdHuw=="
    assert check_password(password, stored)
