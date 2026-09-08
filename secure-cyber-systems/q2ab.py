import secrets

# Q2(a)(b)
#
# The alphabet has 32 symbols, so each symbol is naturally a 5-bit value.
# XOR is therefore just XOR on symbol indices, and CBC follows the usual rule:
# combine with the previous ciphertext symbol, then apply the substitution key.


ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ012345"


def encrypt(x, k):
    return k[ALPHABET.index(x)]


def decrypt(y, k):
    return ALPHABET[k.index(y)]


"""''
Alternative solution for substitution encryption and decryptionused in problem 2c.py. A bit cleaner but uses a package.

from collections import Counter


def encrypt(text, key):
    return text.translate(str.maketrans(ALPHABET, key))

def decrypt(text, key):
    return text.translate(str.maketrans(key, ALPHABET))
""" ""


def cw_xor(a, b):
    return ALPHABET[ALPHABET.index(a) ^ ALPHABET.index(b)]


def encrypt_cbc(m, k):
    initial = secrets.choice(ALPHABET)  # Random IV stored as the first symbol.
    c = initial

    for x in m:
        y = encrypt(cw_xor(x, c[-1]), k)
        c += y

    return c


def decrypt_cbc(c, k):
    m = ""

    for i in range(1, len(c)):
        m += cw_xor(decrypt(c[i], k), c[i - 1])  # Undo substitution, then CBC mix.

    return m


if __name__ == "__main__":
    key = "BACDEFGHIPKLMNOJQRSTUVWXYZ012345"
    message = "HELLOWORLDTHISISTHEPLAINTEXT"
    ciphertext = encrypt_cbc(message, key)

    # print(encrypt("A", key))
    # print(decrypt("B", key))
    # print(cw_xor("A", "G"))
    print(ciphertext)
    print(decrypt_cbc(ciphertext, key))
