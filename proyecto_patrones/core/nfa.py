# =============================================================================
# core/nfa.py
# Construcción del Autómata Finito No Determinista (AFND)
# Algoritmo de Thompson (1968)
#
# La construcción de Thompson transforma un AST de regex en un AFND
# con las siguientes propiedades:
#   - Un único estado inicial
#   - Un único estado de aceptación
#   - Transiciones ε (épsilon) para uniones y clausuras
#   - Estructura modular: cada subexpresión genera un sub-autómata
# =============================================================================

from .parser import (CharNode, ClassNode, DotNode, ConcatNode,
                      AltNode, StarNode, PlusNode, QuestionNode)


class NFAState:
    """
    Representa un estado del AFND.
    
    Atributos:
        id          (int): Identificador único del estado.
        transitions (dict): Mapa carácter/condición → lista de estados destino.
                            La clave None representa transiciones ε.
        is_accept   (bool): True si es estado de aceptación.
    """
    _id_counter = 0  # Contador global para asignar IDs únicos

    def __init__(self):
        NFAState._id_counter += 1
        self.id          = NFAState._id_counter
        self.transitions = {}   # key: char | frozenset | None  → [NFAState]
        self.is_accept   = False

    def add_transition(self, symbol, state):
        """
        Agrega una transición desde este estado.
        
        Args:
            symbol: El símbolo que activa la transición.
                    None → transición epsilon (ε).
                    str  → carácter literal.
                    frozenset → clase de caracteres.
                    'DOT' → cualquier carácter.
            state (NFAState): Estado destino de la transición.
        """
        if symbol not in self.transitions:
            self.transitions[symbol] = []
        self.transitions[symbol].append(state)

    def __repr__(self):
        return f"NFAState(id={self.id}, accept={self.is_accept})"


class NFA:
    """
    Autómata Finito No Determinista resultante de la construcción de Thompson.
    
    Atributos:
        start  (NFAState): Estado inicial del autómata.
        accept (NFAState): Único estado de aceptación.
    """
    def __init__(self, start, accept):
        self.start  = start
        self.accept = accept


class ThompsonBuilder:
    """
    Implementa la construcción de Thompson para transformar el AST
    de una expresión regular en un AFND.
    
    Cada método build_* recibe un nodo del AST y retorna un NFA
    compuesto por dos estados (inicio y aceptación) conectados
    por las transiciones correspondientes.
    
    Reglas de construcción:
    
    1. Literal 'a':
       q0 --a--> q1  (q0=inicio, q1=aceptación)
    
    2. Concatenación r1·r2:
       [NFA1: q0→q1] --ε--> [NFA2: q2→q3]
       Resultado: q0 → ... → q1 --ε--> q2 → ... → q3
    
    3. Alternación r1|r2:
       q_new --ε--> [NFA1] --ε--> q_accept
       q_new --ε--> [NFA2] --ε--> q_accept
    
    4. Clausura de Kleene r*:
       q_new --ε--> [NFA] --ε--> q_accept
              ←-----ε-----
       q_new --ε--> q_accept (acepta cadena vacía)
    """

    def build(self, node):
        """
        Despacha la construcción según el tipo de nodo AST.
        
        Args:
            node (ASTNode): Nodo raíz del subárbol a transformar.
        
        Returns:
            NFA: Autómata correspondiente al subárbol.
        
        Raises:
            TypeError: Si el tipo de nodo no está soportado.
        """
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
        """
        AFND para un carácter literal.
        q0 --char--> q1
        """
        start  = NFAState()
        accept = NFAState()
        accept.is_accept = True
        start.add_transition(char, accept)
        return NFA(start, accept)

    def _build_class(self, chars):
        """
        AFND para una clase de caracteres [a-z], \d, etc.
        Usa un frozenset como símbolo de transición para representar
        múltiples caracteres en una sola transición.
        """
        start  = NFAState()
        accept = NFAState()
        accept.is_accept = True
        start.add_transition(frozenset(chars), accept)
        return NFA(start, accept)

    def _build_dot(self):
        """
        AFND para el metacarácter '.'.
        Usa la cadena especial 'DOT' como símbolo.
        """
        start  = NFAState()
        accept = NFAState()
        accept.is_accept = True
        start.add_transition('DOT', accept)
        return NFA(start, accept)

    def _build_concat(self, node):
        """
        AFND para la concatenación: NFA1 --ε--> NFA2
        El estado de aceptación de NFA1 se conecta con ε al inicio de NFA2.
        """
        nfa1 = self.build(node.left)
        nfa2 = self.build(node.right)

        # Conectar aceptación de NFA1 con inicio de NFA2 via ε
        nfa1.accept.is_accept = False
        nfa1.accept.add_transition(None, nfa2.start)

        return NFA(nfa1.start, nfa2.accept)

    def _build_alt(self, node):
        """
        AFND para la alternación r1|r2.
        
        Crea un nuevo estado inicial y uno de aceptación.
        El nuevo inicio conecta via ε con los inicios de NFA1 y NFA2.
        Los estados de aceptación de NFA1 y NFA2 conectan via ε
        al nuevo estado de aceptación.
        """
        nfa1 = self.build(node.left)
        nfa2 = self.build(node.right)

        new_start  = NFAState()
        new_accept = NFAState()
        new_accept.is_accept = True

        # ε-transiciones del nuevo inicio a ambos inicios
        new_start.add_transition(None, nfa1.start)
        new_start.add_transition(None, nfa2.start)

        # ε-transiciones de ambas aceptaciones al nuevo fin
        nfa1.accept.is_accept = False
        nfa2.accept.is_accept = False
        nfa1.accept.add_transition(None, new_accept)
        nfa2.accept.add_transition(None, new_accept)

        return NFA(new_start, new_accept)

    def _build_star(self, node):
        """
        AFND para la clausura r*.
        
        Estructura:
          new_start --ε--> nfa_start
          nfa_accept --ε--> nfa_start  (retroalimentación)
          nfa_accept --ε--> new_accept (salida)
          new_start  --ε--> new_accept (cadena vacía)
        """
        nfa = self.build(node.child)

        new_start  = NFAState()
        new_accept = NFAState()
        new_accept.is_accept = True

        new_start.add_transition(None, nfa.start)
        new_start.add_transition(None, new_accept)   # acepta ε

        nfa.accept.is_accept = False
        nfa.accept.add_transition(None, nfa.start)   # bucle
        nfa.accept.add_transition(None, new_accept)  # salida

        return NFA(new_start, new_accept)

    def _build_plus(self, node):
        """
        AFND para r+ ≡ r · r*
        
        Construye el NFA base y le agrega la clausura.
        El estado de aceptación puede re-entrar al inicio (bucle).
        """
        nfa = self.build(node.child)

        new_start  = NFAState()
        new_accept = NFAState()
        new_accept.is_accept = True

        new_start.add_transition(None, nfa.start)

        nfa.accept.is_accept = False
        nfa.accept.add_transition(None, nfa.start)   # bucle r*
        nfa.accept.add_transition(None, new_accept)  # salida

        return NFA(new_start, new_accept)

    def _build_question(self, node):
        """
        AFND para r? ≡ r | ε.
        
        Crea nuevo inicio y aceptación.
        El inicio conecta a la subexpresión y directamente a la aceptación.
        """
        nfa = self.build(node.child)

        new_start  = NFAState()
        new_accept = NFAState()
        new_accept.is_accept = True

        new_start.add_transition(None, nfa.start)
        new_start.add_transition(None, new_accept)  # acepta ε

        nfa.accept.is_accept = False
        nfa.accept.add_transition(None, new_accept)

        return NFA(new_start, new_accept)
