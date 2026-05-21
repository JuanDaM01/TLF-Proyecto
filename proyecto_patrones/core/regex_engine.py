from .lexer import Lexer
from .parser import Parser
from .nfa import ThompsonBuilder
from .dfa import SubsetConstructor

class RegexEngine:
    """Motor regex propio: Lexer -> Parser -> AFND (Thompson), sin modulo re."""

    def __init__(self, pattern: str):
        """Compila el patron. Lanza ValueError o SyntaxError si es invalido."""
        self.pattern = pattern
        self.nfa = self._compile(pattern)

    def _compile(self, pattern: str):
        """Lexer, parser y construccion de Thompson."""
        tokens = Lexer(pattern).tokenize()
        ast = Parser(tokens).parse()
        return ThompsonBuilder().build(ast)

    def _simulate(self, text: str):
        """Simula el AFND con epsilon-clausura y move; acepta si hay estado final de aceptacion."""
        current = SubsetConstructor.epsilon_closure([self.nfa.start])

        for symbol in text:
            next_states = SubsetConstructor.move(current, symbol)
            current = SubsetConstructor.epsilon_closure(next_states)
            if not current:
                return False

        return any(state.is_accept for state in current)

    def match(self, text: str) -> bool:
        """True si el patron coincide con toda la cadena (equivalente a fullmatch)."""
        return self._simulate(text)

    def search(self, text: str) -> list:
        """Lista de coincidencias no solapadas: dicts con value, start y end."""
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
                current = SubsetConstructor.epsilon_closure(next_states)

                if not current:
                    break

                j += 1

                if any(state.is_accept for state in current):
                    best_end = j

            if best_end > i:
                matches.append({
                    'value': text[i:best_end],
                    'start': i,
                    'end': best_end
                })
                i = best_end
            else:
                i += 1

        return matches

    def __repr__(self):
        return f"RegexEngine(pattern={repr(self.pattern)})"
