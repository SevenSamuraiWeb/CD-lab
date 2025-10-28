from collections import defaultdict
import os

def read_grammar(filename):
    grammar = defaultdict(list)
    try:
        with open(filename, 'r') as f:
            for line in f:
                if '->' in line:
                    lhs, rhs = line.strip().split('->')
                    productions = [p.strip().split() for p in rhs.split('|')]
                    grammar[lhs.strip()].extend(productions)
    except FileNotFoundError:
        print(f"Error: File '{filename}' not found. Please create it with grammar rules.")
        exit(1)
    return grammar

def eliminate_left_recursion(grammar):
    new_grammar = defaultdict(list)
    for nt in list(grammar.keys()):  
        alpha = [p[1:] for p in grammar[nt] if p and p[0] == nt]
        beta = [p for p in grammar[nt] if p and p[0] != nt]
        if alpha:
            # Left recursion found: create A' and transform
            new_nt = nt + "'"
            # A -> βA' (or A -> A' if no β)
            new_grammar[nt] = [p + [new_nt] for p in beta] if beta else [[new_nt]]
            # A' -> αA' | ε
            new_grammar[new_nt] = [p + [new_nt] for p in alpha] + [['ε']]
        else:
            # No left recursion: copy productions
            new_grammar[nt] = grammar[nt]
    return new_grammar

def print_grammar(grammar):
    for nt in grammar:
        rhs = [' '.join(p) for p in grammar[nt]]
        print(f"{nt} -> {' | '.join(rhs)}")

def main():
    filename = r"c:\Users\nihaa\Compiler design lab\expt 5\grammar.txt"
    print("Current working directory:", os.getcwd())
    print("Original Grammar:")
    grammar = read_grammar(filename)
    print_grammar(grammar)
    print("\nGrammar after Left Recursion Elimination:")
    updated_grammar = eliminate_left_recursion(grammar)
    print_grammar(updated_grammar)

if __name__ == "__main__":
    main()