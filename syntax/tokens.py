from enum import Enum

from .ast import Token


class Markers(Enum):
    INTEGER = "INTEGER"
    PLUS = "PLUS"
    MINUS = "MINUS"
    MUL = "MUL"
    DIV = "DIV"
    LPAREN = "LPAREN"
    RPAREN = "RPAREN"
    EOF = "EOF"


class TokensMarkers(Enum):
    PLUS = "+"
    MINUS = "-"
    MUL = "*"
    DIV = "/"
    LPAREN = "("
    RPAREN = ")"


def new(name: str) -> Token:
    try:
        return Token(name, getattr(TokensMarkers, name).value)
    except AttributeError:
        return Token(TokensMarkers(name).name, name)


def is_include(name_or_op: str) -> bool:
    return name_or_op in Markers or name_or_op in TokensMarkers
