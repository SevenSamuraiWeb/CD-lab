import sys
from pathlib import Path

EPSILON = "ε"
EPSILON_ALIASES = {EPSILON, "#", "epsilon", "EPSILON", "lambda", "Λ", "eps"}


def normalize_symbol(token):
    token = token.strip()
    if not token:
        return ""
    return EPSILON if token in EPSILON_ALIASES else token


def cal_first(s, productions, memo=None, visiting=None):
    if memo is None:
        memo = {}
    if visiting is None:
        visiting = set()

    if s in memo:
        return memo[s]

    if s not in productions:
        return {normalize_symbol(s)}

    if s in visiting:
        return set()

    visiting.add(s)
    first = set()

    for production in productions[s]:
        if not production:
            first.add(EPSILON)
            continue

        all_can_be_epsilon = True

        for symbol in production:
            if symbol == EPSILON:
                continue

            if symbol in productions:
                sub_first = cal_first(symbol, productions, memo, visiting)
                first.update(sub_first - {EPSILON})
                if EPSILON in sub_first:
                    continue
            else:
                first.add(symbol)
                all_can_be_epsilon = False
                break

            if symbol in productions and EPSILON not in sub_first:
                all_can_be_epsilon = False
                break

        if all_can_be_epsilon:
            first.add(EPSILON)

    visiting.remove(s)
    memo[s] = first
    return first


def cal_follow(s, productions, first, memo=None, visiting=None, start_symbol=None):
    if memo is None:
        memo = {}
    if visiting is None:
        visiting = set()
    if start_symbol is None:
        start_symbol = next(iter(productions))

    if s in memo:
        return memo[s]

    follow = memo.setdefault(s, set())

    if s not in productions:
        return follow

    if s in visiting:
        return follow

    visiting.add(s)

    if s == start_symbol:
        follow.add('$')

    for head, rules in productions.items():
        for production in rules:
            indices = [idx for idx, symbol in enumerate(production) if symbol == s]
            for idx in indices:
                if idx == len(production) - 1:
                    if head != s:
                        follow.update(
                            cal_follow(head, productions, first, memo, visiting, start_symbol)
                        )
                else:
                    next_idx = idx + 1
                    while next_idx < len(production):
                        next_symbol = production[next_idx]

                        if next_symbol == EPSILON:
                            next_idx += 1
                            continue

                        if next_symbol in productions:
                            symbol_first = first[next_symbol]
                            follow.update(symbol_first - {EPSILON})
                            if EPSILON in symbol_first:
                                next_idx += 1
                                continue
                        else:
                            follow.add(next_symbol)
                        break
                    else:
                        if head != s:
                            follow.update(
                                cal_follow(head, productions, first, memo, visiting, start_symbol)
                            )

    visiting.remove(s)
    return follow


def parse_grammar(grammar_path):
    productions = {}

    with grammar_path.open(encoding="utf-8") as grammar:
        for raw_line in grammar:
            line = raw_line.strip()
            if not line or line.startswith("//") or line.startswith("#"):
                continue

            if "->" not in line:
                raise ValueError(f"Invalid production (missing '->'): {raw_line.rstrip()}")

            left_part, right_part = (part.strip() for part in line.split("->", 1))
            if not left_part:
                raise ValueError(f"Invalid production (empty LHS): {raw_line.rstrip()}")

            alternatives = [alt.strip() for alt in right_part.split("|") if alt.strip()]
            if not alternatives:
                alternatives = [EPSILON]

            current_rules = productions.setdefault(left_part, [])

            for alternative in alternatives:
                symbols = [normalize_symbol(token) for token in alternative.split() if token.strip()]
                if not symbols:
                    symbols = [EPSILON]
                current_rules.append(symbols)

    return productions


def display_sets(title, sets_dict):
    if title:
        print(title)
    for lhs in sets_dict:
        symbols = ", ".join(sorted(sets_dict[lhs])) if sets_dict[lhs] else "∅"
        print(f"{lhs} : {{ {symbols} }}")


def main():
    if len(sys.argv) > 1:
        grammar_path = Path(sys.argv[1]).expanduser()
    else:
        grammar_path = Path(__file__).with_name("grammar.txt")

    try:
        productions = parse_grammar(grammar_path)
    except (OSError, ValueError) as error:
        print(f"Error: {error}")
        return

    first = {}
    first_memo = {}
    for s in productions:
        first[s] = cal_first(s, productions, first_memo)

    follow = {}
    follow_memo = {}
    start_symbol = next(iter(productions))
    for s in productions:
        follow[s] = cal_follow(s, productions, first, follow_memo, start_symbol=start_symbol)

    print("FIRST sets:")
    display_sets("", first)
    print("\nFOLLOW sets:")
    display_sets("", follow)


if __name__ == "__main__":
    main()