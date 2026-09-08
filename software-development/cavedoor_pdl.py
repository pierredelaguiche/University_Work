import copy

# Begin of general documentation:
# Entire program does not include functions. After allocating the input into a
# buffer, arrange the rest of it in a dictionary of dictionaries. The replacement
# scheme is stored with its modes maping an input letter. In cases where letters
# dont have a replacement, they are saved in another dictionary. I then iterate
# through the passwords, with a set of possible modes at each step and updates
# said set accordingly. If the set is non-empty at the end, the passphrase is valid.
# Input, dictionaries, and other small bits tweaked from:
# https://www.geeksforgeeks.org/taking-multiple-inputs-from-user-in-python/
# https://stackoverflow.com/questions/18449360/access-item-in-a-list-of-lists
# Rest of code knowledge was learned from lectures, geeksforgeeks, w3schools, and
# stackoverflow, not copied.
# End of general documentation.

n, m, l = map(
    int, input().split()
)  # https://www.geeksforgeeks.org/taking-multiple-inputs-from-user-in-python/
replacements = [input().split() for _ in range(m)]
modes = {i: {} for i in range(1, n + 1)}
for rep in replacements:
    x, a, b, y = rep
    x = int(x)
    y = int(y)
    modes[x][a] = (b, y)
passwords = [list(input().strip()) for _ in range(l)]
passwords_cpy = copy.deepcopy(passwords)
poss = {}
for mode in range(1, n + 1):
    poss[mode] = {}
    for letter in "abcdefghijklmnopqrstuvwxyz":
        if letter in modes[mode]:
            out_letter, next_mode = modes[mode][letter]
            poss[mode].setdefault(out_letter, set()).add(next_mode)
        else:
            poss[mode].setdefault(letter, set()).add(mode)
num_of_valid_pass = 0
for pwd in passwords:
    dp = {1}
    for ch in pwd:
        new_dp = set()
        for mode in dp:
            if ch in poss[mode]:
                new_dp.update(poss[mode][ch])
        dp = new_dp
        if not dp:
            break
    if dp:
        num_of_valid_pass += 1
print(num_of_valid_pass)
