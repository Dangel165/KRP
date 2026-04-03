"""
렉서 테스트
"""

import sys
sys.path.insert(0, '..')

from compiler.lexer import Lexer, TokenType

def test_basic_tokens():
    source = "변수 이름 = 10"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.VAR
    assert tokens[1].type == TokenType.IDENTIFIER
    assert tokens[1].value == "이름"
    assert tokens[2].type == TokenType.ASSIGN
    assert tokens[3].type == TokenType.NUMBER
    assert tokens[3].value == 10

def test_string():
    source = '변수 메시지 = "안녕하세요"'
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert tokens[3].type == TokenType.STRING
    assert tokens[3].value == "안녕하세요"

def test_operators():
    source = "10 + 20 * 30"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.NUMBER
    assert tokens[1].type == TokenType.PLUS
    assert tokens[2].type == TokenType.NUMBER
    assert tokens[3].type == TokenType.MULTIPLY
    assert tokens[4].type == TokenType.NUMBER

def test_comparison():
    source = "a == b"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert tokens[1].type == TokenType.EQ

def test_keywords():
    source = "만약 아니면 반복 함수"
    lexer = Lexer(source)
    tokens = lexer.tokenize()
    
    assert tokens[0].type == TokenType.IF
    assert tokens[1].type == TokenType.ELSE
    assert tokens[2].type == TokenType.WHILE
    assert tokens[3].type == TokenType.FUNC

if __name__ == '__main__':
    test_basic_tokens()
    test_string()
    test_operators()
    test_comparison()
    test_keywords()
    print("✓ 모든 렉서 테스트 통과!")
