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

@dataclass
class ListLiteral(ASTNode):
    elements: List[ASTNode]

@dataclass
class DictLiteral(ASTNode):
    pairs: List[tuple]  # [(key, value), ...]

@dataclass
class IndexAccess(ASTNode):
    object: ASTNode
    index: ASTNode

@dataclass
class MemberAccess(ASTNode):
    object: ASTNode
    member: str

@dataclass
class ClassDeclaration(ASTNode):
    name: str
    methods: List[ASTNode]
    attributes: List[ASTNode]

@dataclass
class ImportStatement(ASTNode):
    module: str
    items: Optional[List[str]] = None

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
        elif token.type == TokenType.CLASS:
            return self.parse_class_declaration()
        elif token.type == TokenType.IMPORT:
            return self.parse_import_statement()
        elif token.type == TokenType.RETURN:
            return self.parse_return_statement()
        elif token.type == TokenType.IDENTIFIER:
            # 함수 호출 또는 할당
            if self.peek_token().type == TokenType.LPAREN:
                return self.parse_function_call()
            elif self.peek_token().type == TokenType.ASSIGN:
                return self.parse_assignment()
            elif self.peek_token().type == TokenType.LBRACKET:
                # 리스트 인덱스 할당
                return self.parse_index_assignment()
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
        
        # then 블록 파싱 - column 기반 들여쓰기
        then_block = []
        base_column = None
        
        while self.current_token().type not in [TokenType.ELSE, TokenType.EOF]:
            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                continue
            
            # 첫 문장의 column 저장
            if base_column is None:
                base_column = self.current_token().column
            
            # ELSE 키워드 체크 (같은 레벨)
            if self.current_token().type == TokenType.ELSE:
                break
            
            # 현재 토큰의 column이 base_column보다 작으면 블록 종료
            if self.current_token().column < base_column:
                break
            
            stmt = self.parse_statement()
            if stmt:
                then_block.append(stmt)
        
        # else 블록 파싱
        else_block = None
        if self.current_token().type == TokenType.ELSE:
            self.expect(TokenType.ELSE)
            self.expect(TokenType.COLON)
            self.skip_newlines()
            
            else_block = []
            base_column = None
            
            while self.current_token().type != TokenType.EOF:
                if self.current_token().type == TokenType.NEWLINE:
                    self.advance()
                    continue
                
                # 첫 문장의 column 저장
                if base_column is None:
                    base_column = self.current_token().column
                
                # 현재 토큰의 column이 base_column보다 작으면 블록 종료
                if self.current_token().column < base_column:
                    break
                
                stmt = self.parse_statement()
                if stmt:
                    else_block.append(stmt)
        
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
        
        # 블록 파싱 - 첫 문장의 column을 기준으로 들여쓰기 판단
        body = []
        base_column = None
        
        while self.current_token().type != TokenType.EOF:
            # 빈 줄 건너뛰기
            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                continue
            
            # 첫 문장의 column 저장
            if base_column is None:
                base_column = self.current_token().column
            
            # 현재 토큰의 column이 base_column보다 작으면 블록 종료
            if self.current_token().column < base_column:
                break
            
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
        
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
        # Track if we've seen at least one statement
        seen_statement = False
        
        while self.current_token().type != TokenType.EOF:
            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                # After seeing at least one statement, break on top-level declarations
                if seen_statement and self.current_token().type in [TokenType.VAR, TokenType.FUNC, TokenType.CLASS]:
                    break
                continue
            stmt = self.parse_statement()
            if stmt:
                body.append(stmt)
                seen_statement = True
                # Stop after return statement
                if isinstance(stmt, ReturnStatement):
                    break
            # Break on new function/class declarations
            if self.current_token().type in [TokenType.FUNC, TokenType.CLASS, TokenType.EOF]:
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
    
    def parse_class_declaration(self) -> ClassDeclaration:
        self.expect(TokenType.CLASS)
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.COLON)
        self.skip_newlines()
        
        methods = []
        attributes = []
        
        while self.current_token().type != TokenType.EOF:
            if self.current_token().type == TokenType.NEWLINE:
                self.advance()
                if self.current_token().type in [TokenType.VAR, TokenType.CLASS, TokenType.FUNC]:
                    break
                continue
            
            if self.current_token().type == TokenType.FUNC:
                methods.append(self.parse_function_declaration())
            elif self.current_token().type == TokenType.VAR:
                attributes.append(self.parse_var_declaration())
            else:
                break
        
        return ClassDeclaration(name, methods, attributes)
    
    def parse_import_statement(self) -> ImportStatement:
        self.expect(TokenType.IMPORT)
        module = self.expect(TokenType.IDENTIFIER).value
        
        items = None
        if self.current_token().type == TokenType.FROM:
            self.advance()
            items = []
            items.append(self.expect(TokenType.IDENTIFIER).value)
            while self.current_token().type == TokenType.COMMA:
                self.advance()
                items.append(self.expect(TokenType.IDENTIFIER).value)
        
        self.skip_newlines()
        return ImportStatement(module, items)
    
    def parse_index_assignment(self) -> Assignment:
        name = self.expect(TokenType.IDENTIFIER).value
        self.expect(TokenType.LBRACKET)
        index = self.parse_expression()
        self.expect(TokenType.RBRACKET)
        self.expect(TokenType.ASSIGN)
        value = self.parse_expression()
        self.skip_newlines()
        # Return as special assignment with index
        return Assignment(f"{name}[{index}]", value)
    
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
        elif token.type == TokenType.LBRACKET:
            return self.parse_list_literal()
        elif token.type == TokenType.LBRACE:
            return self.parse_dict_literal()
        elif token.type == TokenType.IDENTIFIER:
            name = token.value
            self.advance()
            
            # 함수 호출
            if self.current_token().type == TokenType.LPAREN:
                self.pos -= 1  # 백트랙
                result = self.parse_function_call()
            else:
                result = Identifier(name)
            
            # 체이닝된 인덱스/멤버 접근 처리
            while self.current_token().type in [TokenType.LBRACKET, TokenType.DOT]:
                if self.current_token().type == TokenType.LBRACKET:
                    self.advance()
                    index = self.parse_expression()
                    self.expect(TokenType.RBRACKET)
                    result = IndexAccess(result, index)
                elif self.current_token().type == TokenType.DOT:
                    self.advance()
                    member = self.expect(TokenType.IDENTIFIER).value
                    result = MemberAccess(result, member)
            
            return result
        elif token.type == TokenType.LPAREN:
            self.advance()
            expr = self.parse_expression()
            self.expect(TokenType.RPAREN)
            return expr
        
        raise SyntaxError(f"Unexpected token {token.type} at line {token.line}")
    
    def parse_list_literal(self) -> ListLiteral:
        self.expect(TokenType.LBRACKET)
        self.skip_newlines()  # Skip newlines after opening bracket
        elements = []
        
        if self.current_token().type != TokenType.RBRACKET:
            elements.append(self.parse_expression())
            self.skip_newlines()  # Skip newlines after element
            
            while self.current_token().type == TokenType.COMMA:
                self.advance()
                self.skip_newlines()  # Skip newlines after comma
                if self.current_token().type == TokenType.RBRACKET:
                    break
                elements.append(self.parse_expression())
                self.skip_newlines()  # Skip newlines after element
        
        self.expect(TokenType.RBRACKET)
        return ListLiteral(elements)
    
    def parse_dict_literal(self) -> DictLiteral:
        self.expect(TokenType.LBRACE)
        self.skip_newlines()  # Skip newlines after opening brace
        pairs = []
        
        if self.current_token().type != TokenType.RBRACE:
            key = self.parse_expression()
            self.skip_newlines()  # Skip newlines after key
            self.expect(TokenType.COLON)
            self.skip_newlines()  # Skip newlines after colon
            value = self.parse_expression()
            self.skip_newlines()  # Skip newlines after value
            pairs.append((key, value))
            
            while self.current_token().type == TokenType.COMMA:
                self.advance()
                self.skip_newlines()  # Skip newlines after comma
                if self.current_token().type == TokenType.RBRACE:
                    break
                key = self.parse_expression()
                self.skip_newlines()  # Skip newlines after key
                self.expect(TokenType.COLON)
                self.skip_newlines()  # Skip newlines after colon
                value = self.parse_expression()
                self.skip_newlines()  # Skip newlines after value
                pairs.append((key, value))
        
        self.expect(TokenType.RBRACE)
        return DictLiteral(pairs)
