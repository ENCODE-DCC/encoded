import base64
import hashlib
import hmac
import os


def generate_password():
    """ Generate a password with 80 bits of entropy
    """
    # Take a random 10 char binary string (80 bits of
    # entropy) and encode it as lower cased base32 (16 chars)
    random_bytes = os.urandom(10)
    password = base64.b32encode(random_bytes).lower()
    return password


def display_password(password):
    """ Display a password with spaces to aid readability
    """
    return ' '.join(password[i:i + 4] for i in range(4))


def hash_password(password):
    """ Hash a password using HMAC-SHA-256 and a random salt

    This is only suitable for passwords with high entropy.
    """
    # Generate a salt as a random 256bit (32 char) binary string
    salt = os.urandom(32)  # may contain null bytes

    # Calculate the digest using HMAC-SHA-256 with the binary salt as the key
    # and the password as the message
    digest = hmac.new(salt, password, hashlib.sha256).digest()

    # Store the password as {hmac-sha-256}<base64 digest+salt> (103 chars)
    # using the urlsafe variant of the base64 alphabet
    stored = '{hmac-sha-256}' + base64.urlsafe_b64encode(digest + salt)

    return stored


def check_password(guess, stored):
    """ Check a password against its stored hash
    """
    # First remove any spaces from the input
    guess = guess.replace(' ', '')

    # Parse digest and salt stored for the user
    scheme, data = stored[1:].split('}', 1)
    assert scheme == 'hmac-sha-256'
    if isinstance(data, unicode):
        data = data.encode('ascii')
    data = base64.urlsafe_b64decode(data)
    digest = data[:32]
    salt = data[32:]

    # Calculate the digest for guessed password
    guess_digest = hmac.new(salt, guess, hashlib.sha256).digest()

    # Compare the new digest to the stored digest using a linear time
    # algorithm to avoid timing attacks
    assert len(digest) == len(guess_digest)
    match = True
    for i in range(len(digest)):
        if digest[i] != data[i]:
            match = False

    return match
