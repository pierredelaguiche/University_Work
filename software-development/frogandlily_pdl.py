# Begin of general documentation:
# Entire program includes one recursive function for calculating the best probability
# of reaching the center. After taking the input and organizing the jumps into a list
# that indexes them according to their starting lily number. I then call the recursive
# function, which in turn checks if its at the end and returns 1 if so. It then multiplies
# all of the inverses of the probabilities and outputs the best probability encountered.
# Input, list of list of list allocation, and other small bits adjusted from code found
# in: https://www.geeksforgeeks.org/taking-multiple-inputs-from-user-in-python/
# https://stackoverflow.com/questions/21581085/how-to-allocate-array-size-in-python .
# Rest of code knowledge was learned from lectures, geeksforgeeks, w3schools, and
# stackoverflow, not copied.
# End of general documentation.

def recursive(lily):
    if lily == num_lilies:
        return 1.0
    if lily in memory_set:
        return memory_set[lily]
    best = 0.0
    for jump in jumps_sorted[lily - 1]:
        next_lily = int(jump[1])
        probability = 1 - float(jump[2])
        candidate = probability * recursive(next_lily)
        if candidate > best:
            best = candidate
    memory_set[lily] = best
    return best
num_lilies, num_jumps = map(int, input().split()) # https://www.geeksforgeeks.org/taking-multiple-inputs-from-user-in-python/
input_buffer = [input().split() for x in range(num_jumps)] 
jumps_sorted = [
    [jump for jump in input_buffer if int(jump[0]) == idx] # https://stackoverflow.com/questions/21581085/how-to-allocate-array-size-in-python
    for idx in range(1, num_lilies + 1)
]
memory_set = {}
result = recursive(1)
print(round(result, 6))
