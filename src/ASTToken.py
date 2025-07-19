class ASTNode:
    def __init__(self, type_, children=None, value=None):
        self.type = type_
        self.children = children or []
        self.value = value

    def __repr__(self):
        if self.value is not None:
            return f"{self.type}({self.value})"
        return f"{self.type}({', '.join(map(str, self.children))})"
    
    def __str__(self):
        return self.__repr__()
