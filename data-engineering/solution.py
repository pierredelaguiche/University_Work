# You can edit this file but cannot import anything.

solutions = {}  # table_name -> iterable of row tuples

def task0(relations):
    global solutions
    solutions = {}

    # Process relations into frozensets for easy coding
    rels = {}
    table_sizes = {}
    index = {}  # frozenset(rows) -> table name

    for name, rows in relations.items():
        s = frozenset(tuple(r) for r in rows)
        if not s:
            continue
        rels[name] = s
        table_sizes[name] = len(next(iter(s)))
        index[s] = name

    names = sorted(rels)
    used = set()
    messages = []

    for i, t0 in enumerate(names): # outer loop: picks first table every operation (wether it is an union check, intersection or cart product)
        if t0 in used:
            continue
        r0 = rels[t0]
        ts0 = table_sizes[t0]

        for t1 in names[i + 1:]: # inner loop: picks second table for every operation
            if t1 in used:
                continue
            r1 = rels[t1]
            ts1 = table_sizes[t1]

            # t0 and t1 must not be subsets of each other
            if r0.issubset(r1) or r1.issubset(r0):
                continue

            # UNION / INTERSECTION (check if arities are equal before operation)
            if ts0 == ts1:
                u = r0 | r1
                t2 = _check_match(index.get(u), used, t0, t1)
                if t2:
                    used.update((t0, t1, t2))
                    messages.append(f"{t2} is UNION of {t0} and {t1}")
                    break

                inter = r0 & r1
                t2 = _check_match(index.get(inter), used, t0, t1)
                if t2:
                    used.update((t0, t1, t2))
                    messages.append(f"{t2} is INTERSECTION of {t0} and {t1}")
                    break

            # CARTESIAN PRODUCT (t0 × t1 ; aka outer loop multiplied by inner loop)
            cp01 = frozenset(a + b for a in r0 for b in r1)
            t2 = _check_match(index.get(cp01), used, t0, t1)
            if t2:
                used.update((t0, t1, t2))
                messages.append(f"{t2} is CARTPROD of {t0} and {t1}")
                break

            # CARTESIAN PRODUCT (t1 × t0 ; aka inner loop multiplied by outer loop)
            cp10 = frozenset(a + b for a in r1 for b in r0)
            t2 = _check_match(index.get(cp10), used, t0, t1)
            if t2:
                used.update((t0, t1, t2))
                messages.append(f"{t2} is CARTPROD of {t1} and {t0}")
                break

    if messages:
        # Only after finding all matches (since we are outside the outer "main" loop that does the operations), decide which tables go into the new DB
        solutions = {name: rels[name] for name in used}
        return messages

    solutions = {}
    return ["NO MATCH"]


def _check_match(t2, used, t0, t1): # outer function to validate tables (repeated functionality)
    if t2 is None:
        return None
    if t2 in used:
        return None
    if t2 == t0 or t2 == t1:
        return None
    return t2


def task1():
    # returns a list of sqlite statements to create tables and populate them
    stmts = []

    for name in sorted(solutions):
        rows = solutions[name]
        if not rows:
            continue

        sample = next(iter(rows))
        num_cols = len(sample)
        cols_def = ", ".join(f"c{i} INTEGER" for i in range(num_cols))
        stmts.append(f"CREATE TABLE {name} ({cols_def});")

        for row in rows:
            values = ", ".join(str(v) for v in row)
            stmts.append(f"INSERT INTO {name} VALUES ({values});")

    return stmts