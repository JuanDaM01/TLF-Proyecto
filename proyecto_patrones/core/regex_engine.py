from .lexer  import Lexer
from .parser import Parser
from .nfa    import ThompsonBuilder
from .dfa    import SubsetConstructor


class RegexEngine:
    def __init__(self, pattern: str):
        self.pattern = pattern
        self.nfa     = self._compile(pattern)

    def _compile(self, pattern: str):
        tokens = Lexer(pattern).tokenize()
        ast    = Parser(tokens).parse()
        nfa    = ThompsonBuilder().build(ast)
        return nfa

    def _simulate(self, text: str):
        current = SubsetConstructor.epsilon_closure([self.nfa.start])

        for symbol in text:
            next_states = SubsetConstructor.move(current, symbol)
            current     = SubsetConstructor.epsilon_closure(next_states)
            if not current:
                return False

        return any(state.is_accept for state in current)

    def match(self, text: str) -> bool:
        return self._simulate(text)

    def search(self, text: str) -> list:
        matches = []
        i = 0
        n = len(text)

        while i < n:
            best_end = -1

            current = SubsetConstructor.epsilon_closure([self.nfa.start])

            if any(state.is_accept for state in current):
                best_end = i

            j = i
            while j < n:
                next_states = SubsetConstructor.move(current, text[j])
                current     = SubsetConstructor.epsilon_closure(next_states)

                if not current:
                    break

                j += 1

                if any(state.is_accept for state in current):
                    best_end = j

            if best_end > i:
                matches.append({
                    'value': text[i:best_end],
                    'start': i,
                    'end':   best_end
                })
                i = best_end
            else:
                i += 1

        return matches

    def __repr__(self):
        return f"RegexEngine(pattern={repr(self.pattern)})"
