// ANTLR4 문법 정의 - 한국어 프로그래밍 언어
grammar Korean;

// 파서 규칙
program
    : statement* EOF
    ;

statement
    : variableDeclaration
    | assignment
    | printStatement
    | ifStatement
    | whileStatement
    | forStatement
    | functionDeclaration
    | functionCall
    | returnStatement
    | NEWLINE
    ;

variableDeclaration
    : '변수' IDENTIFIER '=' expression NEWLINE
    ;

assignment
    : IDENTIFIER '=' expression NEWLINE
    ;

printStatement
    : '보여줘' '(' expression ')' NEWLINE
    ;

ifStatement
    : '만약' '(' condition ')' ':' NEWLINE
      INDENT statement+ DEDENT
      ('아니면' ':' NEWLINE INDENT statement+ DEDENT)?
    ;

whileStatement
    : '반복' '(' condition ')' ':' NEWLINE
      INDENT statement+ DEDENT
    ;

forStatement
    : '반복' IDENTIFIER '를' expression '부터' expression '까지' ':' NEWLINE
      INDENT statement+ DEDENT
    ;

functionDeclaration
    : '함수' IDENTIFIER '(' parameterList? ')' ':' NEWLINE
      INDENT statement+ DEDENT
    ;

functionCall
    : IDENTIFIER '(' argumentList? ')' NEWLINE
    ;

returnStatement
    : '반환' expression NEWLINE
    ;

parameterList
    : IDENTIFIER (',' IDENTIFIER)*
    ;

argumentList
    : expression (',' expression)*
    ;

condition
    : expression comparisonOp expression
    | expression
    ;

comparisonOp
    : '==' | '!=' | '>' | '<' | '>=' | '<='
    | '이면' | '아니면' | '보다크면' | '보다작으면'
    ;

expression
    : expression ('*' | '/') expression     # MulDiv
    | expression ('+' | '-') expression     # AddSub
    | '(' expression ')'                    # Parens
    | functionCall                          # FuncCall
    | IDENTIFIER                            # Variable
    | NUMBER                                # Number
    | STRING                                # String
    | BOOLEAN                               # Bool
    ;

// 렉서 규칙
BOOLEAN
    : '참' | '거짓'
    ;

NUMBER
    : [0-9]+ ('.' [0-9]+)?
    ;

STRING
    : '"' (~["\r\n])* '"'
    | '\'' (~['\r\n])* '\''
    ;

IDENTIFIER
    : [가-힣a-zA-Z_][가-힣a-zA-Z0-9_]*
    ;

NEWLINE
    : '\r'? '\n'
    ;

INDENT
    : '    '
    ;

DEDENT
    : // 파이썬 스타일 들여쓰기 처리
    ;

WS
    : [ \t]+ -> skip
    ;

COMMENT
    : '#' ~[\r\n]* -> skip
    ;
