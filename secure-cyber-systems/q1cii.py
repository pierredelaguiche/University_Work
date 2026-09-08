from hashlib import sha256
from itertools import product

# Q1(c)(ii)
#
# The target digest comes from a lowercase 5-letter word. Exhaustively trying
# all 26^5 candidates is small enough, so we hash each candidate until one
# matches the given SHA-256 digest.


TARGET = bytes.fromhex(
    "47c5c28cae2574cdf5a194fe7717de68f8276f4bf83e653830925056aeb32a48"
)
ALPHABET = range(ord("a"), ord("z") + 1)


def decrypt():
    """Return the matching lowercase 5-letter preimage, if it exists."""
    for candidate in product(ALPHABET, repeat=5):
        word = bytes(candidate)
        if sha256(word).digest() == TARGET:
            return word.decode()
    return None


if __name__ == "__main__":
    print(decrypt())
