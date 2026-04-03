# KRP (Korean Programming Language)

파이썬으로 만든 쉽고 한국어로 작성할 수 있는 프로그래밍 언어입니다.

## 특징

- 🇰🇷 **한국어 키워드**: 변수, 함수, 만약, 반복 등 모든 키워드가 한국어
- 🚀 **LLVM 백엔드**: 고성능 네이티브 코드 생성
- 📝 **간단한 문법**: 파이썬과 유사한 직관적인 문법
- 🔧 **ANTLR 파서**: 강력한 파서 생성기 사용

## 설치

### pip로 설치 (권장)

```bash
pip install krp
```

### 소스에서 설치

```bash
# 저장소 클론
git clone https://github.com/yourusername/krp.git
cd krp

# 의존성 설치
pip install -r requirements.txt

# 패키지 설치
pip install -e .
```

## 사용법

### GUI IDE (추천)

```bash
# 설치 후
krp-ide

# 또는 소스에서
python ide.py
```

Python IDLE 스타일의 통합 개발 환경:
- 문법 하이라이팅
- 코드 에디터
- 즉시 실행 (F5)
- 컴파일 (F6)
- 예제 코드 포함

### 파일 컴파일 (CLI)

```bash
# 기본 컴파일
krp examples/hello.한글

# 출력 파일 지정
krp examples/hello.한글 -o hello.o

# LLVM IR 확인
krp examples/hello.한글 --show-ir

# 실행 파일 생성
gcc hello.o -o hello
./hello
```

### 대화형 모드 (REPL)

```bash
krp --repl
```

## 문법 예제

### 변수 선언

```korean
변수 이름 = "홍길동"
변수 나이 = 25
변수 키 = 175.5
```

### 출력

```korean
보여줘("안녕하세요!")
보여줘(나이)
```

### 조건문

```korean
만약 (나이 >= 18):
    보여줘("성인입니다")
아니면:
    보여줘("미성년자입니다")
```

### 반복문

```korean
변수 i = 0
반복 (i < 10):
    보여줘(i)
    i = i + 1
```

### 함수

```korean
함수 더하기(a, b):
    변수 결과 = a + b
    반환 결과

변수 합계 = 더하기(10, 20)
보여줘(합계)
```

### 재귀 함수

```korean
함수 팩토리얼(n):
    만약 (n <= 1):
        반환 1
    아니면:
        반환 n * 팩토리얼(n - 1)

보여줘(팩토리얼(5))
```

## 키워드

| 한국어 | 설명 |
|--------|------|
| 변수 | 변수 선언 |
| 함수 | 함수 정의 |
| 만약 | if 조건문 |
| 아니면 | else |
| 반복 | while 반복문 |
| 반환 | return |
| 보여줘 | print 출력 |
| 참 | true |
| 거짓 | false |

## 연산자

### 산술 연산자
- `+` : 덧셈
- `-` : 뺄셈
- `*` : 곱셈
- `/` : 나눗셈

### 비교 연산자
- `==` : 같음
- `!=` : 다름
- `>` : 크다
- `<` : 작다
- `>=` : 크거나 같다
- `<=` : 작거나 같다

## 프로젝트 구조

```
krp/
├── compiler/           # 컴파일러 코어
│   ├── lexer.py       # 렉서 (토큰화)
│   ├── parser.py      # 파서 (AST 생성)
│   ├── interpreter.py # 인터프리터
│   └── codegen.py     # 코드 생성 (LLVM IR)
├── grammar/           # ANTLR 문법 정의
│   └── Korean.g4      # 언어 문법
├── examples/          # 예제 코드
│   ├── hello.한글
│   ├── fibonacci.한글
│   ├── loop.한글
│   └── conditional.한글
├── main.py            # CLI 실행 파일
├── ide.py             # GUI IDE
├── requirements.txt   # 의존성
└── README.md          # 문서
```

## 개발 로드맵

- [x] 기본 문법 설계
- [x] 렉서 구현
- [x] 파서 구현
- [x] 인터프리터 구현
- [x] LLVM IR 코드 생성
- [x] GUI IDE
- [x] pip 패키지 배포
- [ ] 표준 라이브러리
- [ ] 배열/리스트 지원
- [ ] 클래스/객체 지원
- [ ] 모듈 시스템
- [ ] 패키지 관리자

## 기술 스택

- **구현 언어**: Python 3.8+
- **파서 생성기**: ANTLR4
- **백엔드**: LLVM (선택사항)
- **GUI**: tkinter
- **최적화**: LLVM Optimization Passes
