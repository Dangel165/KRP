"""
한국어 프로그래밍 언어 - 인터프리터
IDE에서 빠른 실행을 위한 간단한 인터프리터
"""

from compiler.parser import *

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
        self.classes = {}
        self.modules = {}
        self._setup_stdlib()
    
    def execute(self, program: Program):
        for statement in program.statements:
            self.execute_statement(statement)
    
    def execute_statement(self, node: ASTNode):
        if isinstance(node, VarDeclaration):
            value = self.evaluate_expression(node.value)
            # 반복문 안에서는 변수가 이미 존재하면 재할당으로 처리
            self.variables[node.name] = value
            return None
        
        elif isinstance(node, Assignment):
            # 리스트 인덱스 할당 처리
            if '[' in node.name and ']' in node.name:
                var_name = node.name.split('[')[0]
                index_str = node.name.split('[')[1].split(']')[0]
                try:
                    index = int(index_str)
                except:
                    index = self.variables.get(index_str, 0)
                value = self.evaluate_expression(node.value)
                if var_name in self.variables:
                    self.variables[var_name][index] = value
            else:
                value = self.evaluate_expression(node.value)
                self.variables[node.name] = value
            return None
        
        elif isinstance(node, PrintStatement):
            value = self.evaluate_expression(node.expression)
            print(value)
            return None
        
        elif isinstance(node, IfStatement):
            condition = self.evaluate_expression(node.condition)
            if condition:
                for stmt in node.then_block:
                    result = self.execute_statement(stmt)
                    if isinstance(stmt, ReturnStatement):
                        return result
            elif node.else_block:
                for stmt in node.else_block:
                    result = self.execute_statement(stmt)
                    if isinstance(stmt, ReturnStatement):
                        return result
            return None
        
        elif isinstance(node, WhileStatement):
            max_iterations = 100000  # 안전 장치
            iteration_count = 0
            while self.evaluate_expression(node.condition):
                iteration_count += 1
                if iteration_count > max_iterations:
                    raise RuntimeError(f"반복문이 {max_iterations}회를 초과했습니다. 무한 루프일 수 있습니다.")
                
                for stmt in node.body:
                    result = self.execute_statement(stmt)
                    if isinstance(stmt, ReturnStatement):
                        return result
            return None
        
        elif isinstance(node, FunctionDeclaration):
            self.functions[node.name] = node
            return None
        
        elif isinstance(node, ClassDeclaration):
            self.classes[node.name] = node
            return None
        
        elif isinstance(node, ImportStatement):
            self._import_module(node)
            return None
        
        elif isinstance(node, FunctionCall):
            return self.call_function(node)
        
        elif isinstance(node, ReturnStatement):
            return self.evaluate_expression(node.value)
        
        return None
    
    def evaluate_expression(self, node: ASTNode):
        if isinstance(node, Number):
            return node.value
        
        elif isinstance(node, String):
            return node.value
        
        elif isinstance(node, Boolean):
            return node.value
        
        elif isinstance(node, ListLiteral):
            return [self.evaluate_expression(elem) for elem in node.elements]
        
        elif isinstance(node, DictLiteral):
            result = {}
            for key_node, value_node in node.pairs:
                key = self.evaluate_expression(key_node)
                value = self.evaluate_expression(value_node)
                result[key] = value
            return result
        
        elif isinstance(node, IndexAccess):
            obj = self.evaluate_expression(node.object)
            index = self.evaluate_expression(node.index)
            return obj[index]
        
        elif isinstance(node, MemberAccess):
            obj = self.evaluate_expression(node.object)
            # 리스트/딕셔너리 메서드 지원
            if isinstance(obj, list):
                return self._get_list_method(obj, node.member)
            elif isinstance(obj, dict):
                return self._get_dict_method(obj, node.member)
            return None
        
        elif isinstance(node, Identifier):
            if node.name in self.variables:
                return self.variables[node.name]
            raise NameError(f"변수 '{node.name}'이(가) 정의되지 않았습니다")
        
        elif isinstance(node, BinaryOp):
            left = self.evaluate_expression(node.left)
            right = self.evaluate_expression(node.right)
            
            if node.op == '+':
                return left + right
            elif node.op == '-':
                return left - right
            elif node.op == '*':
                return left * right
            elif node.op == '/':
                return left / right
            elif node.op == '==':
                return left == right
            elif node.op == '!=':
                return left != right
            elif node.op == '>':
                return left > right
            elif node.op == '<':
                return left < right
            elif node.op == '>=':
                return left >= right
            elif node.op == '<=':
                return left <= right
        
        elif isinstance(node, FunctionCall):
            return self.call_function(node)
        
        return None
    
    def call_function(self, call: FunctionCall):
        # 표준 라이브러리 함수 체크
        if call.name in self.functions and callable(self.functions[call.name]) and not isinstance(self.functions[call.name], FunctionDeclaration):
            args = [self.evaluate_expression(arg) for arg in call.arguments]
            return self.functions[call.name](*args)
        
        if call.name not in self.functions:
            raise NameError(f"함수 '{call.name}'이(가) 정의되지 않았습니다")
        
        func = self.functions[call.name]
        
        # 인자 평가 (현재 스코프에서)
        arg_values = [self.evaluate_expression(arg) for arg in call.arguments]
        
        # 새로운 스코프 생성 (기존 변수 복사)
        old_vars = self.variables.copy()
        
        # 매개변수 바인딩
        for i, param in enumerate(func.parameters):
            if i < len(arg_values):
                self.variables[param] = arg_values[i]
        
        # 함수 본문 실행
        result = None
        for stmt in func.body:
            result = self.execute_statement(stmt)
            if isinstance(stmt, ReturnStatement):
                break
        
        # 변수 복원
        self.variables = old_vars
        
        return result
    
    def _setup_stdlib(self):
        """표준 라이브러리 함수 설정"""
        import math
        import random
        import time
        
        # 수학 함수
        self.functions['제곱근'] = lambda x: math.sqrt(x)
        self.functions['절댓값'] = lambda x: abs(x)
        self.functions['올림'] = lambda x: math.ceil(x)
        self.functions['내림'] = lambda x: math.floor(x)
        self.functions['반올림'] = lambda x: round(x)
        self.functions['최댓값'] = lambda *args: max(args)
        self.functions['최솟값'] = lambda *args: min(args)
        self.functions['거듭제곱'] = lambda x, y: x ** y
        
        # 문자열 함수
        self.functions['길이'] = lambda x: len(x)
        self.functions['대문자'] = lambda s: s.upper()
        self.functions['소문자'] = lambda s: s.lower()
        self.functions['분리'] = lambda s, sep=' ': s.split(sep)
        self.functions['합치기'] = lambda lst, sep='': sep.join(str(x) for x in lst)
        
        # 리스트 함수
        self.functions['추가'] = lambda lst, item: lst.append(item) or lst
        self.functions['제거'] = lambda lst, item: lst.remove(item) or lst
        self.functions['정렬'] = lambda lst: sorted(lst)
        self.functions['뒤집기'] = lambda lst: list(reversed(lst))
        
        # 랜덤 함수
        self.functions['난수'] = lambda: random.random()
        self.functions['정수난수'] = lambda a, b: random.randint(a, b)
        self.functions['선택'] = lambda lst: random.choice(lst)
        
        # 입출력 함수
        self.functions['입력'] = lambda prompt='': input(prompt)
        self.functions['정수변환'] = lambda x: int(x)
        self.functions['실수변환'] = lambda x: float(x)
        self.functions['문자변환'] = lambda x: str(x)
        
        # 시간 함수
        self.functions['현재시간'] = lambda: time.time()
        self.functions['대기'] = lambda sec: time.sleep(sec)
    
    def _get_list_method(self, lst, method_name):
        """리스트 메서드 반환"""
        if method_name == '추가':
            return lambda item: lst.append(item)
        elif method_name == '제거':
            return lambda item: lst.remove(item)
        elif method_name == '길이':
            return len(lst)
        elif method_name == '정렬':
            return lambda: lst.sort()
        elif method_name == '뒤집기':
            return lambda: lst.reverse()
        elif method_name == '복사':
            return lambda: lst.copy()
        return None
    
    def _get_dict_method(self, dct, method_name):
        """딕셔너리 메서드 반환"""
        if method_name == '키목록':
            return list(dct.keys())
        elif method_name == '값목록':
            return list(dct.values())
        elif method_name == '항목목록':
            return list(dct.items())
        elif method_name == '가져오기':
            return lambda key, default=None: dct.get(key, default)
        return None
    
    def _import_module(self, node: ImportStatement):
        """모듈 가져오기"""
        # 표준 라이브러리 모듈
        if node.module == '수학':
            import math
            self.modules['수학'] = math
            if node.items:
                for item in node.items:
                    if hasattr(math, item):
                        self.variables[item] = getattr(math, item)
        elif node.module == '랜덤':
            import random
            self.modules['랜덤'] = random
            if node.items:
                for item in node.items:
                    if hasattr(random, item):
                        self.variables[item] = getattr(random, item)
        elif node.module == '시간':
            import time
            self.modules['시간'] = time
            if node.items:
                for item in node.items:
                    if hasattr(time, item):
                        self.variables[item] = getattr(time, item)
