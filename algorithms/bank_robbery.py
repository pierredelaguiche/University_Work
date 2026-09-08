from collections import deque
import sys

# BANK ROBBERY
#
# We need the minimum total roadblock cost that cuts every path from 1 to n.
# That is exactly the undirected minimum s-t cut, so we compute max flow with
# Dinic and stop early once the flow already exceeds the available policemen.


def minimum_blocking_police(intersection_count, roads, available_police):
    """
    Return the minimum number of policemen needed to block all 1->n paths.
    The computation stops early once the cut is known to exceed
    `available_police`.
    """
    merged_road_cost = (
        {}
    )  # roads = [(intersection_a, intersection_b, roadblock_cost), ...]; merge parallel roads.

    for intersection_a, intersection_b, roadblock_cost in roads:
        if intersection_a == intersection_b:
            continue

        if intersection_a > intersection_b:
            intersection_a, intersection_b = intersection_b, intersection_a

        edge_key = (intersection_a, intersection_b)
        merged_road_cost[edge_key] = merged_road_cost.get(edge_key, 0) + roadblock_cost

    residual_graph = [
        [] for _ in range(intersection_count + 1)
    ]  # residual_graph[node] = [[to, remaining_capacity, reverse_edge_index], ...]

    def add_directed_edge(start, end, capacity):
        residual_graph[start].append([end, capacity, len(residual_graph[end])])
        residual_graph[end].append([start, 0, len(residual_graph[start]) - 1])

    for (
        intersection_a,
        intersection_b,
    ), roadblock_cost in merged_road_cost.items():  # One directed edge each way.
        add_directed_edge(intersection_a, intersection_b, roadblock_cost)
        add_directed_edge(intersection_b, intersection_a, roadblock_cost)

    source = 1
    sink = intersection_count
    max_flow = 0

    while max_flow <= available_police:
        level_by_intersection = [-1] * (intersection_count + 1)
        level_by_intersection[source] = 0
        bfs_queue = deque([source])

        while bfs_queue and level_by_intersection[sink] == -1:
            node = bfs_queue.popleft()

            for neighbor, capacity, _ in residual_graph[node]:
                if capacity > 0 and level_by_intersection[neighbor] == -1:
                    level_by_intersection[neighbor] = level_by_intersection[node] + 1
                    bfs_queue.append(neighbor)

        if level_by_intersection[sink] == -1:
            break

        next_edge_index = [0] * (intersection_count + 1)

        def send_flow(node, flow_limit):
            if node == sink:
                return flow_limit

            while next_edge_index[node] < len(residual_graph[node]):
                edge_index = next_edge_index[node]
                neighbor, capacity, reverse_index = residual_graph[node][edge_index]

                if (
                    capacity > 0
                    and level_by_intersection[neighbor]
                    == level_by_intersection[node] + 1
                ):
                    pushed = send_flow(neighbor, min(flow_limit, capacity))

                    if pushed:
                        residual_graph[node][edge_index][1] -= pushed
                        residual_graph[neighbor][reverse_index][1] += pushed
                        return pushed

                next_edge_index[node] += 1

            return 0

        while max_flow <= available_police:
            pushed = send_flow(source, available_police + 1 - max_flow)

            if pushed == 0:
                break

            max_flow += pushed

    return max_flow


def solve(tokens):
    """Parse all test cases and return formatted yes/no answers."""
    number_stream = iter(map(int, tokens))
    test_case_count = next(number_stream)
    case_outputs = []

    for case_number in range(1, test_case_count + 1):
        available_police = next(number_stream)
        intersection_count = next(number_stream)
        road_count = next(number_stream)
        roads = []

        for _ in range(road_count):
            intersection_a = next(number_stream)
            intersection_b = next(number_stream)
            roadblock_cost = next(number_stream)
            roads.append((intersection_a, intersection_b, roadblock_cost))

        minimum_police_needed = minimum_blocking_police(
            intersection_count, roads, available_police
        )
        can_catch_robber = minimum_police_needed <= available_police
        case_outputs.append(
            f"Case #{case_number}: {'yes' if can_catch_robber else 'no'}"
        )

    return "\n".join(case_outputs)


def main():
    print(solve(sys.stdin.buffer.read().split()))


if __name__ == "__main__":
    main()
