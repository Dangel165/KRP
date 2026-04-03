"""
한국어 프로그래밍 언어 - 인터프리터
IDE에서 빠른 실행을 위한 간단한 인터프리터
"""

from compiler.parser import *

class Interpreter:
    def __init__(self):
        self.variables = {}
        self.functions = {}
    
    def execute(self, program: Program):
        for statement in program.statements:
            self.execute_statement(statement)
    
    def execute_statement(self, node: ASTNode):
        if isinstance(node, VarDeclaration):
            value = self.evaluate_expression(node.value)
            self.variables[node.name] = value
            return None
        
        elif isinstance(node, Assignment):
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
            while self.evaluate_expression(node.condition):
                for stmt in node.body:
                    result = self.execute_statement(stmt)
                    if isinstance(stmt, ReturnStatement):
                        return result
            return None
        
        elif isinstance(node, FunctionDeclaration):
            self.functions[node.name] = node
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
        if call.name not in self.functions:
            raise NameError(f"함수 '{call.name}'이(가) 정의되지 않았습니다")
        
        func = self.functions[call.name]
        
        # 매개변수 바인딩
        old_vars = self.variables.copy()
        for i, param in enumerate(func.parameters):
            if i < len(call.arguments):
                value = self.evaluate_expression(call.arguments[i])
                self.variables[param] = value
        
        # 함수 본문 실행
        result = None
        for stmt in func.body:
            result = self.execute_statement(stmt)
            if isinstance(stmt, ReturnStatement):
                break
        
        # 변수 복원
        self.variables = old_vars
        
        return result
