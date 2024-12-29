from __future__ import annotations

import typing

from ..errors.errors import SyntaxError
from ..handlers.error_handler import throw
from .tokens import Markers, TokensMarkers, is_include, new

if typing.TYPE_CHECKING:
    from elements.base_object import BaseObject


def error(err: str = "") -> None:
    return throw(SyntaxError(err))


class Token:
    def __init__(self, value_type: str, value: BaseObject | typing.Any) -> None:
        self.value = value
        self.value_type = value_type

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.value_type}, {self.value})"


class Lexer:
    def __init__(self, code: str) -> None:
        self.code = code
        self.pos = 0
        self.current_char = self.code[self.pos]

    def __next__(self) -> BaseObject | typing.Any:
        return self.next()

    def next(self) -> None:
        self.pos += 1
        if self.pos >= len(self.code):
            self.current_char = None
            return
        self.current_char = self.code[self.pos]

    def integer(self) -> int:
        result = []
        while self.current_char is not None and self.current_char.isdigit():
            result.append(self.current_char)
            self.next()
        return int("".join(result))

    def skip_space(self) -> None:
        while self.current_char is not None and self.current_char.isspace():
            self.next()

    def next_token(self) -> Token:
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_space()
            if self.current_char.isdigit():
                return Token("INTEGER", self.integer())
            if is_include(self.current_char):
                char = self.current_char
                self.next()
                return new(char)
            error(err=f"Unexcepted token {self.current_char}")
        return Token("EOF", None)


class AST:
    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}({', '.join(map(str, self.sub_nodes))})".replace(
                "([, ])",
                "",
            )
        )


class BinOp(AST):
    def __init__(self, left: AST, op: Token, right: AST) -> None:
        self.left = left
        self.op = op
        self.right = right

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.left} {self.op.value} {self.right})"


class Num(AST):
    def __init__(self, token: Token) -> None:
        self.token = token
        self.value = token.value


class Tree:
    def __init__(self, left: Tree, node: Tree, right: Tree) -> None:
        self.left = left
        self.node = node
        self.right = right

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.left} {self.node} {self.right})"

    def visit(self):
        while not (
            self.left is None and self.right is None
        ):  # 不是叶节点就一直递归调用
            print(self.left, self.node, self.right)
            self.left = self.left.visit()  # 树左节点一直递归
            self.right = self.right.visit()  # 树右节点一直递归
        # 已经递归到了叶节点
        if self.node == TokensMarkers.PLUS.value:
            return self.left + self.right
        if self.node == TokensMarkers.MINUS.value:
            return self.left - self.right
        if self.node == TokensMarkers.MUL.value:
            return self.left * self.right
        if self.node == TokensMarkers.DIV.value:
            return self.left / self.right
        return None


class Parser:
    def __init__(self, lexer: Lexer) -> None:
        self.lexer = lexer
        self.current_token = self.lexer.next_token()

    def eat(self, token_type: str) -> None:
        if self.current_token.value_type == token_type:
            self.current_token = self.lexer.next_token()
            return
        error()

    def factor(self) -> Tree | None:
        token = self.current_token  # 获取记号
        if token.value_type == Markers.INTEGER.value:  # 整数
            self.eat(Markers.INTEGER.value)
            return Num(token)  # 返回数字节点对象

        if token.value_type == TokensMarkers.LPAREN.value:
            self.eat(TokensMarkers.LPAREN.value)
            tree = self.expr()
            self.eat(TokensMarkers.RPAREN.value)
            return tree
        return None

    def term(self) -> Tree | BinOp:
        node = self.factor()
        while self.current_token.value_type in (
            Markers.MUL.value,
            Markers.DIV.value,
        ):
            token = self.current_token
            if token.value_type == Markers.MUL.value:
                self.eat(Markers.MUL.value)
            if token.value_type == Markers.DIV.value:
                self.eat(Markers.DIV.value)
            node = BinOp(left=node, op=token, right=self.factor())
        return node

    def expr(self) -> Tree | BinOp:
        tree_node = self.term()
        while self.current_token.value_type in (
            Markers.PLUS.value,
            Markers.MINUS.value,
        ):
            token = self.current_token
            if token.value_type == Markers.PLUS.value:
                self.eat(Markers.PLUS.value)
            if token.value_type == Markers.MINUS.value:
                self.eat(Markers.MINUS.value)
            tree_node = BinOp(left=tree_node, op=token, right=self.term())
        return tree_node

    def parse(self) -> Tree | BinOp:
        return self.expr()


class NodeVisitor:
    def visit(self, node: AST) -> BaseObject | None:
        method_name = "visit_" + type(node).__name__  # equals '__getattribute__'
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)

    def generic_visit(self, node: AST) -> None:
        msg = f"No visit_{type(node).__name__} method"
        throw(SyntaxError(msg))


class Interpreter(NodeVisitor):
    def __init__(self, parser: Parser) -> None:
        self.parser = parser

    def visit_BinOp(self, node: BinOp):  # noqa: N802
        if node.op.value_type == Markers.PLUS.value:
            return self.visit(node.left) + self.visit(node.right)
        if node.op.value_type == Markers.MINUS.value:
            return self.visit(node.left) - self.visit(node.right)
        if node.op.value_type == Markers.MUL.value:
            return self.visit(node.left) * self.visit(node.right)
        if node.op.value_type == Markers.DIV.value:
            return self.visit(node.left) // self.visit(node.right)
        return None

    def visit_Num(  # noqa: N802
        self,
        node: Token,
    ) -> BaseObject | None:  # For bypassing 'generic_visit', it MUST BE a upper char.
        return node.value

    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)


if __name__ == "__main__":
    while True:  # 循环获取输入
        try:
            text = input("(AST Demo) >> ")
        except EOFError:
            break
        if not text:
            continue

        lexer = Lexer(text)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        print(f"({text}) -> {result}")
