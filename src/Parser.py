from enum import Enum
from ParsingTable import ParserTokenType

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self, offset=0):
        if self.pos + offset < len(self.tokens):
            return self.tokens[self.pos + offset]
        return self.tokens[-1]  # EOF

    def match(self, *types):
        if not self.is_at_end() and self.peek().type in types:
            self.pos += 1
            return True
        return False

    def consume(self, type_, message):
        if self.peek().type != type_:
            raise SyntaxError(f"{message}. Got: {self.peek().value}")
        self.pos += 1
        return self.tokens[self.pos - 1]

    def is_at_end(self):
        return self.pos >= len(self.tokens)

    def parse(self):
        declarations = []
        while not self.is_at_end():
            declarations.append(self.parse_declaration())
        return declarations

    def parse_declaration(self):
        # Parse modifiers first
        modifiers = self.parse_modifiers()
        
        if self.match(ParserTokenType.CLASS):
            return self.parse_class(modifiers)
        elif self.match(ParserTokenType.INTERFACE):
            return self.parse_interface(modifiers)
        elif self.match(ParserTokenType.FUNCTION):
            return self.parse_function(modifiers)
        elif self.match(ParserTokenType.LET):
            return self.parse_variable(modifiers)
        elif self.match(ParserTokenType.IMPORT):
            return self.parse_import()
        elif self.match(ParserTokenType.FROM):
            return self.parse_from_import()
        elif self.match(ParserTokenType.NAMESPACE):
            return self.parse_namespace()
        elif modifiers and self.peek().type == ParserTokenType.IDENTIFIER:
            # This might be a constructor: public ClassName(...)
            return self.parse_constructor(modifiers)
        else:
            # If we have modifiers but no declaration keyword, it's an error
            if modifiers:
                raise SyntaxError(f"Expected declaration after modifiers, got {self.peek().type}")
            return self.parse_statement()

    def parse_constructor(self, modifiers):
        """Parse constructor declarations: public ClassName(...) [: super(...)] { ... }"""
        name = self.consume(ParserTokenType.IDENTIFIER, "Expected constructor name")
        self.consume(ParserTokenType.LPAREN, "Expected '('")
        params = []
        if not self.match(ParserTokenType.RPAREN):
            while True:
                param_name = self.consume(ParserTokenType.IDENTIFIER, "Expected parameter name")
                param_type = None
                # Handle type annotation: param: type
                if self.match(ParserTokenType.COLON):
                    param_type = self.parse_type_annotation()
                
                params.append({"name": param_name.value, "type": param_type})
                if self.match(ParserTokenType.RPAREN): 
                    break
                self.consume(ParserTokenType.COMMA, "Expected ',' or ')' in parameter list")
        
        # Handle optional super call: : super(args)
        super_call = None
        if self.match(ParserTokenType.COLON):
            self.consume(ParserTokenType.SUPER, "Expected 'super'")
            self.consume(ParserTokenType.LPAREN, "Expected '('")
            super_args = []
            if not self.match(ParserTokenType.RPAREN):
                while True:
                    super_args.append(self.parse_expression())
                    if self.match(ParserTokenType.RPAREN):
                        break
                    self.consume(ParserTokenType.COMMA, "Expected ',' or ')' in super arguments")
            super_call = {"args": super_args}
        
        body = self.parse_block()
        return {"type": "constructor", "name": name.value, "params": params, "modifiers": modifiers, "super": super_call, "body": body}

    def parse_modifiers(self):
        """Parse access modifiers and other modifiers"""
        modifiers = []
        while self.peek().type in [ParserTokenType.PUBLIC, ParserTokenType.PRIVATE, ParserTokenType.PROTECTED, 
                                   ParserTokenType.STATIC, ParserTokenType.ABSTRACT, ParserTokenType.FINAL, 
                                   ParserTokenType.OVERRIDE]:
            modifier = self.tokens[self.pos]
            self.pos += 1
            modifiers.append(modifier.value)
        return modifiers

    def parse_class(self, modifiers=None):
        if modifiers is None:
            modifiers = []
        name = self.consume(ParserTokenType.IDENTIFIER, "Expected class name")
        
        # Handle inheritance: class Derived : Base1, Base2, Base3 OR class Derived extends Base
        base_classes = []
        if self.match(ParserTokenType.COLON):
            base_classes.append(self.consume(ParserTokenType.IDENTIFIER, "Expected base class name").value)
            while self.match(ParserTokenType.COMMA):
                base_classes.append(self.consume(ParserTokenType.IDENTIFIER, "Expected base class name").value)
        elif self.match(ParserTokenType.EXTENDS):
            # Handle qualified base class names like "Examples.Shape"
            base_name = self.consume(ParserTokenType.IDENTIFIER, "Expected base class name").value
            while self.match(ParserTokenType.DOT):
                part = self.consume(ParserTokenType.IDENTIFIER, "Expected identifier after '.'").value
                base_name += "." + part
            base_classes.append(base_name)
        
        self.consume(ParserTokenType.LBRACE, "Expected '{' after class name")
        members = []
        while not self.match(ParserTokenType.RBRACE):
            members.append(self.parse_declaration())
        return {"type": "class", "name": name.value, "base": base_classes, "modifiers": modifiers, "members": members}

    def parse_interface(self, modifiers=None):
        """Parse interface declarations: [modifiers] interface Name { ... }"""
        if modifiers is None:
            modifiers = []
        name = self.consume(ParserTokenType.IDENTIFIER, "Expected interface name")
        
        # Handle inheritance: interface Derived : Base1, Base2
        base_interfaces = []
        if self.match(ParserTokenType.COLON):
            base_interfaces.append(self.consume(ParserTokenType.IDENTIFIER, "Expected base interface name").value)
            while self.match(ParserTokenType.COMMA):
                base_interfaces.append(self.consume(ParserTokenType.IDENTIFIER, "Expected base interface name").value)
        
        self.consume(ParserTokenType.LBRACE, "Expected '{' after interface name")
        members = []
        while not self.match(ParserTokenType.RBRACE):
            members.append(self.parse_interface_member())
        
        return {"type": "interface", "name": name.value, "base": base_interfaces, "modifiers": modifiers, "members": members}

    def parse_interface_member(self):
        """Parse interface member (function signatures only)"""
        # Interface members can only be function signatures
        if self.match(ParserTokenType.FUNCTION):
            name = self.consume(ParserTokenType.IDENTIFIER, "Expected function name")
            self.consume(ParserTokenType.LPAREN, "Expected '('")
            params = []
            if not self.match(ParserTokenType.RPAREN):
                while True:
                    param_name = self.consume(ParserTokenType.IDENTIFIER, "Expected parameter name")
                    param_type = None
                    # Handle type annotation: param: type
                    if self.match(ParserTokenType.COLON):
                        param_type = self.parse_type_annotation()
                    
                    params.append({"name": param_name.value, "type": param_type})
                    if self.match(ParserTokenType.RPAREN): 
                        break
                    self.consume(ParserTokenType.COMMA, "Expected ',' or ')' in parameter list")
            
            return_type = None
            if self.match(ParserTokenType.FUNCTION_ARROW):
                return_type = self.parse_type_annotation()
            
            self.consume(ParserTokenType.SEMICOLON, "Expected ';' after interface function signature")
            return {"type": "interface_function", "name": name.value, "params": params, "return_type": return_type}
        else:
            raise SyntaxError("Interface can only contain function signatures")

    def parse_function(self, modifiers=None):
        if modifiers is None:
            modifiers = []
        name = self.consume(ParserTokenType.IDENTIFIER, "Expected function name")
        self.consume(ParserTokenType.LPAREN, "Expected '('")
        params = []
        if not self.match(ParserTokenType.RPAREN):
            while True:
                param_name = self.consume(ParserTokenType.IDENTIFIER, "Expected parameter name")
                param_type = None
                # Handle type annotation: param: type
                if self.match(ParserTokenType.COLON):
                    param_type = self.parse_type_annotation()
                
                params.append({"name": param_name.value, "type": param_type})
                if self.match(ParserTokenType.RPAREN): 
                    break
                self.consume(ParserTokenType.COMMA, "Expected ',' or ')' in parameter list")
        
        # Handle return type annotation: -> type
        return_type = None
        if self.match(ParserTokenType.FUNCTION_ARROW):
            return_type = self.parse_type_annotation()
        elif self.match(ParserTokenType.COLON):
            # Alternative syntax for return types
            return_type = self.parse_type_annotation()
        
        # Handle abstract functions (no body)
        if "abstract" in modifiers:
            self.consume(ParserTokenType.SEMICOLON, "Expected ';' after abstract function")
            return {"type": "function", "name": name.value, "params": params, "return_type": return_type, "modifiers": modifiers, "body": None}
        else:
            body = self.parse_block()
            return {"type": "function", "name": name.value, "params": params, "return_type": return_type, "modifiers": modifiers, "body": body}

    def parse_type_annotation(self):
        """Parse type annotations, which can be keywords like 'int' or identifiers, optionally followed by '*' for pointers"""
        base_type = None
        token_type = self.peek().type
        if token_type == ParserTokenType.IDENTIFIER:
            base_type = self.consume(ParserTokenType.IDENTIFIER, "Expected type").value
            # Handle qualified type names like Examples.Shape
            while self.match(ParserTokenType.DOT):
                next_part = self.consume(ParserTokenType.IDENTIFIER, "Expected identifier after '.'").value
                base_type = base_type + "." + next_part
        elif token_type == ParserTokenType.INT:
            base_type = self.consume(ParserTokenType.INT, "Expected type").value
        elif token_type == ParserTokenType.FLOAT:
            base_type = self.consume(ParserTokenType.FLOAT, "Expected type").value
        elif token_type == ParserTokenType.DOUBLE:
            base_type = self.consume(ParserTokenType.DOUBLE, "Expected type").value
        elif token_type == ParserTokenType.BOOL:
            base_type = self.consume(ParserTokenType.BOOL, "Expected type").value
        elif token_type == ParserTokenType.VOID:
            base_type = self.consume(ParserTokenType.VOID, "Expected type").value
        elif token_type == ParserTokenType.ANY:
            base_type = self.consume(ParserTokenType.ANY, "Expected type").value
        elif token_type == ParserTokenType.PTR:
            base_type = self.consume(ParserTokenType.PTR, "Expected type").value
        elif token_type == ParserTokenType.STRING:
            base_type = self.consume(ParserTokenType.STRING, "Expected type").value
        elif token_type == ParserTokenType.FUNCTION:
            base_type = self.consume(ParserTokenType.FUNCTION, "Expected type").value
        else:
            raise SyntaxError(f"Expected type annotation, got {self.peek().type}")
        
        # Check for pointer modifier (e.g., int*)
        if self.match(ParserTokenType.STAR):
            return {"type": "pointer", "base_type": base_type}
        else:
            return base_type

    def parse_variable(self, modifiers=None):
        if modifiers is None:
            modifiers = []
        name = self.consume(ParserTokenType.IDENTIFIER, "Expected variable name")
        var_type = None
        initializer = None
        
        # Handle type annotation: let x: int
        if self.match(ParserTokenType.COLON):
            var_type = self.parse_type_annotation()
        
        # Handle initialization: let x = value or let x: int = value
        if self.match(ParserTokenType.EQ):
            initializer = self.parse_expression()
        
        self.consume(ParserTokenType.SEMICOLON, "Expected ';' after variable")
        return {"type": "var_decl", "name": name.value, "var_type": var_type, "init": initializer, "modifiers": modifiers}

    def parse_import(self):
        """Parse import statements: import module.path [as alias]"""
        module_path = []
        module_path.append(self.consume(ParserTokenType.IDENTIFIER, "Expected module name").value)
        
        while self.match(ParserTokenType.DOT):
            module_path.append(self.consume(ParserTokenType.IDENTIFIER, "Expected module name after '.'").value)
        
        alias = None
        if self.match(ParserTokenType.AS):
            alias = self.consume(ParserTokenType.IDENTIFIER, "Expected alias name").value
        
        self.consume(ParserTokenType.SEMICOLON, "Expected ';' after import statement")
        return {"type": "import", "module": ".".join(module_path), "alias": alias}

    def parse_from_import(self):
        """Parse from import statements: from module.path import item1, item2 [as alias]"""
        # Parse module path
        module_path = []
        module_path.append(self.consume(ParserTokenType.IDENTIFIER, "Expected module name").value)
        
        while self.match(ParserTokenType.DOT):
            module_path.append(self.consume(ParserTokenType.IDENTIFIER, "Expected module name after '.'").value)
        
        # Expect 'import' keyword
        self.consume(ParserTokenType.IMPORT, "Expected 'import' after module path")
        
        # Parse imported items
        imports = []
        imports.append(self.consume(ParserTokenType.IDENTIFIER, "Expected import item").value)
        
        while self.match(ParserTokenType.COMMA):
            imports.append(self.consume(ParserTokenType.IDENTIFIER, "Expected import item").value)
        
        self.consume(ParserTokenType.SEMICOLON, "Expected ';' after from import statement")
        return {"type": "from_import", "module": ".".join(module_path), "imports": imports}

    def parse_namespace(self):
        """Parse namespace declarations: namespace Name { ... }"""
        name = self.consume(ParserTokenType.IDENTIFIER, "Expected namespace name")
        self.consume(ParserTokenType.LBRACE, "Expected '{' after namespace name")
        
        statements = []
        while not self.match(ParserTokenType.RBRACE):
            statements.append(self.parse_declaration())
        
        return {"type": "namespace", "name": name.value, "body": statements}

    def parse_block(self):
        self.consume(ParserTokenType.LBRACE, "Expected '{'")
        statements = []
        while not self.match(ParserTokenType.RBRACE):
            statements.append(self.parse_statement())
        return statements

    def parse_statement(self):
        if self.match(ParserTokenType.LET):
            return self.parse_variable_declaration()
        elif self.match(ParserTokenType.IF):
            return self.parse_if()
        elif self.match(ParserTokenType.WHILE):
            return self.parse_while()
        elif self.match(ParserTokenType.DO):
            return self.parse_do_while()
        elif self.match(ParserTokenType.FOR):
            return self.parse_for()
        elif self.match(ParserTokenType.SWITCH):
            return self.parse_switch()
        elif self.match(ParserTokenType.MATCH):
            return self.parse_match()
        elif self.match(ParserTokenType.TRY):
            return self.parse_try()
        elif self.match(ParserTokenType.THROW):
            return self.parse_throw()
        elif self.match(ParserTokenType.RETURN):
            return self.parse_return()
        elif self.match(ParserTokenType.BREAK):
            return self.parse_break()
        elif self.match(ParserTokenType.CONTINUE):
            return self.parse_continue()
        elif self.match(ParserTokenType.LBRACE):
            self.pos -= 1
            return {"type": "block", "body": self.parse_block()}
        else:
            # Check for assignment statement: identifier = expression
            if (self.peek().type == ParserTokenType.IDENTIFIER and 
                self.pos + 1 < len(self.tokens) and 
                self.tokens[self.pos + 1].type == ParserTokenType.EQ):
                return self.parse_assignment()
            else:
                expr = self.parse_expression()
                self.consume(ParserTokenType.SEMICOLON, "Expected ';'")
                return {"type": "expr_stmt", "expr": expr}

    def parse_assignment(self):
        """Parse assignment statements: identifier = expression"""
        name = self.consume(ParserTokenType.IDENTIFIER, "Expected identifier")
        self.consume(ParserTokenType.EQ, "Expected '='")
        value = self.parse_expression()
        self.consume(ParserTokenType.SEMICOLON, "Expected ';'")
        return {"type": "assignment", "name": name.value, "value": value}

    def parse_variable_declaration(self):
        """Parse variable declarations: let name [: type] [= value]"""
        # Allow type keywords as variable names
        if self.peek().type in [ParserTokenType.IDENTIFIER, ParserTokenType.INT, ParserTokenType.FLOAT, 
                                ParserTokenType.DOUBLE, ParserTokenType.BOOL, ParserTokenType.VOID, 
                                ParserTokenType.ANY, ParserTokenType.PTR, ParserTokenType.STRING, 
                                ParserTokenType.FUNCTION]:
            name = self.tokens[self.pos]
            self.pos += 1
        else:
            name = self.consume(ParserTokenType.IDENTIFIER, "Expected variable name")
        
        # Optional type annotation
        var_type = None
        if self.match(ParserTokenType.COLON):
            var_type = self.parse_type_annotation()
        
        # Optional initialization (for dynamic variables)
        value = None
        if self.match(ParserTokenType.EQ):
            value = self.parse_expression()
        elif var_type is None:
            # No type and no initialization - this is a dynamic variable
            var_type = "dynamic"
        
        self.consume(ParserTokenType.SEMICOLON, "Expected ';'")
        
        return {"type": "variable_declaration", "name": name.value, "var_type": var_type, "value": value}

    def parse_if(self):
        self.consume(ParserTokenType.LPAREN, "Expected '(' after 'if'")
        condition = self.parse_expression()
        self.consume(ParserTokenType.RPAREN, "Expected ')'")
        then_branch = self.parse_statement()
        else_branch = self.parse_statement() if self.match(ParserTokenType.ELSE) else None
        return {"type": "if", "cond": condition, "then": then_branch, "else": else_branch}

    def parse_while(self):
        self.consume(ParserTokenType.LPAREN, "Expected '(' after 'while'")
        condition = self.parse_expression()
        self.consume(ParserTokenType.RPAREN, "Expected ')'")
        body = self.parse_statement()
        return {"type": "while", "cond": condition, "body": body}

    def parse_do_while(self):
        """Parse do-while statements: do { body } while (condition);"""
        body = self.parse_statement()
        self.consume(ParserTokenType.WHILE, "Expected 'while' after do body")
        self.consume(ParserTokenType.LPAREN, "Expected '(' after 'while'")
        condition = self.parse_expression()
        self.consume(ParserTokenType.RPAREN, "Expected ')'")
        self.consume(ParserTokenType.SEMICOLON, "Expected ';' after do-while statement")
        return {"type": "do_while", "body": body, "cond": condition}

    def parse_return(self):
        value = None
        if not self.peek().type == ParserTokenType.SEMICOLON:
            value = self.parse_expression()
        self.consume(ParserTokenType.SEMICOLON, "Expected ';' after return statement")
        return {"type": "return", "value": value}

    def parse_for(self):
        """Parse for statements: for (init; condition; update) body"""
        self.consume(ParserTokenType.LPAREN, "Expected '(' after 'for'")
        
        # For loop initialization
        init = None
        if not self.peek().type == ParserTokenType.SEMICOLON:
            if self.match(ParserTokenType.LET):
                # Parse variable declaration without consuming semicolon here
                name = self.consume(ParserTokenType.IDENTIFIER, "Expected variable name")
                var_type = None
                initializer = None
                
                # Handle type annotation: let x: int
                if self.match(ParserTokenType.COLON):
                    var_type = self.parse_type_annotation()
                
                # Handle initialization: let x = value or let x: int = value
                if self.match(ParserTokenType.EQ):
                    initializer = self.parse_expression()
                
                init = {"type": "var_decl", "name": name.value, "var_type": var_type, "init": initializer}
            else:
                init = self.parse_expression()
        self.consume(ParserTokenType.SEMICOLON, "Expected ';'")
        
        # For loop condition
        condition = None
        if not self.peek().type == ParserTokenType.SEMICOLON:
            condition = self.parse_expression()
        self.consume(ParserTokenType.SEMICOLON, "Expected ';'")
        
        # For loop update
        update = None
        if not self.peek().type == ParserTokenType.RPAREN:
            update = self.parse_expression()
        self.consume(ParserTokenType.RPAREN, "Expected ')'")
        
        body = self.parse_statement()
        return {"type": "for", "init": init, "condition": condition, "update": update, "body": body}

    def parse_switch(self):
        """Parse switch statements: switch (expression) { case value: ... default: ... }"""
        self.consume(ParserTokenType.LPAREN, "Expected '(' after 'switch'")
        expr = self.parse_expression()
        self.consume(ParserTokenType.RPAREN, "Expected ')'")
        self.consume(ParserTokenType.LBRACE, "Expected '{'")
        
        cases = []
        default_case = None
        
        while not self.match(ParserTokenType.RBRACE):
            if self.match(ParserTokenType.CASE):
                value = self.parse_expression()
                self.consume(ParserTokenType.COLON, "Expected ':' after case value")
                statements = []
                while (not self.peek().type in [ParserTokenType.CASE, ParserTokenType.DEFAULT, ParserTokenType.RBRACE]):
                    statements.append(self.parse_statement())
                cases.append({"value": value, "statements": statements})
            elif self.match(ParserTokenType.DEFAULT):
                self.consume(ParserTokenType.COLON, "Expected ':' after 'default'")
                statements = []
                while (not self.peek().type in [ParserTokenType.CASE, ParserTokenType.DEFAULT, ParserTokenType.RBRACE]):
                    statements.append(self.parse_statement())
                default_case = statements
            else:
                break
        
        return {"type": "switch", "expr": expr, "cases": cases, "default": default_case}

    def parse_match(self):
        """Parse match statements: match expression { pattern => action; ... else => default; }"""
        expr = self.parse_expression()
        self.consume(ParserTokenType.LBRACE, "Expected '{' after match expression")
        
        cases = []
        default_case = None
        
        while not self.match(ParserTokenType.RBRACE):
            if self.match(ParserTokenType.ELSE):
                # Default case
                self.consume(ParserTokenType.ARROW, "Expected '=>' after 'else'")
                action = self.parse_statement()  # Allow statements, not just expressions
                default_case = action
            else:
                # Pattern case
                pattern = self.parse_expression()  # This will handle regex literals
                self.consume(ParserTokenType.ARROW, "Expected '=>' after pattern")
                action = self.parse_statement()  # Allow statements, not just expressions
                cases.append({"pattern": pattern, "action": action})
        
        return {"type": "match", "expr": expr, "cases": cases, "default": default_case}

    def parse_try(self):
        """Parse try-catch-finally statements"""
        # Parse try block
        try_block = self.parse_block()
        
        catch_blocks = []
        finally_block = None
        
        # Parse catch blocks
        while self.match(ParserTokenType.CATCH):
            self.consume(ParserTokenType.LPAREN, "Expected '(' after 'catch'")
            exception_name = self.consume(ParserTokenType.IDENTIFIER, "Expected exception name").value
            exception_type = None
            
            # Handle type annotation: catch (e: Error)
            if self.match(ParserTokenType.COLON):
                exception_type = self.parse_type_annotation()
            
            self.consume(ParserTokenType.RPAREN, "Expected ')'")
            
            catch_body = self.parse_block()
            catch_blocks.append({
                "name": exception_name,
                "type": exception_type,
                "body": catch_body
            })
        
        # Parse finally block
        if self.match(ParserTokenType.FINALLY):
            finally_block = self.parse_block()
        
        return {"type": "try", "try_block": try_block, "catch_blocks": catch_blocks, "finally_block": finally_block}

    def parse_throw(self):
        """Parse throw statements: throw expression;"""
        expr = self.parse_expression()
        self.consume(ParserTokenType.SEMICOLON, "Expected ';' after throw statement")
        return {"type": "throw", "expr": expr}

    def parse_break(self):
        """Parse break statements"""
        self.consume(ParserTokenType.SEMICOLON, "Expected ';' after 'break'")
        return {"type": "break"}

    def parse_continue(self):
        """Parse continue statements"""
        self.consume(ParserTokenType.SEMICOLON, "Expected ';' after 'continue'")
        return {"type": "continue"}

    def parse_expression(self):
        return self.parse_assignment_expr()

    def parse_assignment_expr(self):
        """Parse assignment expressions: identifier = expression or object.member = expression or *ptr = expression"""
        # Check for lambda expressions: (param1, param2) => expression or () => expression
        if self.peek().type == ParserTokenType.LPAREN:
            # Look ahead to see if this is a lambda
            saved_pos = self.pos
            is_lambda = False
            params = []
            
            try:
                self.pos += 1  # consume (
                
                # Try to parse parameter list
                if self.peek().type == ParserTokenType.RPAREN:
                    # Empty parameter list - check for arrow
                    self.pos += 1  # consume )
                    if self.peek().type == ParserTokenType.ARROW:
                        is_lambda = True
                        params = []
                else:
                    # Try to parse parameter names
                    while True:
                        if self.peek().type != ParserTokenType.IDENTIFIER:
                            break  # Not a lambda
                        params.append(self.consume(ParserTokenType.IDENTIFIER, "Expected parameter name").value)
                        
                        if self.peek().type == ParserTokenType.RPAREN:
                            self.pos += 1  # consume )
                            if self.peek().type == ParserTokenType.ARROW:
                                is_lambda = True
                            break
                        elif self.peek().type == ParserTokenType.COMMA:
                            self.pos += 1  # consume ,
                        else:
                            break  # Not a lambda
                
                if is_lambda:
                    # Parse lambda
                    self.consume(ParserTokenType.ARROW, "Expected '=>'")
                    
                    # Check if lambda body is a block or expression
                    if self.peek().type == ParserTokenType.LBRACE:
                        body = self.parse_block()
                    else:
                        body = self.parse_assignment_expr()
                    
                    return {"type": "lambda", "params": params, "body": body}
                else:
                    # Not a lambda, restore position
                    self.pos = saved_pos
            except:
                # Error during lookahead, restore position
                self.pos = saved_pos
        
        expr = self.parse_logical_or()
        
        if self.match(ParserTokenType.EQ):
            # This is an assignment
            if expr.get("type") not in ["identifier", "member", "unary"]:
                raise SyntaxError("Invalid assignment target")
            value = self.parse_assignment_expr()
            if expr.get("type") == "identifier":
                return {"type": "assignment", "name": expr["value"], "value": value}
            else:  # member access
                return {"type": "member_assignment", "target": expr, "value": value}
        
        return expr

    def parse_logical_or(self):
        expr = self.parse_logical_and()
        while self.match(ParserTokenType.PIPEPIPE):
            operator = self.tokens[self.pos - 1]
            right = self.parse_logical_and()
            expr = {"type": "binary", "op": operator.value, "left": expr, "right": right}
        return expr

    def parse_logical_and(self):
        expr = self.parse_equality()
        while self.match(ParserTokenType.AMPAMP):
            operator = self.tokens[self.pos - 1]
            right = self.parse_equality()
            expr = {"type": "binary", "op": operator.value, "left": expr, "right": right}
        return expr

    def parse_equality(self):
        expr = self.parse_comparison()
        while self.match(ParserTokenType.EQEQ, ParserTokenType.BANGEQ):
            operator = self.tokens[self.pos - 1]
            right = self.parse_comparison()
            expr = {"type": "binary", "op": operator.value, "left": expr, "right": right}
        return expr

    def parse_comparison(self):
        expr = self.parse_cast()
        while self.match(ParserTokenType.GT, ParserTokenType.GTEQ, ParserTokenType.LT, ParserTokenType.LTEQ, ParserTokenType.INSTANCEOF):
            operator = self.tokens[self.pos - 1]
            right = self.parse_cast()
            expr = {"type": "binary", "op": operator.value, "left": expr, "right": right}
        return expr

    def parse_cast(self):
        expr = self.parse_term()
        while self.match(ParserTokenType.AS):
            operator = self.tokens[self.pos - 1]
            # Parse qualified type names like "Examples.Shape"
            type_name = self.consume(ParserTokenType.IDENTIFIER, "Expected type name after 'as'").value
            while self.match(ParserTokenType.DOT):
                part = self.consume(ParserTokenType.IDENTIFIER, "Expected identifier after '.'").value
                type_name += "." + part
            expr = {"type": "cast", "expr": expr, "target_type": type_name}
        return expr

    def parse_term(self):
        expr = self.parse_factor()
        while self.match(ParserTokenType.PLUS, ParserTokenType.MINUS):
            operator = self.tokens[self.pos - 1]
            right = self.parse_factor()
            expr = {"type": "binary", "op": operator.value, "left": expr, "right": right}
        return expr

    def parse_factor(self):
        expr = self.parse_unary()
        while self.match(ParserTokenType.STAR, ParserTokenType.SLASH, ParserTokenType.MOD):
            operator = self.tokens[self.pos - 1]
            right = self.parse_unary()
            expr = {"type": "binary", "op": operator.value, "left": expr, "right": right}
        return expr

    def parse_unary(self):
        if self.match(ParserTokenType.MINUS, ParserTokenType.BANG, ParserTokenType.STAR, ParserTokenType.AMP):
            operator = self.tokens[self.pos - 1]
            right = self.parse_unary()
            return {"type": "unary", "op": operator.value, "right": right}
        return self.parse_primary()

    def parse_primary(self):
        if self.match(ParserTokenType.NUMBER):
            return {"type": "number", "value": self.tokens[self.pos - 1].value}
        elif self.match(ParserTokenType.STRING_LITERAL):
            return {"type": "string", "value": self.tokens[self.pos - 1].value}
        elif self.match(ParserTokenType.REGEX):
            return {"type": "regex", "value": self.tokens[self.pos - 1].value}
        elif self.match(ParserTokenType.TRUE):
            return {"type": "boolean", "value": True}
        elif self.match(ParserTokenType.FALSE):
            return {"type": "boolean", "value": False}
        elif self.match(ParserTokenType.NULL):
            return {"type": "null", "value": None}
        elif self.match(ParserTokenType.NEW):
            # Parse new expression: new ClassName(args) or new Namespace.ClassName(args)
            class_name = self.consume(ParserTokenType.IDENTIFIER, "Expected class name after 'new'").value
            # Handle qualified class names like Examples.Circle
            while self.match(ParserTokenType.DOT):
                part = self.consume(ParserTokenType.IDENTIFIER, "Expected identifier after '.'").value
                class_name += "." + part
            self.consume(ParserTokenType.LPAREN, "Expected '(' after class name")
            args = []
            if not self.peek().type == ParserTokenType.RPAREN:
                while True:
                    args.append(self.parse_expression())
                    if self.peek().type == ParserTokenType.RPAREN:
                        break
                    self.consume(ParserTokenType.COMMA, "Expected ',' or ')' in constructor arguments")
            self.consume(ParserTokenType.RPAREN, "Expected ')'")
            return {"type": "new", "class": class_name, "args": args}
        elif self.match(ParserTokenType.IDENTIFIER):
            identifier = self.tokens[self.pos - 1]
            return self.parse_postfix({"type": "identifier", "value": identifier.value})
        elif self.peek().type in [ParserTokenType.PTR, ParserTokenType.INT, ParserTokenType.FLOAT, 
                                  ParserTokenType.BOOL, ParserTokenType.ANY, ParserTokenType.VOID, ParserTokenType.THIS,
                                  ParserTokenType.DOUBLE, ParserTokenType.STRING, ParserTokenType.CHAR]:
            # Handle keywords used as variable names in expression contexts
            identifier = self.tokens[self.pos]
            self.pos += 1
            return self.parse_postfix({"type": "identifier", "value": identifier.value})
        elif self.match(ParserTokenType.LPAREN):
            # Check if this is a lambda expression: (param: type) => expr
            # We need to look ahead to see if this looks like lambda parameters
            saved_pos = self.pos
            is_lambda = False
            
            # Try to detect lambda pattern: ( identifier : type ) =>
            if self.peek().type == ParserTokenType.IDENTIFIER:
                self.pos += 1  # skip identifier
                if self.peek().type == ParserTokenType.COLON:
                    is_lambda = True
            elif self.peek().type == ParserTokenType.RPAREN:
                # Empty parameter list: () => expr
                self.pos += 1  # skip )
                if self.peek().type == ParserTokenType.ARROW:
                    is_lambda = True
            
            # Restore position
            self.pos = saved_pos
            
            if is_lambda:
                return self.parse_lambda()
            else:
                # Regular parenthesized expression
                expr = self.parse_expression()
                self.consume(ParserTokenType.RPAREN, "Expected ')'")
                return expr
        elif self.match(ParserTokenType.LBRACKET):
            # Parse array literal: [element1, element2, ...]
            elements = []
            if not self.peek().type == ParserTokenType.RBRACKET:
                while True:
                    elements.append(self.parse_expression())
                    if self.peek().type == ParserTokenType.RBRACKET:
                        break
                    self.consume(ParserTokenType.COMMA, "Expected ',' or ']' in array literal")
            self.consume(ParserTokenType.RBRACKET, "Expected ']'")
            return {"type": "array_literal", "elements": elements}
        raise SyntaxError("Expected expression")

    def parse_lambda(self):
        """Parse lambda expressions: (param: type, ...) => expr or (param: type, ...) => { block }"""
        # Note: LPAREN is already consumed by the caller
        params = []
        
        if not self.match(ParserTokenType.RPAREN):
            while True:
                param_name = self.consume(ParserTokenType.IDENTIFIER, "Expected parameter name")
                self.consume(ParserTokenType.COLON, "Expected ':' after parameter name")
                param_type = self.parse_type_annotation()
                params.append({"name": param_name.value, "type": param_type})
                
                if self.match(ParserTokenType.RPAREN):
                    break
                self.consume(ParserTokenType.COMMA, "Expected ',' or ')' in lambda parameters")
        
        self.consume(ParserTokenType.ARROW, "Expected '=>' after lambda parameters")
        
        # Parse lambda body - can be expression or block
        if self.peek().type == ParserTokenType.LBRACE:
            body = self.parse_block()
            return {"type": "lambda", "params": params, "body": body}
        else:
            expr = self.parse_expression()
            return {"type": "lambda", "params": params, "body": expr}

    def parse_postfix(self, expr):
        """Handle postfix operations like function calls and member access"""
        while True:
            if self.match(ParserTokenType.LPAREN):
                # Function call
                args = []
                if not self.peek().type == ParserTokenType.RPAREN:
                    while True:
                        args.append(self.parse_expression())
                        if self.peek().type == ParserTokenType.RPAREN:
                            break
                        self.consume(ParserTokenType.COMMA, "Expected ',' or ')' in argument list")
                self.consume(ParserTokenType.RPAREN, "Expected ')'")
                expr = {"type": "call", "callee": expr, "args": args}
            elif self.match(ParserTokenType.DOT):
                # Member access
                member = self.consume(ParserTokenType.IDENTIFIER, "Expected member name")
                expr = {"type": "member", "object": expr, "member": member.value}
            else:
                break
        return expr
