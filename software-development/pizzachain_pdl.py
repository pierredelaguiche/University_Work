# Begin of general documentation:
# Entire program does not include functions. Input is taken, n of good pizza
# places are joined in a cummulated list to make the later calculation easier
# and more efficient. I then, after calculating the upper and lower bounds,
# keep iterating through each possible position and saving the biggest possible
# reachable amount of pizza places. That's then printed. Input code tweaked from:
# https://www.geeksforgeeks.org/taking-multiple-inputs-from-user-in-python/ and
# https://stackoverflow.com/questions/7845165/how-to-take-input-in-an-array-python.
# Rest of codek nowledge was learned from lectures, geeksforgeeks, w3schools, and
# stackoverflow, not copied.
# End of general documentation.

length_strt, possible_loc, max_dist = map(
    int, input().split()
)  # https://www.geeksforgeeks.org/taking-multiple-inputs-from-user-in-python/
street_list = list(
    map(int, input().strip())
)  # https://stackoverflow.com/questions/7845165/how-to-take-input-in-an-array-python
position_list = list(map(int, input().split()))
cummulated_places = [0] * (length_strt + 1)
for i in range(length_strt):
    cummulated_places[i + 1] = cummulated_places[i] + street_list[i]
best_pos_count = 0
for pos in position_list:
    left_furthest = max(0, pos - max_dist - 1)
    right_furthest = min(length_strt, pos + max_dist)
    pos_count = cummulated_places[right_furthest] - cummulated_places[left_furthest]
    best_pos_count = max(best_pos_count, pos_count)
print(best_pos_count)
