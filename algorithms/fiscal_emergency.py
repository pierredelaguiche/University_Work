import sys

# FISCAL EMERGENCY
#
# The subway graph is a tree. We need the largest set of stations with no edge
# between any two chosen stations, i.e. the maximum independent set on a tree.
#
# Root the tree once, then do bottom-up DP:
# - open_dp[v]   = best answer in v's subtree if v stays open
# - closed_dp[v] = best answer in v's subtree if v is closed
#
# Complexity: O(n) time and O(n) memory per test case.


def max_closable_stations(station_count, direct_links):
    """Return the maximum number of closable stations in a tree."""
    network = [[] for _ in range(station_count + 1)]

    for station_a, station_b in direct_links:
        network[station_a].append(station_b)
        network[station_b].append(station_a)

    parent_station = [0] * (station_count + 1)
    traversal_order = [1]
    parent_station[1] = -1

    for station in traversal_order:  # Grow a root-to-leaf order.
        for neighbor in network[station]:
            if neighbor == parent_station[station]:
                continue

            parent_station[neighbor] = station
            traversal_order.append(neighbor)

    best_if_open = [0] * (station_count + 1)
    best_if_closed = [0] * (station_count + 1)

    for station in reversed(traversal_order):  # Reverse order = children before parent.
        close_station_total = 1
        keep_station_open_total = 0

        for neighbor in network[station]:
            if neighbor == parent_station[station]:
                continue

            close_station_total += best_if_open[neighbor]
            keep_station_open_total += max(
                best_if_open[neighbor], best_if_closed[neighbor]
            )

        best_if_closed[station] = close_station_total
        best_if_open[station] = keep_station_open_total

    return max(best_if_open[1], best_if_closed[1])


def solve(case_data):
    """Parse all test cases and return the formatted answers."""
    number_stream = iter(map(int, case_data))
    test_case_count = next(number_stream)
    case_outputs = []

    for case_number in range(1, test_case_count + 1):
        station_count = next(number_stream)
        direct_links = []

        for _ in range(station_count - 1):
            direct_links.append((next(number_stream), next(number_stream)))

        max_shutdowns = max_closable_stations(station_count, direct_links)
        case_outputs.append(f"Case #{case_number}: {max_shutdowns}")

    return "\n".join(case_outputs)


def main():
    case_data = sys.stdin.buffer.read().split()
    print(solve(case_data))


if __name__ == "__main__":
    main()
