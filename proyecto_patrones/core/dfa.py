class DFAState:
    """
    Estado del AFD resultante de la construcción de subconjuntos.
    
    Atributos:
        nfa_states (frozenset): Conjunto de estados AFND que representa.
        transitions (dict): Mapa símbolo → DFAState.
        is_accept (bool): True si contiene algún estado de aceptación del AFND.
        id (int): Identificador único.
    """
    _id_counter = 0

    def __init__(self, nfa_states):
        DFAState._id_counter += 1
        self.id          = DFAState._id_counter
        self.nfa_states  = nfa_states   # frozenset de NFAState
        self.transitions = {}           # símbolo → DFAState
        self.is_accept   = False

    def __repr__(self):
        ids = {s.id for s in self.nfa_states}
        return f"DFAState(id={self.id}, nfa={ids}, accept={self.is_accept})"


class SubsetConstructor:
    """
    Implementa la Construcción de Subconjuntos para convertir
    un AFND en un AFD equivalente.
    
    La simulación del AFD resultante se realiza directamente sobre
    el AFND usando ε-clausuras, lo que es equivalente pero más eficiente
    en memoria para expresiones regulares medianas.
    
    Método de simulación (usado en RegexEngine):
        En lugar de materializar el AFD completo, se simula el AFND
        manteniendo el conjunto activo de estados en cada paso.
        Esta técnica se llama "simulación de AFND con conjuntos de estados".
    """

    @staticmethod
    def epsilon_closure(states):
        """
        Calcula la ε-clausura de un conjunto de estados AFND.
        
        La ε-clausura(S) es el conjunto de todos los estados alcanzables
        desde S usando exclusivamente transiciones ε (épsilon).
        
        Algoritmo: BFS/DFS sobre transiciones ε.
        
        Args:
            states (iterable): Conjunto inicial de estados AFND.
        
        Returns:
            frozenset: ε-clausura del conjunto dado.
        """
        closure = set(states)
        stack   = list(states)

        while stack:
            state = stack.pop()
            # Obtener todos los estados alcanzables via ε desde este estado
            for next_state in state.transitions.get(None, []):
                if next_state not in closure:
                    closure.add(next_state)
                    stack.append(next_state)

        return frozenset(closure)

    @staticmethod
    def move(states, symbol):
        """
        Calcula el conjunto de estados alcanzables desde `states`
        consumiendo el símbolo `symbol`.
        
        move(S, a) = { q' | q ∈ S, q' ∈ δ(q, a) }
        
        Soporta tres tipos de transiciones:
            - Carácter literal: 'a', '1', '@'
            - Clase de caracteres: frozenset
            - Metacarácter punto: 'DOT'
        
        Args:
            states (iterable): Conjunto de estados AFND actuales.
            symbol (str): Carácter de entrada a consumir.
        
        Returns:
            set: Conjunto de estados AFND destino.
        """
        result = set()

        for state in states:
            for trans_sym, dest_states in state.transitions.items():
                if trans_sym is None:
                    continue  # transiciones ε ya manejadas por epsilon_closure

                matched = False

                if trans_sym == 'DOT':
                    # '.' acepta cualquier carácter excepto newline
                    matched = (symbol != '\n')

                elif isinstance(trans_sym, frozenset):
                    # Clase de caracteres: verificar pertenencia
                    matched = (symbol in trans_sym)

                elif isinstance(trans_sym, str):
                    # Carácter literal: comparación exacta
                    matched = (trans_sym == symbol)

                if matched:
                    result.update(dest_states)

        return result