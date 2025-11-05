from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path
from typing import DefaultDict, Dict, Iterable, List, Sequence, Set


EPSILON = "ε"
EPSILON_TOKENS = {EPSILON, "#", "epsilon", "EPSILON", "lambda", "Λ"}


class GrammarParseError(Exception):
	"""Raised when the grammar file cannot be parsed correctly."""


def normalize_symbol(symbol: str) -> str:
	symbol = symbol.strip()
	return EPSILON if symbol in EPSILON_TOKENS else symbol


def parse_grammar_file(path: Path) -> tuple[Dict[str, List[List[str]]], str]:
	if not path.exists():
		raise GrammarParseError(f"Grammar file '{path}' not found.")

	entries: List[tuple[str, List[str], int]] = []
	start_symbol: str | None = None

	with path.open(encoding="utf-8") as handle:
		for line_no, raw_line in enumerate(handle, start=1):
			stripped = raw_line.strip()
			if not stripped or stripped.startswith("//"):
				continue

			if "->" not in stripped:
				raise GrammarParseError(
					f"Line {line_no}: Missing '->' in production: {raw_line.rstrip()}"
				)

			lhs_part, rhs_part = (part.strip() for part in stripped.split("->", 1))
			if not lhs_part:
				raise GrammarParseError(f"Line {line_no}: Empty non-terminal on LHS.")

			if start_symbol is None:
				start_symbol = lhs_part

			if not rhs_part:
				raise GrammarParseError(
					f"Line {line_no}: Non-terminal '{lhs_part}' has no productions."
				)

			alternatives = [alt.strip() for alt in rhs_part.split("|") if alt.strip()]
			if not alternatives:
				raise GrammarParseError(
					f"Line {line_no}: Non-terminal '{lhs_part}' has only empty alternatives."
				)

			entries.append((lhs_part, alternatives, line_no))

	if start_symbol is None:
		raise GrammarParseError("The grammar file does not contain any productions.")

	productions: DefaultDict[str, List[List[str]]] = defaultdict(list)
	nonterminals = {lhs for lhs, _, _ in entries}
	sorted_nonterminals = sorted(nonterminals, key=len, reverse=True)

	for lhs, alternatives, line_no in entries:
		for alt in alternatives:
			symbols = tokenize_alternative(alt, nonterminals, sorted_nonterminals)
			if not symbols:
				raise GrammarParseError(
					f"Line {line_no}: Unable to parse production '{alt}' for '{lhs}'."
				)
			productions[lhs].append(symbols)

	return dict(productions), start_symbol


def tokenize_alternative(
	alternative: str,
	nonterminals: Set[str],
	sorted_nonterminals: Sequence[str],
) -> List[str]:
	tokens: List[str] = []
	parts = alternative.split()

	if not parts:
		return [EPSILON]

	for part in parts:
		tokens.extend(split_token(part, nonterminals, sorted_nonterminals))

	normalized = [normalize_symbol(token) for token in tokens if token]
	return normalized or [EPSILON]


def split_token(
	token: str,
	nonterminals: Set[str],
	sorted_nonterminals: Sequence[str],
) -> List[str]:
	if not token:
		return []

	if token in EPSILON_TOKENS:
		return [EPSILON]

	if token in nonterminals:
		return [token]

	symbols: List[str] = []
	index = 0
	length = len(token)

	while index < length:
		match = None
		for nonterminal in sorted_nonterminals:
			if token.startswith(nonterminal, index):
				match = nonterminal
				break

		if match:
			symbols.append(match)
			index += len(match)
			continue

		lookahead = index + 1
		while lookahead < length and not any(
			token.startswith(nt, lookahead) for nt in sorted_nonterminals
		):
			lookahead += 1

		symbols.append(token[index:lookahead])
		index = lookahead

	return symbols


def is_nonterminal(symbol: str, grammar: Dict[str, List[List[str]]]) -> bool:
	return symbol in grammar


def compute_first_sets(grammar: Dict[str, List[List[str]]]) -> Dict[str, Set[str]]:
	first_sets: Dict[str, Set[str]] = {nt: set() for nt in grammar}
	changed = True

	while changed:
		changed = False
		for non_terminal, production_list in grammar.items():
			for production in production_list:
				if production == [EPSILON]:
					if EPSILON not in first_sets[non_terminal]:
						first_sets[non_terminal].add(EPSILON)
						changed = True
					continue

				derives_epsilon = True
				for symbol in production:
					symbol_first: Set[str]

					if symbol == EPSILON:
						symbol_first = {EPSILON}
					elif is_nonterminal(symbol, grammar):
						symbol_first = first_sets[symbol]
					else:
						symbol_first = {symbol}

					before_size = len(first_sets[non_terminal])
					first_sets[non_terminal].update(symbol_first - {EPSILON})
					if len(first_sets[non_terminal]) != before_size:
						changed = True

					if EPSILON not in symbol_first:
						derives_epsilon = False
						break

				if derives_epsilon:
					if EPSILON not in first_sets[non_terminal]:
						first_sets[non_terminal].add(EPSILON)
						changed = True

	return first_sets


def first_of_sequence(
	sequence: Sequence[str],
	first_sets: Dict[str, Set[str]],
	grammar: Dict[str, List[List[str]]],
) -> Set[str]:
	if not sequence:
		return {EPSILON}

	result: Set[str] = set()

	for symbol in sequence:
		if symbol == EPSILON:
			result.add(EPSILON)
			continue

		if is_nonterminal(symbol, grammar):
			symbol_first = first_sets[symbol]
		else:
			symbol_first = {symbol}

		result.update(symbol_first - {EPSILON})

		if EPSILON not in symbol_first:
			break
	else:
		result.add(EPSILON)

	return result


def update_set(target: Set[str], additions: Iterable[str]) -> bool:
	before = len(target)
	target.update(additions)
	return len(target) != before


def compute_follow_sets(
	grammar: Dict[str, List[List[str]]],
	first_sets: Dict[str, Set[str]],
	start_symbol: str,
) -> Dict[str, Set[str]]:
	follow_sets: Dict[str, Set[str]] = {nt: set() for nt in grammar}
	follow_sets[start_symbol].add("$")

	changed = True
	while changed:
		changed = False
		for head, production_list in grammar.items():
			for production in production_list:
				for index, symbol in enumerate(production):
					if not is_nonterminal(symbol, grammar):
						continue

					remainder = production[index + 1 :]
					lookahead_first = first_of_sequence(remainder, first_sets, grammar)

					if update_set(follow_sets[symbol], lookahead_first - {EPSILON}):
						changed = True

					if not remainder or EPSILON in lookahead_first:
						if update_set(follow_sets[symbol], follow_sets[head]):
							changed = True

	return follow_sets


def sorted_symbols(symbols: Iterable[str]) -> List[str]:
	return sorted(symbols, key=lambda sym: (sym != EPSILON, sym))


def display_sets(title: str, sets: Dict[str, Set[str]]):
	print(title)
	for non_terminal in sorted(sets.keys()):
		members = ", ".join(sorted_symbols(sets[non_terminal])) or "∅"
		print(f"  {non_terminal}: {{ {members} }}")


def resolve_grammar_path(argv: Sequence[str]) -> Path:
	if len(argv) > 1:
		return Path(argv[1]).expanduser().resolve()
	return Path(__file__).with_name("grammar.txt")


def main(argv: Sequence[str]) -> int:
	grammar_path = resolve_grammar_path(argv)

	try:
		grammar, start_symbol = parse_grammar_file(grammar_path)
	except GrammarParseError as error:
		print(f"Error: {error}")
		return 1

	print(f"Grammar loaded from: {grammar_path}")
	print(f"Start symbol: {start_symbol}\n")

	first_sets = compute_first_sets(grammar)
	follow_sets = compute_follow_sets(grammar, first_sets, start_symbol)

	display_sets("FIRST sets:", first_sets)
	print()
	display_sets("FOLLOW sets:", follow_sets)

	return 0


if __name__ == "__main__":
	raise SystemExit(main(sys.argv))
