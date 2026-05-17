# =============================================================================
# core/lexer.py
# Tokenizador del motor de expresiones regulares
# Convierte una cadena regex en una lista de tokens con tipo y valor
#
# Autor: Proyecto - Teoría de Lenguajes Formales
# Versión: 1.0
# =============================================================================

class TokenType:
    """
    Enumera todos los tipos de tokens reconocidos por el lexer.
    Cada tipo representa un elemento sintáctico de una expresión regular.
    """
    CHAR       = 'CHAR'       # Carácter literal: a, b, 1, @, etc.
    DOT        = 'DOT'        # Metacarácter '.': cualquier carácter
    STAR       = 'STAR'       # Cuantificador '*': cero o más
    PLUS       = 'PLUS'       # Cuantificador '+': uno o más
    QUESTION   = 'QUESTION'   # Cuantificador '?': cero o uno
    PIPE       = 'PIPE'       # Alternación '|': r1 | r2
    LPAREN     = 'LPAREN'     # Paréntesis izquierdo '('
    RPAREN     = 'RPAREN'     # Paréntesis derecho ')'
    LBRACKET   = 'LBRACKET'   # Clase de caracteres '[' (inicio)
    CHAR_CLASS = 'CHAR_CLASS' # Clase de caracteres expandida: [a-z] → set
    ESCAPE     = 'ESCAPE'     # Secuencia de escape: \d, \w, \s, \D, etc.
    END        = 'END'        # Fin de la expresión regular


class Token:
    """
    Representa un token individual con su tipo y valor.
    
    Atributos:
        type  (str): Tipo del token (de TokenType)
        value (any): Valor asociado. Para CHAR es un carácter;
                     para CHAR_CLASS es un set de caracteres válidos.
    """
    def __init__(self, token_type, value):
        self.type  = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"


class Lexer:
    """
    Análisis léxico de una expresión regular.
    
    Transforma la cadena de la expresión regular en una secuencia
    de tokens. Soporta:
        - Caracteres literales
        - Metacaracteres: . * + ? | ( ) [ ]
        - Secuencias de escape: \d \w \s \D \W \S \n \t
        - Clases de caracteres con rangos: [a-z], [0-9], [^abc]
        - Escape de metacaracteres: \. \* etc.
    
    Ejemplo de uso:
        lexer = Lexer(r"[a-z]+@\w+\\.com")
        tokens = lexer.tokenize()
    """

    # Mapa de escapes simples: \n → newline, \t → tab, etc.
    SIMPLE_ESCAPES = {
        'n': '\n',
        't': '\t',
        'r': '\r',
    }

    # Mapa de clases de escape estándar (\d, \w, \s y sus negaciones)
    CLASS_ESCAPES = {
        'd': set('0123456789'),
        'w': set('abcdefghijklmnopqrstuvwxyz'
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                 '0123456789_'),
        's': set(' \t\n\r\f\v'),
    }

    def __init__(self, pattern: str):
        """
        Inicializa el lexer con el patrón de expresión regular.
        
        Args:
            pattern (str): La expresión regular a tokenizar.
        """
        self.pattern = pattern
        self.pos     = 0           # Posición actual en el patrón
        self.tokens  = []          # Lista de tokens generados

    def current(self):
        """Retorna el carácter actual sin avanzar, o None si llegó al fin."""
        if self.pos < len(self.pattern):
            return self.pattern[self.pos]
        return None

    def advance(self):
        """Avanza la posición y retorna el carácter consumido."""
        ch = self.pattern[self.pos]
        self.pos += 1
        return ch

    def _expand_escape(self, ch: str):
        """
        Expande una secuencia de escape \X en su representación.
        
        Args:
            ch (str): El carácter después de la barra invertida.
        
        Returns:
            Token: El token correspondiente a la secuencia de escape.
        
        Raises:
            ValueError: Si la secuencia de escape no es reconocida.
        """
        if ch in self.SIMPLE_ESCAPES:
            # \n, \t, \r → carácter especial
            return Token(TokenType.CHAR, self.SIMPLE_ESCAPES[ch])

        if ch in self.CLASS_ESCAPES:
            # \d → {0..9}, \w → {a-z,A-Z,0-9,_}, \s → espacios
            return Token(TokenType.CHAR_CLASS, self.CLASS_ESCAPES[ch])

        upper = ch.upper()
        if upper in self.CLASS_ESCAPES:
            # \D → negación de \d, \W → negación de \w, etc.
            # El complemento se representa como todos los ASCII minus la clase
            all_chars = set(chr(i) for i in range(32, 127))
            neg_class = all_chars - self.CLASS_ESCAPES[upper]
            return Token(TokenType.CHAR_CLASS, neg_class)

        # Escape de metacaracter: \. \* \+ etc. → literal
        return Token(TokenType.CHAR, ch)

    def _parse_char_class(self):
        """
        Parsea una clase de caracteres [...] y retorna un Token CHAR_CLASS.
        
        Soporta:
            - Caracteres individuales: [abc]
            - Rangos: [a-z], [0-9], [A-Z]
            - Negación: [^abc]
            - Escapes dentro de la clase: [\d\s]
            - Combinaciones: [a-z0-9_\-]
        
        Returns:
            Token: Token de tipo CHAR_CLASS con el set de caracteres válidos.
        
        Raises:
            ValueError: Si la clase no se cierra correctamente.
        """
        chars = set()
        negated = False

        # Verificar si la clase está negada [^...]
        if self.current() == '^':
            negated = True
            self.advance()

        # Parsear el contenido de la clase
        while self.current() is not None and self.current() != ']':
            if self.current() == '\\':
                self.advance()  # consumir '\'
                esc_ch = self.advance()
                tok = self._expand_escape(esc_ch)
                if tok.type == TokenType.CHAR_CLASS:
                    chars |= tok.value
                else:
                    chars.add(tok.value)
            else:
                ch = self.advance()
                # Verificar si es un rango: a-z
                if self.current() == '-' and self.pos + 1 < len(self.pattern) \
                        and self.pattern[self.pos + 1] != ']':
                    self.advance()  # consumir '-'
                    end_ch = self.advance()
                    # Expandir el rango carácter a carácter
                    if ord(ch) > ord(end_ch):
                        raise ValueError(
                            f"Rango inválido en clase de caracteres: [{ch}-{end_ch}]"
                        )
                    for code in range(ord(ch), ord(end_ch) + 1):
                        chars.add(chr(code))
                else:
                    chars.add(ch)

        if self.current() != ']':
            raise ValueError("Clase de caracteres no cerrada: falta ']'")
        self.advance()  # consumir ']'

        # Aplicar negación si corresponde
        if negated:
            all_chars = set(chr(i) for i in range(32, 127))
            chars = all_chars - chars

        return Token(TokenType.CHAR_CLASS, chars)

    def tokenize(self):
        """
        Realiza el análisis léxico completo del patrón.
        
        Returns:
            list[Token]: Lista ordenada de tokens representando
                         la expresión regular.
        
        Raises:
            ValueError: Si se encuentra una secuencia inválida.
        """
        self.tokens = []
        self.pos    = 0

        # Mapa de metacaracteres simples a tipos de token
        meta = {
            '.': TokenType.DOT,
            '*': TokenType.STAR,
            '+': TokenType.PLUS,
            '?': TokenType.QUESTION,
            '|': TokenType.PIPE,
            '(': TokenType.LPAREN,
            ')': TokenType.RPAREN,
        }

        while self.pos < len(self.pattern):
            ch = self.advance()

            if ch == '\\':
                # Secuencia de escape
                if self.current() is None:
                    raise ValueError("Escape al final de la expresión regular")
                esc_ch = self.advance()
                self.tokens.append(self._expand_escape(esc_ch))

            elif ch == '[':
                # Clase de caracteres
                self.tokens.append(self._parse_char_class())

            elif ch in meta:
                # Metacaracter simple
                self.tokens.append(Token(meta[ch], ch))

            else:
                # Carácter literal
                self.tokens.append(Token(TokenType.CHAR, ch))

        self.tokens.append(Token(TokenType.END, None))
        return self.tokens
