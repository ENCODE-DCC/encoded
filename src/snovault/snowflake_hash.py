from base64 import (
    b64decode,
    b64encode,
)
from hashlib import sha384
from passlib.registry import register_crypt_handler
from passlib.utils import handlers as uh


def includeme(config):
    register_crypt_handler(SNOWHash)


class SNOWHash(uh.StaticHandler):
    """ a special snowflake of a  password hashing scheme

    Cryptographic strength of the hashing function is less of a concern for
    randomly generated passwords.
    """
    name = 'snowflake_hash'
    checksum_chars = uh.PADDED_BASE64_CHARS
    checksum_size = 64

    setting_kwds = ('salt_before', 'salt_after', 'salt_base')
    salt_before = b"186ED79BAEXzeusdioIsdklnw88e86cd73"
    salt_after = b"<*#$*(#)!DSDFOUIHLjksdf"
    salt_base = b64decode(b"""\
Kf8r/S37L/kh9yP1JfMn8TnvO+096z/pMecz5TXjN+EJ3wvdDdsP2QHXA9UF0wfRGc8bzR3LH8kR
xxPFFcMXwWm/a71tu2+5YbdjtWWzZ7F5r3utfat/qXGnc6V1o3ehSZ9LnU2bT5lBl0OVRZNHkVmP
W41di1+JUYdThVWDV4Gpf6t9rXuveaF3o3Wlc6dxuW+7bb1rv2mxZ7NltWO3YYlfi12NW49ZgVeD
VYVTh1GZT5tNnUufSZFHk0WVQ5dB6T/rPe077znhN+M15TPnMfkv+y39K/8p8SfzJfUj9yHJH8sd
zRvPGcEXwxXFE8cR2Q/bDd0L3wnRB9MF1QPXASn/K/0t+y/5Ifcj9SXzJ/E57zvtPes/6THnM+U1
4zfhCd8L3Q3bD9kB1wPVBdMH0RnPG80dyx/JEccTxRXDF8Fpv2u9bbtvuWG3Y7Vls2exea97rX2r
f6lxp3OldaN3oUmfS51Nm0+ZQZdDlUWTR5FZj1uNXYtfiVGHU4VVg1eBqX+rfa17r3mhd6N1pXOn
cblvu229a79psWezZbVjt2GJX4tdjVuPWYFXg1WFU4dRmU+bTZ1Ln0mRR5NFlUOXQek/6z3tO+85
4TfjNeUz5zH5L/st/Sv/KfEn8yX1I/chyR/LHc0bzxnBF8MVxRPHEdkP2w3dC98J0QfTBdUD1wE=
""")

    def _calc_checksum(self, secret):
        if not isinstance(secret, bytes):
            secret = secret.encode('utf-8')
        salted = self.salt_before + secret + self.salt_after + b'\0'
        if len(salted) > len(self.salt_base):
            raise ValueError("Password too long")
        salted += self.salt_base[len(salted):]
        chk = sha384(salted).digest()
        return b64encode(chk).decode("ascii")
