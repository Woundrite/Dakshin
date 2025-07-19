# Using TokenType and NonTerminal enums in the parsing table
from Tokens import TokenType, Token
from enum import Enum, auto

class ParserTokenType(Enum):
    # Literals
    IDENTIFIER = "IDENTIFIER"
    NUMBER = "NUMBER"
    STRING_LITERAL = "STRING_LITERAL"
    CHAR = "CHAR"
    TRUE = "true"
    FALSE = "false"
    NULL = "null"

    # Keywords
    LET = "let"
    FUNCTION = "function"
    CLASS = "class"
    INTERFACE = "interface"
    FINAL = "final"
    ABSTRACT = "abstract"
    STATIC = "static"
    OVERRIDE = "override"
    RETURN = "return"
    IF = "if"
    ELSE = "else"
    WHILE = "while"
    DO = "do"
    FOR = "for"
    SWITCH = "switch"
    CASE = "case"
    DEFAULT = "default"
    MATCH = "match"
    TRY = "try"
    CATCH = "catch"
    FINALLY = "finally"
    THROW = "throw"
    NEW = "new"
    DELETE = "delete"
    IMPORT = "import"
    FROM = "from"
    NAMESPACE = "namespace"
    PUBLIC = "public"
    PRIVATE = "private"
    PROTECTED = "protected"
    SUPER = "super"
    GC = "gc"
    
    # Control flow
    BREAK = "break"
    CONTINUE = "continue"
    AS = "as"
    IS = "is"
    INSTANCEOF = "instanceof"
    EXTENDS = "extends"
    IMPLEMENTS = "implements"
    THIS = "this"
    
    # Types
    INT = "int"
    FLOAT = "float"
    STRING = "string"
    DOUBLE = "double"
    BOOL = "bool"
    VOID = "void"
    ANY = "any"
    REF = "ref"
    CONST = "const"
    PTR = "ptr"
    TYPEOF = "typeof"
    SIZEOF = "sizeof"
    IN = "in"
    YIELD = "yield"
    AWAIT = "await"
    ASYNC = "async"
    ALLOC = "alloc"
    FREE = "free"
    
    # Brackets
    LBRACKET = "["
    RBRACKET = "]"

    # Operators and Punctuation
    EQ = "="
    EQEQ = "=="
    BANGEQ = "!="
    LT = "<"
    LTEQ = "<="
    GT = ">"
    GTEQ = ">="
    PLUS = "+"
    MINUS = "-"
    STAR = "*"
    SLASH = "/"
    MOD = "%"
    AMP = "&"
    PIPE = "|"
    CARET = "^"
    LTLT = "<<"
    GTGT = ">>"
    STARSTAR = "**"
    PIPEPIPE = "||"
    AMPAMP = "&&"
    BANG = "!"
    ARROW = "=>"
    FUNCTION_ARROW = "->"
    DOT = "."
    COLON = ":"
    SEMICOLON = ";"
    COMMA = ","
    LPAREN = "("
    RPAREN = ")"
    LBRACE = "{"
    RBRACE = "}"
    SLASHSLASH = "//"
    SLASHSTAR = "/*"
    STARSLASH = "*/"

    # Regex
    REGEX = "REGEX"

    EOF = "EOF"

def convert_token_types(tokens):
    """
    Convert a TokenType to a ParserTokenType.
    """
    if not all([isinstance(token_, Token) for token_ in tokens]):
        raise TypeError("All elements in token_type must be instances of TokenType")
    
    def identify_ident_type(token_type):
        """
        Identify if the token type is an identifier.
        """
        # the lexer also treats keywords as identifiers, so we need to check if the token type is a keyword
        match(token_type):
            case "let":
                return ParserTokenType.LET
            case "function":
                return ParserTokenType.FUNCTION
            case "fun":
                return ParserTokenType.FUNCTION
            case "class":
                return ParserTokenType.CLASS
            case "interface":
                return ParserTokenType.INTERFACE
            case "final":
                return ParserTokenType.FINAL
            case "abstract":
                return ParserTokenType.ABSTRACT
            case "static":
                return ParserTokenType.STATIC
            case "override":
                return ParserTokenType.OVERRIDE
            case "return":
                return ParserTokenType.RETURN
            case "if":
                return ParserTokenType.IF
            case "else":
                return ParserTokenType.ELSE
            case "while":
                return ParserTokenType.WHILE
            case "do":
                return ParserTokenType.DO
            case "for":
                return ParserTokenType.FOR
            case "switch":
                return ParserTokenType.SWITCH
            case "case":
                return ParserTokenType.CASE
            case "default":
                return ParserTokenType.DEFAULT
            case "match":
                return ParserTokenType.MATCH
            case "try":
                return ParserTokenType.TRY
            case "catch":
                return ParserTokenType.CATCH
            case "finally":
                return ParserTokenType.FINALLY
            case "throw":
                return ParserTokenType.THROW
            case "new":
                return ParserTokenType.NEW
            case "delete":
                return ParserTokenType.DELETE
            case "import":
                return ParserTokenType.IMPORT
            case "from":
                return ParserTokenType.FROM
            case "namespace":
                return ParserTokenType.NAMESPACE
            case "public":
                return ParserTokenType.PUBLIC
            case "private":
                return ParserTokenType.PRIVATE
            case "protected":
                return ParserTokenType.PROTECTED
            case "super":
                return ParserTokenType.SUPER
            case "gc":
                return ParserTokenType.GC
            case "true":
                return ParserTokenType.TRUE
            case "false":
                return ParserTokenType.FALSE
            case "null":
                return ParserTokenType.NULL
            case "break":
                return ParserTokenType.BREAK
            case "continue":
                return ParserTokenType.CONTINUE
            case "as":
                return ParserTokenType.AS
            case "is":
                return ParserTokenType.IS
            case "instanceof":
                return ParserTokenType.INSTANCEOF
            case "extends":
                return ParserTokenType.EXTENDS
            case "implements":
                return ParserTokenType.IMPLEMENTS
            case "this":
                return ParserTokenType.THIS
            case "int":
                return ParserTokenType.INT
            case "float":
                return ParserTokenType.FLOAT
            case "string":
                return ParserTokenType.STRING
            case "char":
                return ParserTokenType.CHAR
            case "bool":
                return ParserTokenType.BOOL
            case "void":
                return ParserTokenType.VOID
            case "any":
                return ParserTokenType.ANY
            case "double":
                return ParserTokenType.DOUBLE
            case "ref":
                return ParserTokenType.REF
            case "const":
                return ParserTokenType.CONST
            case "ptr":
                return ParserTokenType.PTR
            case "typeof":
                return ParserTokenType.TYPEOF
            case "sizeof":
                return ParserTokenType.SIZEOF
            case "in":
                return ParserTokenType.IN
            case "yield":
                return ParserTokenType.YIELD
            case "await":
                return ParserTokenType.AWAIT
            case "async":
                return ParserTokenType.ASYNC
            case "alloc":
                return ParserTokenType.ALLOC
            case "free":
                return ParserTokenType.FREE
            case _:
                # if the token type is not a keyword, then it is an identifier
                return ParserTokenType.IDENTIFIER

    toks = []
    for i in tokens:
        # if the tokentype is an identifier, figure out which identifier it is
        if i.type == TokenType.IDENT:
            toks.append(Token(identify_ident_type(i.value), i.value))
        elif i.type == TokenType.INTEGER or i.type == TokenType.FLOAT or i.type == TokenType.BINARY or i.type == TokenType.HEX:
            toks.append(Token(ParserTokenType.NUMBER, i.value))
        elif i.type == TokenType.STRING:
            toks.append(Token(ParserTokenType.STRING_LITERAL, i.value))
        elif i.type == TokenType.REGEX:
            toks.append(Token(ParserTokenType.REGEX, i.value))
        elif i.type == TokenType.ASSIGN:
            toks.append(Token(ParserTokenType.EQ, i.value))
        elif i.type == TokenType.ARROW:
            toks.append(Token(ParserTokenType.ARROW, i.value))
        elif i.type == TokenType.FUNCTION_ARROW:
            toks.append(Token(ParserTokenType.FUNCTION_ARROW, i.value))
        elif i.type == TokenType.EQUAL:
            toks.append(Token(ParserTokenType.EQEQ, i.value))
        elif i.type == TokenType.NEQUAL:
            toks.append(Token(ParserTokenType.BANGEQ, i.value))
        elif i.type == TokenType.LT:
            toks.append(Token(ParserTokenType.LT, i.value))
        elif i.type == TokenType.LTE:
            toks.append(Token(ParserTokenType.LTEQ, i.value))
        elif i.type == TokenType.GT:
            toks.append(Token(ParserTokenType.GT, i.value))
        elif i.type == TokenType.GTE:
            toks.append(Token(ParserTokenType.GTEQ, i.value))
        elif i.type == TokenType.PLUS:
            toks.append(Token(ParserTokenType.PLUS, i.value))
        elif i.type == TokenType.MINUS:
            toks.append(Token(ParserTokenType.MINUS, i.value))
        elif i.type == TokenType.MUL:
            toks.append(Token(ParserTokenType.STAR, i.value))
        elif i.type == TokenType.DIV:
            toks.append(Token(ParserTokenType.SLASH, i.value))
        elif i.type == TokenType.MOD:
            toks.append(Token(ParserTokenType.MOD, i.value))
        elif i.type == TokenType.BITWISE_AND:
            toks.append(Token(ParserTokenType.AMP, i.value))
        elif i.type == TokenType.OR:
            toks.append(Token(ParserTokenType.PIPEPIPE, i.value))
        elif i.type == TokenType.AND:
            toks.append(Token(ParserTokenType.AMPAMP, i.value))
        elif i.type == TokenType.NOT:
            toks.append(Token(ParserTokenType.BANG, i.value))
        elif i.type == TokenType.COLON:
            toks.append(Token(ParserTokenType.COLON, i.value))
        elif i.type == TokenType.SEMICOLON:
            toks.append(Token(ParserTokenType.SEMICOLON, i.value))
        elif i.type == TokenType.COMMA:
            toks.append(Token(ParserTokenType.COMMA, i.value))
        elif i.type == TokenType.LPAREN:
            toks.append(Token(ParserTokenType.LPAREN, i.value))
        elif i.type == TokenType.RPAREN:
            toks.append(Token(ParserTokenType.RPAREN, i.value))
        elif i.type == TokenType.LBRACE:
            toks.append(Token(ParserTokenType.LBRACE, i.value))
        elif i.type == TokenType.RBRACE:
            toks.append(Token(ParserTokenType.RBRACE, i.value))
        elif i.type == TokenType.LBRACKET:
            toks.append(Token(ParserTokenType.LBRACKET, i.value))
        elif i.type == TokenType.RBRACKET:
            toks.append(Token(ParserTokenType.RBRACKET, i.value))
        elif i.type == TokenType.BITWISE_XOR:
            toks.append(Token(ParserTokenType.CARET, i.value))
        elif i.type == TokenType.BITWISE_OR:
            toks.append(Token(ParserTokenType.PIPE, i.value))
        elif i.type == TokenType.SHIFT_LEFT:
            toks.append(Token(ParserTokenType.LTLT, i.value))
        elif i.type == TokenType.SHIFT_RIGHT:
            toks.append(Token(ParserTokenType.GTGT, i.value))
        elif i.type == TokenType.EXPONENT:
            toks.append(Token(ParserTokenType.STARSTAR, i.value))
        elif i.type == TokenType.DOT:
            toks.append(Token(ParserTokenType.DOT, i.value))
        elif i.type == TokenType.NEWLINE:
            # Skip newlines in parsing
            continue
        elif i.type == TokenType.WHITESPACE:
            # Skip whitespace in parsing
            continue
        elif i.type == TokenType.COMMENT:
            # Skip comments in parsing
            continue
        elif i.type == TokenType.MULTILINE_COMMENT_START:
            # Skip multiline comment start in parsing
            continue
        elif i.type == TokenType.MULTILINE_COMMENT_END:
            # Skip multiline comment end in parsing
            continue
        elif i.type == TokenType.EOF:
            toks.append(Token(ParserTokenType.EOF, i.value))
        elif i.type == TokenType.UNKNOWN:
            # For unknown tokens, we need to decide what to do
            # If it's a regex special character, it might need special handling
            print(f"Warning: Unknown token type {i.type} with value '{i.value}'")
            continue
        else:
            # For any unmapped tokens, try to preserve them or map to a default
            # You may need to add more ParserTokenType enums for complete coverage
            print(f"Warning: Unmapped token type {i.type} with value '{i.value}'")
            continue
    
    return toks