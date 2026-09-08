import heapq
import sys

# NIGHTMARE
#
# We need two edge-disjoint paths from a to b with minimum total length. Shared
# vertices are allowed, shared roads are not.
#
# Send 2 units of min-cost flow. Each undirected road is replaced by a small
# gadget with one unit of central capacity, so the road can be used at most
# once in either direction.
#
# Important corner cases from the statement:
# - m may be 0, so "impossible" must be handled cleanly.
# - all values are integers, so integer arithmetic is exact.
# - blank lines between test cases do not matter because split() ignores them.


INF = 10**30


def add_edge(graph, start, end, capacity, cost):
    """Add one directed residual edge and its reverse edge."""
    graph[start].append(
        [end, capacity, cost, len(graph[end])]
    )  # graph[node] = [[to, remaining_capacity, cost, reverse_edge_index], ...]
    graph[end].append([start, 0, -cost, len(graph[start]) - 1])


def min_cost_flow(graph, source, sink, needed_flow):
    """Send up to needed_flow units and return (sent_flow, min_total_cost)."""
    node_count = len(graph)
    potential = [0] * node_count
    flow = 0
    total_cost = 0

    while flow < needed_flow:
        distance = [INF] * node_count
        parent_node = [-1] * node_count
        parent_edge = [-1] * node_count
        distance[source] = 0
        priority_queue = [(0, source)]

        while priority_queue:
            current_dist, current = heapq.heappop(priority_queue)

            if current_dist != distance[current]:
                continue

            for edge_index, edge in enumerate(graph[current]):
                neighbor, capacity, cost, _ = edge

                if capacity <= 0:
                    continue

                reduced_cost = cost + potential[current] - potential[neighbor]
                new_dist = current_dist + reduced_cost

                if new_dist < distance[neighbor]:
                    distance[neighbor] = new_dist
                    parent_node[neighbor] = current
                    parent_edge[neighbor] = edge_index
                    heapq.heappush(priority_queue, (new_dist, neighbor))

        if distance[sink] == INF:
            break

        for node in range(node_count):  # Reweight for Dijkstra.
            if distance[node] < INF:
                potential[node] += distance[node]

        bottleneck = needed_flow - flow
        current = sink

        while current != source:
            prev = parent_node[current]
            edge = graph[prev][parent_edge[current]]
            bottleneck = min(bottleneck, edge[1])
            current = prev

        current = sink

        while current != source:
            prev = parent_node[current]
            edge_index = parent_edge[current]
            edge = graph[prev][edge_index]
            reverse_index = edge[3]

            edge[1] -= bottleneck
            graph[current][reverse_index][1] += bottleneck
            total_cost += bottleneck * edge[2]
            current = prev

        flow += bottleneck

    return flow, total_cost


def minimum_total_distance(intersection_count, roads, start, target):
    assert start != target

    node_count = intersection_count + 2 * len(
        roads
    )  # roads = [(intersection_a, intersection_b, length), ...]
    graph = [[] for _ in range(node_count)]
    next_node_id = intersection_count

    for intersection_a, intersection_b, length in roads:
        u = intersection_a - 1
        v = intersection_b - 1
        edge_in = next_node_id
        edge_out = next_node_id + 1
        next_node_id += 2

        add_edge(
            graph, u, edge_in, 1, length
        )  # Pay on entry; center edge has shared capacity 1.
        add_edge(graph, v, edge_in, 1, length)
        add_edge(graph, edge_in, edge_out, 1, 0)
        add_edge(graph, edge_out, u, 1, 0)
        add_edge(graph, edge_out, v, 1, 0)

    flow, cost = min_cost_flow(graph, start - 1, target - 1, 2)

    if flow < 2:
        return None

    return cost


def solve(tokens):
    """Parse cases and output min total length or impossible."""
    values = iter(map(int, tokens))
    test_case_count = next(values)
    answers = []

    for case_number in range(1, test_case_count + 1):
        intersection_count = next(values)
        road_count = next(values)
        start = next(values)
        target = next(values)
        roads = []

        for _ in range(road_count):
            roads.append((next(values), next(values), next(values)))

        best = minimum_total_distance(intersection_count, roads, start, target)

        if best is None:
            answers.append(f"Case #{case_number}: impossible")
        else:
            answers.append(f"Case #{case_number}: {best}")

    return "\n".join(answers)


def main():
    print(solve(sys.stdin.buffer.read().split()))


if __name__ == "__main__":
    main()
