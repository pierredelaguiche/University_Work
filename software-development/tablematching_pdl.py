# Begin of general documentation:
# Entire program does not include functions. Input is taken, Reservation are put
# into a list with their begining time appended with 1 and their ending time with
# -1. I then sort and iterate through the list and set a variable to current_active.
# This variable's max through the for loop is then printed, unless the variable is
# bigger than the amount of tables. Input handling and list index organization created
# with the help of
# https://www.geeksforgeeks.org/taking-multiple-inputs-from-user-in-python/ .
# Rest of codek nowledge was learned from lectures, geeksforgeeks, w3schools, and
# stackoverflow, not copied.
# End of general documentation.

num_tables, num_reservations = map(
    int, input().split()
)  # https://www.geeksforgeeks.org/taking-multiple-inputs-from-user-in-python/
reservations = []
for x in range(num_reservations):
    start, end = map(int, input().split())
    reservations.append((start, 1))
    reservations.append((end + 1, -1))
reservations.sort()
current_active = 0
max_reservations = 0
for time_begin, diff in reservations:
    current_active += diff
    max_reservations = max(max_reservations, current_active)
if max_reservations > num_tables:
    print("impossible")
else:
    print(max_reservations)
