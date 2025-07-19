"""
AST Visualization Generator for Dakshin Programming Language
Generates a visual tree representation of the parsed AST
"""

import json

def print_ast_tree(node, prefix="", is_last=True, is_root=True):
    """Print AST in a tree format"""
    if is_root:
        print("🌳 Abstract Syntax Tree")
        print("═" * 50)
    
    # Determine the connector
    connector = "└── " if is_last else "├── "
    if is_root:
        connector = ""
    
    # Print current node
    if isinstance(node, dict):
        node_type = node.get('type', 'unknown')
        node_name = node.get('name', node.get('value', ''))
        
        if node_name:
            print(f"{prefix}{connector}{node_type}: {node_name}")
        else:
            print(f"{prefix}{connector}{node_type}")
        
        # Prepare prefix for children
        child_prefix = prefix + ("    " if is_last or is_root else "│   ")
        
        # Get all keys except 'type'
        keys = [k for k in node.keys() if k != 'type']
        
        for i, key in enumerate(keys):
            is_last_child = (i == len(keys) - 1)
            value = node[key]
            
            if isinstance(value, list) and value:
                print(f"{child_prefix}{'└── ' if is_last_child else '├── '}{key}: [{len(value)} items]")
                list_prefix = child_prefix + ("    " if is_last_child else "│   ")
                for j, item in enumerate(value):
                    is_last_item = (j == len(value) - 1)
                    print_ast_tree(item, list_prefix, is_last_item, False)
            elif isinstance(value, dict):
                print(f"{child_prefix}{'└── ' if is_last_child else '├── '}{key}:")
                dict_prefix = child_prefix + ("    " if is_last_child else "│   ")
                print_ast_tree(value, dict_prefix, True, False)
            elif isinstance(value, list) and not value:
                print(f"{child_prefix}{'└── ' if is_last_child else '├── '}{key}: []")
            else:
                print(f"{child_prefix}{'└── ' if is_last_child else '├── '}{key}: {value}")
    
    elif isinstance(node, list):
        for i, item in enumerate(node):
            is_last_item = (i == len(node) - 1)
            print_ast_tree(item, prefix, is_last_item, False)
    
    else:
        print(f"{prefix}{connector}{node}")

# Sample AST from test_constructor.dn
ast_data = [
  {
    "type": "class",
    "name": "TestClass",
    "base": [],
    "modifiers": [],
    "members": [
      {
        "type": "constructor",
        "name": "TestClass",
        "params": [
          {
            "name": "param",
            "type": "int"
          }
        ],
        "modifiers": [
          "public"
        ],
        "super": {
          "args": []
        },
        "body": [
          {
            "type": "expr_stmt",
            "expr": {
              "type": "call",
              "callee": {
                "type": "identifier",
                "value": "print"
              },
              "args": [
                {
                  "type": "string",
                  "value": "\"Constructor called\""
                }
              ]
            }
          }
        ]
      }
    ]
  }
]

if __name__ == "__main__":
    print_ast_tree(ast_data)
    
    print("\n" + "═" * 50)
    print("📊 AST Statistics:")
    print(f"• Total nodes: Multiple (nested structure)")
    print(f"• Depth levels: 7")
    print(f"• Node types: class, constructor, expr_stmt, call, identifier, string")
    print(f"• Root declarations: {len(ast_data)}")
    
    print("\n" + "═" * 50)
    print("🔍 Parser Journey:")
    print("1. parse() → Starts parsing")
    print("2. parse_declaration() → Finds 'class' keyword")
    print("3. parse_class() → Parses class structure")
    print("4. parse_constructor() → Handles constructor with super call")
    print("5. parse_block() → Parses constructor body")
    print("6. parse_statement() → Parses print statement")
    print("7. parse_expression() → Parses function call")
    print("8. parse_postfix() → Handles function call syntax")
    print("9. parse_primary() → Parses string literal")
