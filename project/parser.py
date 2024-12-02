from project.ogl_grammarLexer import ogl_grammarLexer
from project.ogl_grammarParser import ogl_grammarParser
from antlr4 import (
    InputStream,
    CommonTokenStream,
    ParserRuleContext,
)


def program_to_tree(program: str) -> tuple[ParserRuleContext, bool]:
    input_stream = InputStream(program)
    lexer = ogl_grammarLexer(input_stream)
    stream = CommonTokenStream(lexer)

    parser = ogl_grammarParser(stream)
    parser.removeParseListeners()
    tree = parser.prog()

    if parser.getNumberOfSyntaxErrors() != 0:
        return None, False

    return tree, True


def nodes_count(tree: ParserRuleContext) -> int:
    if tree.getChildCount() == 0:
        return 1

    result = 1
    for children in tree.getChildren():
        result += nodes_count(children)

    return result


def tree_to_program(tree: ParserRuleContext) -> str:
    if tree.getChildCount() == 0:
        text = tree.getText()
        return f"{text} " if text != "\n" else text

    result = ""
    for children in tree.getChildren():
        result += tree_to_program(children)

    return result
