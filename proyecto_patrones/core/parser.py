from .lexer import TokenType

class ASTNode:
    """Nodo base del AST."""
    pass

class CharNode(ASTNode):
    """Caracter literal."""
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return f"Char({repr(self.char)})"

class ClassNode(ASTNode):
    """Clase de caracteres."""
    def __init__(self, chars):
        self.chars = chars

    def __repr__(self):
        return f"Class({len(self.chars)} chars)"

class DotNode(ASTNode):
    """Metacaracter punto."""
    def __repr__(self):
        return "Dot(.)"

class ConcatNode(ASTNode):
    """Concatenacion."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Concat({self.left}, {self.right})"

class AltNode(ASTNode):
    """Alternacion."""
    def __init__(self, left, right):
        self.left = left
        self.right = right

    def __repr__(self):
        return f"Alt({self.left} | {self.right})"

class StarNode(ASTNode):
    """Clausura de Kleene."""
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Star({self.child})"

class PlusNode(ASTNode):
    """Uno o mas."""
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Plus({self.child})"

class QuestionNode(ASTNode):
    """Opcional."""
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Question({self.child})"

class Parser:
    """Parser recursivo: expr | concat | quantify | atom."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def current(self):
        """Token actual."""
        return self.tokens[self.pos]

    def consume(self, expected_type=None):
        """Consume el token actual; SyntaxError si el tipo no coincide."""
        tok = self.tokens[self.pos]
        if expected_type and tok.type != expected_type:
            raise SyntaxError(
                f"Token esperado: {expected_type}, encontrado: {tok.type}"
            )
        self.pos += 1
        return tok

    def parse(self):
        """Raiz del AST."""
        ast = self._parse_expr()
        if self.current().type != TokenType.END:
            raise SyntaxError(
                f"Tokens inesperados al final: {self.current()}"
            )
        return ast

    def _parse_expr(self):
        """Alternacion."""
        left = self._parse_concat()

        while self.current().type == TokenType.PIPE:
            self.consume(TokenType.PIPE)
            right = self._parse_concat()
            left = AltNode(left, right)

        return left

    def _parse_concat(self):
        """Concatenacion implicita."""
        ATOM_STARTERS = {
            TokenType.CHAR, TokenType.DOT,
            TokenType.CHAR_CLASS, TokenType.LPAREN
        }

        left = self._parse_quantify()

        while self.current().type in ATOM_STARTERS:
            right = self._parse_quantify()
            left = ConcatNode(left, right)

        return left

    def _parse_quantify(self):
        """Atomo con cuantificador opcional."""
        node = self._parse_atom()

        tok_type = self.current().type
        if tok_type == TokenType.STAR:
            self.consume()
            return StarNode(node)
        elif tok_type == TokenType.PLUS:
            self.consume()
            return PlusNode(node)
        elif tok_type == TokenType.QUESTION:
            self.consume()
            return QuestionNode(node)

        return node

    def _parse_atom(self):
        """CHAR, DOT, clase o (expr)."""
        tok = self.current()

        if tok.type == TokenType.CHAR:
            self.consume()
            return CharNode(tok.value)

        elif tok.type == TokenType.DOT:
            self.consume()
            return DotNode()

        elif tok.type == TokenType.CHAR_CLASS:
            self.consume()
            return ClassNode(tok.value)

        elif tok.type == TokenType.LPAREN:
            self.consume(TokenType.LPAREN)
            node = self._parse_expr()
            self.consume(TokenType.RPAREN)
            return node

        raise SyntaxError(
            f"Átomo inesperado: token '{tok}' en posición {self.pos}"
        )
