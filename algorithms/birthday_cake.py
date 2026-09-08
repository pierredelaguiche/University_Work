import sys

# BIRTHDAY CAKE
#
# This task exactly mirrors the egg drop problem. We can, with the same logic,
# find the optimal strategy.
#
# With k kitchen visits and n cakes, the total possible number of times Lea can
# check on the cake is described by sum(C(k, i), i = 1..n). We binary-search
# the smallest k whose coverage reaches the required bound.


def resolvable_baking_times(visits, cake_count, cap):
    """
    Return number of resolvable baking times on a given amount of visits and cakes.
    Cap return since we dont care about exceeding the required bound of cakes.
    """
    if visits <= 0 or cake_count <= 0:
        return 0

    total = 0
    combination = 1
    limit = min(visits, cake_count)

    for i in range(1, limit + 1):
        combination = combination * (visits - i + 1) // i  # Next binomial term.
        total += combination

        if total >= cap:
            return cap

    return total


def minimum_kitchen_visits(cake_count, max_baking_minutes):
    """Return minimum worst-case checks needed for one test case."""
    if max_baking_minutes <= 0:
        return 0

    if cake_count <= 1:
        return max_baking_minutes

    low = 1
    high = 1

    while (
        resolvable_baking_times(high, cake_count, max_baking_minutes)
        < max_baking_minutes
    ):
        high *= 2

    while low < high:
        mid = (low + high) // 2

        if (
            resolvable_baking_times(mid, cake_count, max_baking_minutes)
            >= max_baking_minutes
        ):
            high = mid
        else:
            low = mid + 1

    return low


def solve(tokens):
    """Parse all cases and return outputs in 'Case #i: answer' format."""
    values = iter(map(int, tokens))
    test_case_count = next(values)
    answers = []

    for case_number in range(1, test_case_count + 1):
        cake_count = next(values)
        max_baking_minutes = next(values)
        kitchen_visits = minimum_kitchen_visits(cake_count, max_baking_minutes)
        answers.append(f"Case #{case_number}: {kitchen_visits}")

    return "\n".join(answers)


def main():
    tokens = sys.stdin.buffer.read().split()
    print(solve(tokens))


if __name__ == "__main__":
    main()
