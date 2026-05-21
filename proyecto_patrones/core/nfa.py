from .parser import (CharNode, ClassNode, DotNode, ConcatNode,
                    AltNode, StarNode, PlusNode, QuestionNode)


class NFAState:
    """Estado del AFND (transiciones y flag de aceptacion)."""

    _id_counter = 0

    def __init__(self):
        NFAState._id_counter += 1
        self.id = NFAState._id_counter
        self.transitions = {}
        self.is_accept = False

    def add_transition(self, symbol, state):
        """Agrega transicion epsilon (None), literal, clase o DOT."""
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        self.transitions[symbol].append(state)

    def __repr__(self):
        return f"NFAState(id={self.id}, accept={self.is_accept})"

class NFA:
    """Par inicio / aceptacion del AFND."""

    def __init__(self, start, accept):
        self.start = start
        self.accept = accept

class ThompsonBuilder:
    """Construccion de Thompson: AST -> AFND."""

    def build(self, node):
        """Despacha por tipo de nodo AST."""
        if isinstance(node, CharNode):
            return self._build_char(node.char)
        elif isinstance(node, ClassNode):
            return self._build_class(node.chars)
        elif isinstance(node, DotNode):
            return self._build_dot()
        elif isinstance(node, ConcatNode):
            return self._build_concat(node)
        elif isinstance(node, AltNode):
            return self._build_alt(node)
        elif isinstance(node, StarNode):
            return self._build_star(node)
        elif isinstance(node, PlusNode):
            return self._build_plus(node)
        elif isinstance(node, QuestionNode):
            return self._build_question(node)
        else:
            raise TypeError(f"Nodo AST no soportado: {type(node)}")

    def _build_char(self, char):
        start = NFAState()
        accept = NFAState()
        accept.is_accept = True
        start.add_transition(char, accept)
        return NFA(start, accept)

    def _build_class(self, chars):
        start = NFAState()
        accept = NFAState()
        accept.is_accept = True
        start.add_transition(frozenset(chars), accept)
        return NFA(start, accept)

    def _build_dot(self):
        start = NFAState()
        accept = NFAState()
        accept.is_accept = True
        start.add_transition('DOT', accept)
        return NFA(start, accept)

    def _build_concat(self, node):
        nfa1 = self.build(node.left)
        nfa2 = self.build(node.right)

        nfa1.accept.is_accept = False
        nfa1.accept.add_transition(None, nfa2.start)

        return NFA(nfa1.start, nfa2.accept)

    def _build_alt(self, node):
        nfa1 = self.build(node.left)
        nfa2 = self.build(node.right)

        new_start = NFAState()
        new_accept = NFAState()
        new_accept.is_accept = True

        new_start.add_transition(None, nfa1.start)
        new_start.add_transition(None, nfa2.start)

        nfa1.accept.is_accept = False
        nfa2.accept.is_accept = False
        nfa1.accept.add_transition(None, new_accept)
        nfa2.accept.add_transition(None, new_accept)

        return NFA(new_start, new_accept)

    def _build_star(self, node):
        nfa = self.build(node.child)

        new_start = NFAState()
        new_accept = NFAState()
        new_accept.is_accept = True

        new_start.add_transition(None, nfa.start)
        new_start.add_transition(None, new_accept)

        nfa.accept.is_accept = False
        nfa.accept.add_transition(None, nfa.start)
        nfa.accept.add_transition(None, new_accept)

        return NFA(new_start, new_accept)

    def _build_plus(self, node):
        nfa = self.build(node.child)

        new_start = NFAState()
        new_accept = NFAState()
        new_accept.is_accept = True

        new_start.add_transition(None, nfa.start)

        nfa.accept.is_accept = False
        nfa.accept.add_transition(None, nfa.start)
        nfa.accept.add_transition(None, new_accept)

        return NFA(new_start, new_accept)

    def _build_question(self, node):
        nfa = self.build(node.child)

        new_start = NFAState()
        new_accept = NFAState()
        new_accept.is_accept = True

        new_start.add_transition(None, nfa.start)
        new_start.add_transition(None, new_accept)

        nfa.accept.is_accept = False
        nfa.accept.add_transition(None, new_accept)

        return NFA(new_start, new_accept)
