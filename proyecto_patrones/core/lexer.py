class TokenType:
    CHAR       = 'CHAR'
    DOT        = 'DOT'
    STAR       = 'STAR'
    PLUS       = 'PLUS'
    QUESTION   = 'QUESTION'
    PIPE       = 'PIPE'
    LPAREN     = 'LPAREN'
    RPAREN     = 'RPAREN'
    LBRACKET   = 'LBRACKET'
    CHAR_CLASS = 'CHAR_CLASS'
    ESCAPE     = 'ESCAPE'
    END        = 'END'


class Token:
    def __init__(self, token_type, value):
        self.type  = token_type
        self.value = value

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"


class Lexer:
    SIMPLE_ESCAPES = {
        'n': '\n',
        't': '\t',
        'r': '\r',
    }

    CLASS_ESCAPES = {
        'd': set('0123456789'),
        'w': set('abcdefghijklmnopqrstuvwxyz'
                 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                 '0123456789_'),
        's': set(' \t\n\r\f\v'),
    }

    def __init__(self, pattern: str):
        self.pattern = pattern
        self.pos     = 0
        self.tokens  = []

    def current(self):
        if self.pos < len(self.pattern):
            return self.pattern[self.pos]
        return None

    def advance(self):
        ch = self.pattern[self.pos]
        self.pos += 1
        return ch

    def _expand_escape(self, ch: str):
        if ch in self.SIMPLE_ESCAPES:
            return Token(TokenType.CHAR, self.SIMPLE_ESCAPES[ch])

        if ch in self.CLASS_ESCAPES:
            return Token(TokenType.CHAR_CLASS, self.CLASS_ESCAPES[ch])

        upper = ch.upper()
        if upper in self.CLASS_ESCAPES:
            all_chars = set(chr(i) for i in range(32, 127))
            neg_class = all_chars - self.CLASS_ESCAPES[upper]
            return Token(TokenType.CHAR_CLASS, neg_class)

        return Token(TokenType.CHAR, ch)

    def _parse_char_class(self):
        chars = set()
        negated = False

        if self.current() == '^':
            negated = True
            self.advance()

        while self.current() is not None and self.current() != ']':
            if self.current() == '\\':
                self.advance()
                esc_ch = self.advance()
                tok = self._expand_escape(esc_ch)
                if tok.type == TokenType.CHAR_CLASS:
                    chars |= tok.value
                else:
                    chars.add(tok.value)
            else:
                ch = self.advance()
                if self.current() == '-' and self.pos + 1 < len(self.pattern) \
                        and self.pattern[self.pos + 1] != ']':
                    self.advance()
                    end_ch = self.advance()
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
        self.advance()

        if negated:
            all_chars = set(chr(i) for i in range(32, 127))
            chars = all_chars - chars

        return Token(TokenType.CHAR_CLASS, chars)

    def tokenize(self):
        self.tokens = []
        self.pos    = 0

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
                if self.current() is None:
                    raise ValueError("Escape al final de la expresión regular")
                esc_ch = self.advance()
                self.tokens.append(self._expand_escape(esc_ch))

            elif ch == '[':
                self.tokens.append(self._parse_char_class())

            elif ch in meta:
                self.tokens.append(Token(meta[ch], ch))

            else:
                self.tokens.append(Token(TokenType.CHAR, ch))

        self.tokens.append(Token(TokenType.END, None))
        return self.tokens
