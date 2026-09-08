from functools import cmp_to_key
import sys

# POLYSTAN PRODUCTION
#
# The feasible total production set is the Minkowski sum of all facility
# polygons. For convex polygons, that sum is still convex.
#
# Normalize each polygon to start at its lowest-leftmost vertex, collect all
# edge vectors, sort them by angle, and walk them cumulatively to build the
# full sum polygon. Then test whether the target lies inside that convex
# polygon.


def cross(vector_a, vector_b):
    return vector_a[0] * vector_b[1] - vector_a[1] * vector_b[0]


def upper_half(vector):
    x_coord, y_coord = vector
    return 0 if (y_coord > 0 or (y_coord == 0 and x_coord >= 0)) else 1


def compare_by_angle(vector_a, vector_b):
    half_a = upper_half(vector_a)
    half_b = upper_half(vector_b)

    if half_a != half_b:
        return -1 if half_a < half_b else 1

    turn = cross(vector_a, vector_b)

    if turn > 0:
        return -1

    if turn < 0:
        return 1

    return 0


def rotate_to_lowest_left(points):
    """Rotate so the first point is lexicographically lowest by (y, x)."""
    start_index = min(
        range(len(points)), key=lambda index: (points[index][1], points[index][0])
    )
    return points[start_index:] + points[:start_index]


def normalize_convex_polygon(points):
    if len(points) >= 3:  # Also handle clockwise input.
        area2 = 0

        for index in range(len(points)):
            x1, y1 = points[index]
            x2, y2 = points[(index + 1) % len(points)]
            area2 += x1 * y2 - y1 * x2

        if area2 < 0:
            points = list(reversed(points))

    return rotate_to_lowest_left(points)


def build_total_polygon(polygons):
    """Build the Minkowski sum polygon from all facility polygons."""
    start_x = 0
    start_y = 0
    all_edges = []  # polygons = [[(x, y), ...], ...]

    for polygon in polygons:
        polygon = normalize_convex_polygon(polygon)
        start_x += polygon[0][0]
        start_y += polygon[0][1]

        vertex_count = len(polygon)

        for index in range(vertex_count):
            next_index = (index + 1) % vertex_count
            edge_x = polygon[next_index][0] - polygon[index][0]
            edge_y = polygon[next_index][1] - polygon[index][1]

            if edge_x != 0 or edge_y != 0:
                all_edges.append((edge_x, edge_y))

    if not all_edges:
        return [(start_x, start_y)]

    all_edges.sort(key=cmp_to_key(compare_by_angle))

    polygon = [(start_x, start_y)]
    current_x = start_x
    current_y = start_y

    for edge_x, edge_y in all_edges:
        current_x += edge_x
        current_y += edge_y

        if (current_x, current_y) != polygon[-1]:
            polygon.append((current_x, current_y))

    if len(polygon) > 1 and polygon[-1] == polygon[0]:
        polygon.pop()

    return polygon


def point_in_convex_polygon(polygon, target):
    """Return True if target is inside or on the boundary of a convex polygon."""
    target_x, target_y = target
    point_count = len(polygon)  # polygon = [(x, y), ...]

    if point_count == 0:
        return False

    if point_count == 1:
        return polygon[0] == target

    if point_count == 2:
        (x1, y1), (x2, y2) = polygon
        direction = (x2 - x1, y2 - y1)
        offset = (target_x - x1, target_y - y1)

        if cross(direction, offset) != 0:
            return False

        return min(x1, x2) <= target_x <= max(x1, x2) and min(
            y1, y2
        ) <= target_y <= max(y1, y2)

    for index in range(point_count):
        x1, y1 = polygon[index]
        x2, y2 = polygon[(index + 1) % point_count]
        edge = (x2 - x1, y2 - y1)
        to_target = (target_x - x1, target_y - y1)

        if cross(edge, to_target) < 0:
            return False

    return True


def solve(tokens):
    """Parse all cases and return yes/no feasibility for each target vector."""
    values = iter(map(int, tokens))
    test_case_count = next(values)
    answers = []

    for case_number in range(1, test_case_count + 1):
        required_x = next(values)
        required_y = next(values)
        facility_count = next(values)
        polygons = []

        for _ in range(facility_count):
            vertex_count = next(values)
            polygon = []

            for _ in range(vertex_count):
                x_coord = next(values)
                y_coord = next(values)
                polygon.append((x_coord, y_coord))

            polygons.append(polygon)

        total_polygon = build_total_polygon(polygons)
        feasible = point_in_convex_polygon(total_polygon, (required_x, required_y))
        answers.append(f"Case #{case_number}: {'yes' if feasible else 'no'}")

    return "\n".join(answers)


def main():
    print(solve(sys.stdin.buffer.read().split()))


if __name__ == "__main__":
    main()
