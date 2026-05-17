from .lexer import TokenType


class ASTNode:
    pass


class CharNode(ASTNode):
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return f"Char({repr(self.char)})"


class ClassNode(ASTNode):
    def __init__(self, chars):
        self.chars = chars

    def __repr__(self):
        return f"Class({len(self.chars)} chars)"


class DotNode(ASTNode):
    def __repr__(self):
        return "Dot(.)"


class ConcatNode(ASTNode):
    def __init__(self, left, right):
        self.left  = left
        self.right = right

    def __repr__(self):
        return f"Concat({self.left}, {self.right})"


class AltNode(ASTNode):
    def __init__(self, left, right):
        self.left  = left
        self.right = right

    def __repr__(self):
        return f"Alt({self.left} | {self.right})"


class StarNode(ASTNode):
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Star({self.child})"


class PlusNode(ASTNode):
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Plus({self.child})"


class QuestionNode(ASTNode):
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Question({self.child})"


class Parser:
    def __init__(self, tokens):
        self.tokens  = tokens
        self.pos     = 0

    def current(self):
        return self.tokens[self.pos]

    def consume(self, expected_type=None):
        tok = self.tokens[self.pos]
        if expected_type and tok.type != expected_type:
            raise SyntaxError(
                f"Token esperado: {expected_type}, encontrado: {tok.type}"
            )
        self.pos += 1
        return tok

    def parse(self):
        ast = self._parse_expr()
        if self.current().type != TokenType.END:
            raise SyntaxError(
                f"Tokens inesperados al final: {self.current()}"
            )
        return ast

    def _parse_expr(self):
        left = self._parse_concat()

        while self.current().type == TokenType.PIPE:
            self.consume(TokenType.PIPE)
            right = self._parse_concat()
            left  = AltNode(left, right)

        return left

    def _parse_concat(self):
        ATOM_STARTERS = {
            TokenType.CHAR, TokenType.DOT,
            TokenType.CHAR_CLASS, TokenType.LPAREN
        }

        left = self._parse_quantify()

        while self.current().type in ATOM_STARTERS:
            right = self._parse_quantify()
            left  = ConcatNode(left, right)

        return left

    def _parse_quantify(self):
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
