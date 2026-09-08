# Standard library
from collections import Counter
from csv import reader
from itertools import permutations
from math import log10
from pathlib import Path

# Local imports
from q2c_format import format_poem

# Q2(c)
#
# Break the monoalphabetic substitution by starting with a frequency-based key
# guess, then hill-climb using trigram log-probabilities as the scoring model.
# Each step swaps two plaintext letters if that improves the decoded text.


CIPHERTEXT = "TRKKZAARTLBZKLZEJZSNXMXWWXKYRZTLBZKLZAMHZSXHNUAZMRGRWSABDZAURHMXMAVURXWAZMZTAXWWAUBKNTVBAUAUJYZZMBKNZJZTVUJYMZJZTAAURHAUHTHYRKAUZYRZATUZXMAOHWAHMZVURTZVBKNTXMZSHWWMZXWBABZTURVTURHWSUZWROZAUZZRMURVSZZDAUZZVBTZVURVRHWSTAKRAWZXOZUBDBKUBTVXKSZMBKNARTZZPGRMAMZXTHMZBKAUZIZVZWWZSTPBZTXWEZBAUZTRXMZSVBAUXKHKSXHKAZSVBKNUXTAAURHKRASMXNNZSSBXKXGMRDUZMLXMXKSSMBOZKAUZUXDXSMJXSGMRDAUZVRRSARTZZPXTUZWAZMBKTRDZUXYYBZMTAXMUXTAAURHKRAARMKAUZKXBXSZMRDUZMGWRRSAUZZWGBKGMRDAUZNMZZKNMXTTXKSGMRDDZAUZTHDDZMSMZXDEZKZXAUAUZAXDXMBKSAMZZ"
ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ENGLISH_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQZ"
TRIGRAM_FILE = Path(__file__).with_name("english_3grams.csv")
ALPHABET_SIZE = len(ALPHABET)
A_ORD = ord("A")
TRIGRAM_WIDTH = 3


def trigram_index(a, b, c):
    return (a * ALPHABET_SIZE + b) * ALPHABET_SIZE + c


def to_text(indices):
    return "".join(ALPHABET[index] for index in indices)


def get_frequency_analysis(text):
    counts = Counter(text)
    total = len(text)

    for letter, count in counts.most_common():
        print(f"{letter}: {count} ({count / total:.2%})")


def get_frequency_order(text):
    counts = Counter(text)
    ranked = "".join(letter for letter, _ in counts.most_common())
    return ranked + "".join(letter for letter in ALPHABET if letter not in counts)


def load_trigram_scores(path):
    trigram_counts = []
    total_count = 0

    with path.open(newline="") as file:
        csv_rows = reader(file)
        next(csv_rows, None)

        for trigram, count in csv_rows:
            count = int(count)
            trigram_counts.append((trigram.upper(), count))
            total_count += count

    fallback_score = log10(0.01 / total_count)
    scores = [fallback_score] * (ALPHABET_SIZE**TRIGRAM_WIDTH)  # Dense lookup table.

    for trigram, count in trigram_counts:
        a, b, c = (ord(char) - A_ORD for char in trigram)
        scores[trigram_index(a, b, c)] = log10(count / total_count)

    return scores


def build_cipher(text):
    cipher = [ord(char) - A_ORD for char in text]
    positions = [[] for _ in range(ALPHABET_SIZE)]

    for index, letter in enumerate(cipher):
        positions[letter].append(index)

    return cipher, tuple(tuple(letter_positions) for letter_positions in positions)


def affected_starts(changed_positions, text_length):
    last_start = text_length - TRIGRAM_WIDTH + 1
    if last_start <= 0:
        return ()

    # Only trigrams touching a changed character can change score.
    starts = {
        start
        for position in changed_positions
        for start in range(
            max(0, position - TRIGRAM_WIDTH + 1),
            min(last_start, position + 1),
        )
    }
    return tuple(sorted(starts))


def build_swaps(positions, text_length):
    swaps = []  # Precompute every possible pair of cipher letters to swap.

    for a, left in enumerate(positions):
        if not left:
            continue

        for b in range(a + 1, ALPHABET_SIZE):
            right = positions[b]
            if not right:
                continue

            starts = affected_starts(left + right, text_length)
            swaps.append((a, b, left, right, starts))

    return swaps


def guess_key(text):
    key = [0] * ALPHABET_SIZE

    for cipher_letter, plain_letter in zip(get_frequency_order(text), ENGLISH_ORDER):
        key[ord(cipher_letter) - A_ORD] = ord(plain_letter) - A_ORD

    return key


def score_plaintext(plaintext, trigram_scores):
    return sum(
        trigram_scores[trigram_index(a, b, c)]
        for a, b, c in zip(plaintext, plaintext[1:], plaintext[2:])
    )


def score_region(plaintext, starts, trigram_scores):
    return sum(
        trigram_scores[
            trigram_index(
                plaintext[index],
                plaintext[index + 1],
                plaintext[index + 2],
            )
        ]
        for index in starts
    )


def swap_plaintext(plaintext, left_positions, right_positions, left_value, right_value):
    for index in left_positions:
        plaintext[index] = right_value

    for index in right_positions:
        plaintext[index] = left_value


def swap_delta(plaintext, key, swap, trigram_scores):
    a, b, left_positions, right_positions, starts = swap
    left_value, right_value = key[a], key[b]
    score_before = score_region(plaintext, starts, trigram_scores)

    swap_plaintext(
        plaintext,
        left_positions,
        right_positions,
        left_value,
        right_value,
    )
    score_after = score_region(plaintext, starts, trigram_scores)
    swap_plaintext(
        plaintext,
        left_positions,
        right_positions,
        right_value,
        left_value,
    )
    return score_after - score_before


def apply_swap(plaintext, key, swap):
    a, b, left_positions, right_positions, _ = swap
    left_value, right_value = key[a], key[b]
    swap_plaintext(plaintext, left_positions, right_positions, left_value, right_value)
    key[a], key[b] = right_value, left_value


def find_best_swap(plaintext, key, swaps, trigram_scores):
    best_delta = 0.0
    best_swap = None

    for swap in swaps:
        delta = swap_delta(plaintext, key, swap, trigram_scores)
        if delta > best_delta:
            best_delta = delta
            best_swap = swap

    return best_delta, best_swap


def decrypt(text, trigram_scores):
    cipher, positions = build_cipher(text)
    swaps = build_swaps(positions, len(cipher))
    key = guess_key(text)
    plaintext = [key[letter] for letter in cipher]
    current_score = score_plaintext(plaintext, trigram_scores)
    steps = 0

    while True:  # Greedy hill-climb until no swap improves the score.
        delta, best = find_best_swap(plaintext, key, swaps, trigram_scores)
        if best is None:
            return current_score, key, plaintext, steps

        apply_swap(plaintext, key, best)
        current_score += delta
        steps += 1


def equivalent_keys(text, key):
    unused = [ord(letter) - A_ORD for letter in ALPHABET if letter not in text]
    leftovers = [key[index] for index in unused]
    keys = []

    # Unused cipher letters can be permuted without changing this plaintext.
    for permutation in permutations(leftovers):
        trial = key[:]
        for index, value in zip(unused, permutation):
            trial[index] = value
        keys.append(to_text(trial))

    return keys


def print_optional_output(text, key, plaintext_text, trigram_scores):
    print("All keys that lead to this decoding are:")
    for possible_key in equivalent_keys(text, key):
        print(possible_key)

    print("\nReadable layout:")
    print(format_poem(plaintext_text, trigram_scores))


def main():
    print("Frequency analysis:")
    get_frequency_analysis(CIPHERTEXT)

    print("\nCipher frequency order:")
    print(get_frequency_order(CIPHERTEXT))

    print("\nRecovered key and program statistics:")
    trigram_scores = load_trigram_scores(TRIGRAM_FILE)
    plaintext_score, key, plaintext, steps = decrypt(CIPHERTEXT, trigram_scores)
    plaintext_text = to_text(plaintext)
    print(to_text(key))
    print(f"Hill-climb steps: {steps}")
    print(f"Score: {plaintext_score:.2f}")
    print("\nDecrypted message:")
    print(plaintext_text)
    print(
        "\n# ============================================================================\n"
    )
    print_optional_output(CIPHERTEXT, key, plaintext_text, trigram_scores)


if __name__ == "__main__":
    main()
