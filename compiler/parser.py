"""
한국어 프로그래밍 언어 - 파서 (Parser)
구문 분석 및 AST 생성
"""

from dataclasses import dataclass
from typing import List, Optional, Any
from compiler.lexer import Token, TokenType, Lexer

# AST 노드 정의
@dataclass
class ASTNode:
    pass

@dataclass
class Program(ASTNode):
    statements: List[ASTNode]

@dataclass
class VarDeclaration(ASTNode):
    name: str
    value: ASTNode

@dataclass
class Assignment(ASTNode):
    name: str
    value: ASTNode

@dataclass
class BinaryOp(ASTNode):
    left: ASTNode
    op: str
    right: ASTNode

@dataclass
class UnaryOp(ASTNode):
    op: str
    operand: ASTNode

@dataclass
class Number(ASTNode):
    value: float

@dataclass
class String(ASTNode):
    value: str

@dataclass
class Boolean(ASTNode):
    value: bool

@dataclass
class Identifier(ASTNode):
    name: str

@dataclass
class PrintStatement(ASTNode):
    expression: ASTNode

@dataclass
class IfStatement(ASTNode):
    condition: ASTNode
    then_block: List[ASTNode]
    else_block: Optional[List[ASTNode]] = None

@dataclass
class WhileStatement(ASTNode):
    condition: ASTNode
    body: List[ASTNode]

@dataclass
class FunctionDeclaration(ASTNode):
    name: str
    parameters: List[str]
    body: List[ASTNode]

@dataclass
class FunctionCall(ASTNode):
    name: str
    arguments: List[ASTNode]

@dataclass
class ReturnStatement(ASTNode):
    value: ASTNode

class Parser:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.pos = 0
    
    def current_token(self) -> Token:
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return self.tokens[-1]  # EOF
    
    def peek_token(self, offset=1) -> Token:
        pos = self.pos + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return self.tokens[-1]
    
    def advance(self):
        if self.pos < len(self.tokens) - 1:
            self.pos += 1
    
    def expect(self, token_type: TokenType) -> Token:
        token = self.current_token()
        if token.type != token_type:
            raise SyntaxError(f"Expected {token_type}, got {token.type} at line {token.line}")
        self.advance()
        return token
    
    def skip_newlines(self):
        while self.current_token().type == TokenType.NEWLINE:
            self.advance()
    
    def parse(self) -> Program:
        statements = []
        self.skip_newlines()
        
        while self.current_token().type != TokenType.EOF:
            stmt = self.parse_statement()
            if stmt:
                statements.append(stmt)
            self.skip_newlines()
        
        return Program(statements)
    
    def parse_statement(self) -> Optional[ASTNode]:
        self.skip_newlines()
        token = self.current_token()
        
        if token.type == TokenType.VAR:
            return self.parse_var_declaration()
        elif token.type == TokenType.PRINT:
            return self.parse_print_statement()
        elif token.type == TokenType.IF:
            return self.parse_if_statement()
        elif token.type == TokenType.WHILE:
            return self.parse_while_statement()
        elif token.type == TokenType.FUNC:
            return self.parse_function_declaration()
        elif token.type == TokenType.RETURN:
            return self.parse_return_statement()
        elif token.type == TokenType.IDENTIFIER:
            # 함수 호출 또는 할당
            if self.peek_token().type == TokenType.LPAREN:
                return self.parse_function_call()
            elif self.peek_token().type == TokenType.ASSIGN:
                return self.parse_assignment()
        elif token.type == TokenType.NEWLINE:
            self.advance()
            return None
        
        return None
    
    def parse_var_declaration(self) -> VarDeclaration:
        self.expect(TokenType.VAR)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.skip_newlines()
        return VarDeclaration(name, value)
    
    def parse_assignment(self) -> Assignment:
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.skip_newlines()
        return Assignment(name, value)
    
    def parse_print_statement(self) -> PrintStatement:
        self.expect(TokenType.PRINT)
        # 괄호는 선택사항
        has_paren = False
        if self.current_token().type == TokenType.LPAREN:
            self.advance()
            has_paren = True
        
        expr = self.parse_expression()
        
        if has_paren:
            self.expect(TokenType.RPAREN)
        
        self.skip_newlines()
        return PrintStatement(expr)
    
    def parse_if_statement(self) -> IfStatement:
        self.expect(TokenType.IF)
        # 괄호는 선택사항
        has_paren = False
        if self.current_token().type == TokenType.LPAREN:
            self.advance()
            has_paren = True
        
        condition = self.parse_expression()
        
        if has_paren:
            self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        then_block = []
        while self.current_token().type not in [TokenType.ELSE, TokenType.EOF]:
            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                if self.current_token().type in [TokenType.ELSE, TokenType.VAR, TokenType.FUNC, TokenType.IF, TokenType.PRINT]:
                    break
                continue
            stmt = self.parse_statement()
            if stmt:
                then_block.append(stmt)
            if self.current_token().type in [TokenType.ELSE, TokenType.EOF]:
                break
        
        else_block = None
        if self.current_token().type == TokenType.ELSE:
            self.expect(TokenType.ELSE)
            self.expect(TokenType.COLON)
            self.skip_newlines()
            else_block = []
            while self.current_token().type != TokenType.EOF:
                if self.current_token().type == TokenType.NEWLINE:
                    self.advance()
                    if self.current_token().type in [TokenType.VAR, TokenType.FUNC, TokenType.IF, TokenType.PRINT]:
                        break
                    continue
                stmt = self.parse_statement()
                if stmt:
                    else_block.append(stmt)
                if self.current_token().type in [TokenType.VAR, TokenType.FUNC, TokenType.IF, TokenType.PRINT, TokenType.EOF]:
                    break
        
        return IfStatement(condition, then_block, else_block)
    
    def parse_while_statement(self) -> WhileStatement:
        self.expect(TokenType.WHILE)
        # 괄호는 선택사항
        has_paren = False
        if self.current_token().type == TokenType.LPAREN:
            self.advance()
            has_paren = True
        
        condition = self.parse_expression()
        
        if has_paren:
            self.expect(TokenType.RPAREN)
        
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        body = []
        while self.current_token().type != TokenType.EOF:
            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                if self.current_token().type in [TokenType.VAR, TokenType.FUNC, TokenType.IF, TokenType.PRINT]:
                    break
                continue
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            if self.current_token().type in [TokenType.VAR, TokenType.FUNC, TokenType.IF, TokenType.PRINT, TokenType.EOF]:
                break
        
        return WhileStatement(condition, body)
    
    def parse_function_declaration(self) -> FunctionDeclaration:
        self.expect(TokenType.FUNC)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        
        parameters = []
        if self.current_token().type == TokenType.IDENTIFIER:
            parameters.append(self.expect(TokenType.IDENTIFIER).value)
            while self.current_token().type == TokenType.COMMA:
                self.advance()
                parameters.append(self.expect(TokenType.IDENTIFIER).value)
        
        self.expect(TokenType.RPAREN)
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        body = []
        while self.current_token().type != TokenType.EOF:
            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                if self.current_token().type in [TokenType.VAR, TokenType.FUNC, TokenType.IF, TokenType.PRINT]:
                    break
                continue
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
            if self.current_token().type in [TokenType.VAR, TokenType.FUNC, TokenType.IF, TokenType.PRINT, TokenType.EOF]:
                break
        
        return FunctionDeclaration(name, parameters, body)
    
    def parse_function_call(self) -> FunctionCall:
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LPAREN)
        
        arguments = []
        if self.current_token().type != TokenType.RPAREN:
            arguments.append(self.parse_expression())
            while self.current_token().type == TokenType.COMMA:
                self.advance()
                arguments.append(self.parse_expression())
        
        self.expect(TokenType.RPAREN)
        self.skip_newlines()
        return FunctionCall(name, arguments)
    
    def parse_return_statement(self) -> ReturnStatement:
        self.expect(TokenType.RETURN)
        value = self.parse_expression()
        self.skip_newlines()
        return ReturnStatement(value)
    
    def parse_expression(self) -> ASTNode:
        return self.parse_comparison()
    
    def parse_comparison(self) -> ASTNode:
        left = self.parse_additive()
        
        while self.current_token().type in [TokenType.EQ, TokenType.NE, 
                                            TokenType.GT, TokenType.LT,
                                            TokenType.GE, TokenType.LE]:
            op = self.current_token().value
            self.advance()
            right = self.parse_additive()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_additive(self) -> ASTNode:
        left = self.parse_multiplicative()
        
        while self.current_token().type in [TokenType.PLUS, TokenType.MINUS]:
            op = self.current_token().value
            self.advance()
            right = self.parse_multiplicative()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_multiplicative(self) -> ASTNode:
        left = self.parse_primary()
        
        while self.current_token().type in [TokenType.MULTIPLY, TokenType.DIVIDE]:
            op = self.current_token().value
            self.advance()
            right = self.parse_primary()
            left = BinaryOp(left, op, right)
        
        return left
    
    def parse_primary(self) -> ASTNode:
        token = self.current_token()
        
        if token.type == TokenType.NUMBER:
            self.advance()
            return Number(token.value)
        elif token.type == TokenType.STRING:
            self.advance()
            return String(token.value)
        elif token.type == TokenType.BOOLEAN:
            self.advance()
            return Boolean(token.value)
        elif token.type == TokenType.IDENTIFIER:
            if self.peek_token().type == TokenType.LPAREN:
                return self.parse_function_call()
            else:
                self.advance()
                return Identifier(token.value)
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        raise SyntaxError(f"Unexpected token {token.type} at line {token.line}")
