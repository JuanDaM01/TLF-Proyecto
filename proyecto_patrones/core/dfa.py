class DFAState:
    """Estado del AFD (conjunto de estados AFND)."""

    _id_counter = 0

    def __init__(self, nfa_states):
        DFAState._id_counter += 1
        self.id = DFAState._id_counter
        self.nfa_states = nfa_states
        self.transitions = {}
        self.is_accept = False

    def __repr__(self):
        ids = {s.id for s in self.nfa_states}
        return f"DFAState(id={self.id}, nfa={ids}, accept={self.is_accept})"


class SubsetConstructor:
    """Epsilon-clausura y move para simular el AFND."""

    @staticmethod
    def epsilon_closure(states):
        """Clausura epsilon del conjunto de estados."""
        closure = set(states)
        stack = list(states)

        while stack:
            state = stack.pop()
            for next_state in state.transitions.get(None, []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

        return frozenset(closure)

    @staticmethod
    def move(states, symbol):
        """Estados alcanzables al consumir symbol (literal, clase o DOT)."""
        result = set()

        for state in states:
            for trans_sym, dest_states in state.transitions.items():
                if trans_sym is None:
                    continue

                matched = False

                if trans_sym == 'DOT':
                    matched = (symbol != '\n')

                elif isinstance(trans_sym, frozenset):
                    matched = (symbol in trans_sym)

                elif isinstance(trans_sym, str):
                    matched = (trans_sym == symbol)

                if matched:
                    result.update(dest_states)

        return result
