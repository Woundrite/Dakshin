import sys
sys.path.append('src')
from Parser import DakshinParser
from Lexer import Lexer

# Test parsing the function test
code = """
function testFunc(x) {
    println("In testFunc, x =", x);
    return x * 2;
}

function main() {
    println("Before function call");
    let result = testFunc(5);
    println("Result:", result);
    return 0;
}
"""

lexer = Lexer(code)
tokens = lexer.tokenize()
parser = DakshinParser(tokens)
ast = parser.parse()

import json
print(json.dumps(ast, indent=2))
