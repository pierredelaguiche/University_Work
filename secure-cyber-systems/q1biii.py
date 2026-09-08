import sys

# Q1(b)(iii)
#
# This hash is the number of adjacent equal bits in the input bitstream.
# Scan the message from left to right, remember the previous bit, and count
# whenever the next bit matches it.


def hash_by_counting_repeating_bits(message):
    """Return how often two consecutive bits in the message are equal."""
    hash_count = 0
    previous_bit = None

    for byte in message:
        for shift in range(7, -1, -1):
            bit = (byte >> shift) & 1  # Read the current bit most-significant first.
            if bit == previous_bit:
                hash_count += 1
            previous_bit = bit

    return hash_count


if __name__ == "__main__":
    message = bytearray(sys.stdin.buffer.read())
    print(hash_by_counting_repeating_bits(message))
