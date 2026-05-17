# =============================================================================
# core/regex_engine.py
# Motor de Expresiones Regulares — API Pública
#
# Este módulo integra el pipeline completo:
#   Lexer → Parser → Thompson(AFND) → Simulación con ε-clausuras
#
# Provee dos operaciones principales:
#   1. match(text)   → Verifica si TODO el texto cumple el patrón
#   2. search(text)  → Busca TODAS las ocurrencias del patrón en el texto
#
# NO usa ninguna librería regex de Python (sin 'import re').
# =============================================================================

from .lexer  import Lexer
from .parser import Parser
from .nfa    import ThompsonBuilder
from .dfa    import SubsetConstructor


class RegexEngine:
    """
    Motor de expresiones regulares construido desde cero.
    
    Pipeline interno:
        pattern (str)
            ↓ Lexer.tokenize()
        [Token, ...]
            ↓ Parser.parse()
        ASTNode (árbol sintáctico)
            ↓ ThompsonBuilder.build()
        NFA (autómata no determinista)
            → simulado con epsilon_closure + move
    
    Ejemplo de uso:
        engine = RegexEngine(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")
        
        # Verificar si toda la cadena es un email válido
        engine.match("usuario@ejemplo.com")   # → True
        engine.match("no_es_email")           # → False
        
        # Buscar todos los emails en un texto
        matches = engine.search("Contacto: a@b.com y c@d.org")
        # → [Match(value='a@b.com', start=10, end=17), ...]
    
    Limitaciones conocidas:
        - No soporta cuantificadores con repetición exacta {n,m} (extensión futura)
        - No soporta grupos de captura con backreferences
        - El punto '.' no acepta \\n (comportamiento estándar)
    """

    def __init__(self, pattern: str):
        """
        Compila la expresión regular en un AFND listo para simulación.
        
        Args:
            pattern (str): Expresión regular a compilar.
        
        Raises:
            ValueError: Si el patrón tiene sintaxis inválida.
            SyntaxError: Si el parser no puede procesar la expresión.
        """
        self.pattern = pattern
        self.nfa     = self._compile(pattern)

    def _compile(self, pattern: str):
        """
        Ejecuta el pipeline completo de compilación.
        
        Returns:
            NFA: Autómata compilado.
        """
        tokens = Lexer(pattern).tokenize()
        ast    = Parser(tokens).parse()
        nfa    = ThompsonBuilder().build(ast)
        return nfa

    def _simulate(self, text: str):
        """
        Simula el AFND sobre el texto completo usando conjuntos de estados.
        
        La simulación mantiene el conjunto activo de estados del AFND
        en cada paso, expandido por ε-clausura tras cada transición.
        
        Algoritmo:
            1. current = ε-clausura({estado_inicial})
            2. Para cada símbolo s en text:
               a. next = move(current, s)
               b. current = ε-clausura(next)
               c. Si current es vacío → rechazar de inmediato
            3. Si algún estado en current es de aceptación → aceptar
        
        Args:
            text (str): Cadena a reconocer.
        
        Returns:
            bool: True si el AFND acepta la cadena completa.
        """
        # Paso 1: estado inicial expandido por ε-clausura
        current = SubsetConstructor.epsilon_closure([self.nfa.start])

        # Paso 2: procesar cada carácter
        for symbol in text:
            next_states = SubsetConstructor.move(current, symbol)
            current     = SubsetConstructor.epsilon_closure(next_states)
            if not current:
                return False  # No hay estados activos → rechazo temprano

        # Paso 3: aceptar si algún estado activo es de aceptación
        return any(state.is_accept for state in current)

    def match(self, text: str) -> bool:
        """
        Verifica si el patrón coincide con la cadena COMPLETA.
        
        Equivalente a: re.fullmatch(pattern, text) en la librería estándar.
        
        Args:
            text (str): Cadena a verificar.
        
        Returns:
            bool: True si toda la cadena es aceptada por el patrón.
        
        Ejemplo:
            engine = RegexEngine(r"\d+")
            engine.match("123")    # True
            engine.match("12x")    # False  ← 'x' no es dígito
            engine.match("")       # False  ← requiere al menos un dígito
        """
        return self._simulate(text)

    def search(self, text: str) -> list:
        """
        Busca TODAS las ocurrencias no solapadas del patrón en `text`.
        
        Usa un enfoque de ventana deslizante: para cada posición de inicio `i`,
        intenta extender el match hasta la posición más larga posible `j`.
        Si encuentra un match, lo registra y salta al siguiente inicio en j.
        
        Complejidad: O(n² × |AFND|) en el peor caso.
        Para textos muy largos se recomienda el enfoque con AFD materializado.
        
        Args:
            text (str): Texto donde buscar.
        
        Returns:
            list[dict]: Lista de coincidencias. Cada elemento tiene:
                - 'value' (str): Subcadena que hizo match
                - 'start' (int): Posición inicial (inclusiva)
                - 'end'   (int): Posición final (exclusiva)
        
        Ejemplo:
            engine = RegexEngine(r"\d+")
            engine.search("hay 123 y 456 aquí")
            # → [{'value': '123', 'start': 4, 'end': 7},
            #    {'value': '456', 'start': 10, 'end': 13}]
        """
        matches = []
        i = 0
        n = len(text)

        while i < n:
            best_end = -1  # Mejor posición de fin encontrada desde i

            # Simular el AFND desde la posición i
            current = SubsetConstructor.epsilon_closure([self.nfa.start])

            # Verificar si el estado inicial ya es de aceptación (ε acepta)
            if any(state.is_accept for state in current):
                best_end = i

            j = i
            while j < n:
                # Consumir el carácter en posición j
                next_states = SubsetConstructor.move(current, text[j])
                current     = SubsetConstructor.epsilon_closure(next_states)

                if not current:
                    break  # No hay más estados → no hay match más largo

                j += 1

                # Si algún estado es de aceptación, registrar esta posición
                if any(state.is_accept for state in current):
                    best_end = j

            if best_end > i:
                # Encontró un match desde i hasta best_end
                matches.append({
                    'value': text[i:best_end],
                    'start': i,
                    'end':   best_end
                })
                i = best_end  # Avanzar al siguiente inicio
            else:
                i += 1  # No hay match desde esta posición → avanzar uno

        return matches

    def __repr__(self):
        return f"RegexEngine(pattern={repr(self.pattern)})"
