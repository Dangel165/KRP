"""
한국어 프로그래밍 언어 - 렉서 (Lexer)
토큰화 및 어휘 분석
"""

import re
from enum import Enum, auto
from dataclasses import dataclass
from typing import List, Optional

class TokenType(Enum):
    # 키워드
    VAR = auto()          # 변수
    FUNC = auto()         # 함수
    IF = auto()           # 만약
    ELSE = auto()         # 아니면
    WHILE = auto()        # 반복
    FOR = auto()          # 반복
    RETURN = auto()       # 반환
    PRINT = auto()        # 보여줘
    
    # 리터럴
    NUMBER = auto()
    STRING = auto()
    BOOLEAN = auto()
    IDENTIFIER = auto()
    
    # 연산자
    PLUS = auto()         # +
    MINUS = auto()        # -
    MULTIPLY = auto()     # *
    DIVIDE = auto()       # /
    ASSIGN = auto()       # =
    
    # 비교 연산자
    EQ = auto()           # ==
    NE = auto()           # !=
    GT = auto()           # >
    LT = auto()           # <
    GE = auto()           # >=
    LE = auto()           # <=
    
    # 구분자
    LPAREN = auto()       # (
    RPAREN = auto()       # )
    COMMA = auto()        # ,
    COLON = auto()        # :
    NEWLINE = auto()
    INDENT = auto()
    DEDENT = auto()
    EOF = auto()

@dataclass
class Token:
    type: TokenType
    value: any
    line: int
    column: int

class Lexer:
    def __init__(self, source: str):
        self.source = source
        self.pos = 0
        self.line = 1
        self.column = 1
        self.tokens: List[Token] = []
        self.indent_stack = [0]
        
        # 한국어 키워드 매핑
        self.keywords = {
            '변수': TokenType.VAR,
            '함수': TokenType.FUNC,
            '만약': TokenType.IF,
            '아니면': TokenType.ELSE,
            '반복': TokenType.WHILE,
            '반환': TokenType.RETURN,
            '보여줘': TokenType.PRINT,
            '참': TokenType.BOOLEAN,
            '거짓': TokenType.BOOLEAN,
        }
    
    def current_char(self) -> Optional[str]:
        if self.pos >= len(self.source):
            return None
        return self.source[self.pos]
    
    def peek_char(self, offset=1) -> Optional[str]:
        pos = self.pos + offset
        if pos >= len(self.source):
            return None
        return self.source[pos]
    
    def advance(self):
        if self.pos < len(self.source):
            if self.source[self.pos] == '\n':
                self.line += 1
                self.column = 1
            else:
                self.column += 1
            self.pos += 1
    
    def skip_whitespace(self):
        while self.current_char() and self.current_char() in ' \t':
            self.advance()
    
    def skip_comment(self):
        if self.current_char() == '#':
            while self.current_char() and self.current_char() != '\n':
                self.advance()
    
    def read_number(self) -> Token:
        start_line = self.line
        start_col = self.column
        num_str = ''
        
        while self.current_char() and (self.current_char().isdigit() or self.current_char() == '.'):
            num_str += self.current_char()
            self.advance()
        
        value = float(num_str) if '.' in num_str else int(num_str)
        return Token(TokenType.NUMBER, value, start_line, start_col)
    
    def read_string(self) -> Token:
        start_line = self.line
        start_col = self.column
        quote = self.current_char()
        self.advance()  # Skip opening quote
        
        string_val = ''
        while self.current_char() and self.current_char() != quote:
            string_val += self.current_char()
            self.advance()
        
        if self.current_char() == quote:
            self.advance()  # Skip closing quote
        
        return Token(TokenType.STRING, string_val, start_line, start_col)
    
    def read_identifier(self) -> Token:
        start_line = self.line
        start_col = self.column
        ident = ''
        
        while self.current_char() and (self.current_char().isalnum() or 
                                       self.current_char() == '_' or
                                       '가' <= self.current_char() <= '힣'):
            ident += self.current_char()
            self.advance()
        
        # 키워드 체크
        token_type = self.keywords.get(ident, TokenType.IDENTIFIER)
        value = ident if token_type == TokenType.IDENTIFIER else ident
        
        if token_type == TokenType.BOOLEAN:
            value = True if ident == '참' else False
        
        return Token(token_type, value, start_line, start_col)
    
    def tokenize(self) -> List[Token]:
        while self.pos < len(self.source):
            self.skip_whitespace()
            
            if not self.current_char():
                break
            
            # 주석 처리
            if self.current_char() == '#':
                self.skip_comment()
                continue
            
            # 개행
            if self.current_char() == '\n':
                token = Token(TokenType.NEWLINE, '\n', self.line, self.column)
                self.tokens.append(token)
                self.advance()
                continue
            
            # 숫자
            if self.current_char().isdigit():
                self.tokens.append(self.read_number())
                continue
            
            # 문자열
            if self.current_char() in '"\'':
                self.tokens.append(self.read_string())
                continue
            
            # 식별자 및 키워드
            if self.current_char().isalpha() or '가' <= self.current_char() <= '힣' or self.current_char() == '_':
                self.tokens.append(self.read_identifier())
                continue
            
            # 연산자 및 구분자
            char = self.current_char()
            line, col = self.line, self.column
            
            if char == '+':
                self.tokens.append(Token(TokenType.PLUS, '+', line, col))
                self.advance()
            elif char == '-':
                self.tokens.append(Token(TokenType.MINUS, '-', line, col))
                self.advance()
            elif char == '*':
                self.tokens.append(Token(TokenType.MULTIPLY, '*', line, col))
                self.advance()
            elif char == '/':
                self.tokens.append(Token(TokenType.DIVIDE, '/', line, col))
                self.advance()
            elif char == '=':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.EQ, '==', line, col))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.ASSIGN, '=', line, col))
                    self.advance()
            elif char == '!':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.NE, '!=', line, col))
                    self.advance()
                    self.advance()
            elif char == '>':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.GE, '>=', line, col))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.GT, '>', line, col))
                    self.advance()
            elif char == '<':
                if self.peek_char() == '=':
                    self.tokens.append(Token(TokenType.LE, '<=', line, col))
                    self.advance()
                    self.advance()
                else:
                    self.tokens.append(Token(TokenType.LT, '<', line, col))
                    self.advance()
            elif char == '(':
                self.tokens.append(Token(TokenType.LPAREN, '(', line, col))
                self.advance()
            elif char == ')':
                self.tokens.append(Token(TokenType.RPAREN, ')', line, col))
                self.advance()
            elif char == ',':
                self.tokens.append(Token(TokenType.COMMA, ',', line, col))
                self.advance()
            elif char == ':':
                self.tokens.append(Token(TokenType.COLON, ':', line, col))
                self.advance()
            else:
                self.advance()
        
        self.tokens.append(Token(TokenType.EOF, None, self.line, self.column))
        return self.tokens
