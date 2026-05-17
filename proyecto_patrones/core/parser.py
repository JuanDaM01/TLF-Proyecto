# =============================================================================
# core/parser.py
# Parser de expresiones regulares → Árbol Sintáctico Abstracto (AST)
#
# Gramática reconocida (BNF):
#   expr    ::= concat ('|' concat)*
#   concat  ::= quantify (quantify)*
#   quantify::= atom ('*' | '+' | '?')?
#   atom    ::= CHAR | DOT | CHAR_CLASS | '(' expr ')'
#
# El parser implementa el método de descenso recursivo (Recursive Descent),
# uno de los enfoques más claros para construir parsers LL(1).
# =============================================================================

from .lexer import TokenType


# ---------------------------------------------------------------------------
# Nodos del AST
# Cada clase representa un nodo en el árbol sintáctico.
# El árbol codifica la estructura de la expresión regular de forma jerárquica.
# ---------------------------------------------------------------------------

class ASTNode:
    """Clase base para todos los nodos del AST."""
    pass


class CharNode(ASTNode):
    """
    Nodo hoja: representa un carácter literal.
    Ejemplo: 'a', '5', '@'
    """
    def __init__(self, char):
        self.char = char

    def __repr__(self):
        return f"Char({repr(self.char)})"


class ClassNode(ASTNode):
    """
    Nodo hoja: representa una clase de caracteres [a-z], \d, etc.
    Almacena el set de caracteres aceptados por la clase.
    """
    def __init__(self, chars):
        self.chars = chars  # set de caracteres válidos

    def __repr__(self):
        return f"Class({len(self.chars)} chars)"


class DotNode(ASTNode):
    """
    Nodo hoja: representa el metacarácter '.' (cualquier carácter
    excepto newline en la mayoría de implementaciones).
    """
    def __repr__(self):
        return "Dot(.)"


class ConcatNode(ASTNode):
    """
    Nodo interior: representa la concatenación de dos subexpresiones.
    r1 · r2 acepta cadenas de la forma uv donde u ∈ L(r1), v ∈ L(r2).
    """
    def __init__(self, left, right):
        self.left  = left
        self.right = right

    def __repr__(self):
        return f"Concat({self.left}, {self.right})"


class AltNode(ASTNode):
    """
    Nodo interior: representa la alternación (unión) r1 | r2.
    Acepta cadenas que pertenezcan a L(r1) o a L(r2).
    """
    def __init__(self, left, right):
        self.left  = left
        self.right = right

    def __repr__(self):
        return f"Alt({self.left} | {self.right})"


class StarNode(ASTNode):
    """
    Nodo interior: clausura de Kleene r*.
    Acepta cero o más repeticiones de L(child).
    """
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Star({self.child})"


class PlusNode(ASTNode):
    """
    Nodo interior: r+ = r · r*
    Acepta una o más repeticiones de L(child).
    Azúcar sintáctico: r+ ≡ Concat(r, Star(r))
    """
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Plus({self.child})"


class QuestionNode(ASTNode):
    """
    Nodo interior: r? = r | ε
    Acepta cero o una ocurrencia de L(child).
    Azúcar sintáctico: r? ≡ Alt(r, ε)
    """
    def __init__(self, child):
        self.child = child

    def __repr__(self):
        return f"Question({self.child})"


# ---------------------------------------------------------------------------
# Parser — Descenso Recursivo
# ---------------------------------------------------------------------------

class Parser:
    """
    Construye el AST de una expresión regular a partir de su lista de tokens.
    
    Implementa un parser de descenso recursivo para la gramática:
        expr    → concat ('|' concat)*
        concat  → quantify+
        quantify→ atom quantifier?
        atom    → CHAR | DOT | CLASS | '(' expr ')'
    
    Ejemplo de uso:
        from core.lexer import Lexer
        from core.parser import Parser
        
        tokens = Lexer(r"[a-z]+@\w+").tokenize()
        ast = Parser(tokens).parse()
    """

    def __init__(self, tokens):
        self.tokens  = tokens
        self.pos     = 0

    def current(self):
        """Retorna el token actual sin consumirlo."""
        return self.tokens[self.pos]

    def consume(self, expected_type=None):
        """
        Consume y retorna el token actual.
        
        Args:
            expected_type: Si se indica, valida que el token sea de ese tipo.
        
        Raises:
            SyntaxError: Si el tipo no coincide con el esperado.
        """
        tok = self.tokens[self.pos]
        if expected_type and tok.type != expected_type:
            raise SyntaxError(
                f"Token esperado: {expected_type}, encontrado: {tok.type}"
            )
        self.pos += 1
        return tok

    def parse(self):
        """
        Punto de entrada del parser.
        
        Returns:
            ASTNode: Raíz del árbol sintáctico de la expresión regular.
        """
        ast = self._parse_expr()
        if self.current().type != TokenType.END:
            raise SyntaxError(
                f"Tokens inesperados al final: {self.current()}"
            )
        return ast

    def _parse_expr(self):
        """
        expr → concat ('|' concat)*
        
        Parsea la alternación (menor precedencia).
        """
        left = self._parse_concat()

        while self.current().type == TokenType.PIPE:
            self.consume(TokenType.PIPE)
            right = self._parse_concat()
            left  = AltNode(left, right)

        return left

    def _parse_concat(self):
        """
        concat → quantify+
        
        Parsea la concatenación (precedencia media).
        Consume tokens mientras haya átomos disponibles.
        """
        # Tipos que pueden iniciar un átomo
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
        """
        quantify → atom ('*' | '+' | '?')?
        
        Parsea un átomo opcionalmente seguido de un cuantificador.
        """
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
        """
        atom → CHAR | DOT | CHAR_CLASS | '(' expr ')'
        
        Parsea la unidad atómica con mayor precedencia.
        
        Raises:
            SyntaxError: Si no hay un átomo válido.
        """
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
