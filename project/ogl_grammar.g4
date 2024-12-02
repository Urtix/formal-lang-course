grammar ogl_grammar;

prog: stmt*;

stmt: bind | add | remove | declare;

declare: LET VAR IS GRAPH;

bind: LET VAR EQUAL expr;

remove: REMOVE (VERTEX | EDGE | VERTICES) expr FROM VAR;

add: ADD (VERTEX | EDGE) expr TO VAR;

expr: NUM | CHAR | VAR | edge_expr | set_expr | regexp | select;

set_expr: LEFT_SBRACKET expr (COMMA expr)* RIGHT_SBRACKET;

edge_expr: LEFT_PAREN expr COMMA expr COMMA expr RIGHT_PAREN;


regexp:
    CHAR
    | VAR
    | LEFT_PAREN regexp RIGHT_PAREN
    | regexp STICK regexp | regexp CARET range
    | regexp DOT regexp
    | regexp AMPERSAND regexp
;

range: LEFT_SBRACKET NUM DOUBLE_DOT NUM? RIGHT_SBRACKET;

select: v_filter? v_filter? RETURN VAR (COMMA VAR)? WHERE VAR REACHABLE FROM VAR IN VAR BY expr;

v_filter: FOR VAR IN expr;

LET:            'let';
IS:             'is';
GRAPH:          'graph';
REMOVE:         'remove';
WHERE:          'where';
REACHABLE:      'reachable';
RETURN:         'return';
BY:             'by';
VERTEX:         'vertex';
EDGE:           'edge';
VERTICES:       'vertices';
FROM:           'from';
ADD:            'add';
TO:             'to';
FOR:            'for';
IN:             'in';

EQUAL:           '=';
LEFT_SBRACKET:   '[';
RIGHT_SBRACKET:  ']';
LEFT_PAREN:      '(';
RIGHT_PAREN:     ')';
COMMA:           ',';
CARET:           '^';
DOT:             '.';
AMPERSAND:       '&';
DOUBLE_DOT:      '..';
STICK:           '|';
QUOTES:          '"';

VAR: [a-z] [a-z0-9]*;
NUM: [0] | ([1-9] [0-9]*);
CHAR: QUOTES [a-z] QUOTES;
