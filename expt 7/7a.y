%{
#include <stdio.h>
#include <stdlib.h>
void yyerror(char *s);
extern int yylex();
%}

%union {
int ival;
}

%token <ival> NUMBER
%token ID
%token TYPE
%type <ival> expr
%left '+' '-'
%left '*' '/'

%%
program:
lines
;

lines:
| lines line
;

line:
decl
| assign_stmt
| expr_stmt
| '\n'
| error '\n' { yyerrok; }
;

decl:
TYPE id_list ';' { printf(">> Syntax valid: Declaration\n"); }
;

id_list:
ID
| id_list ',' ID
;

assign_stmt:
ID '=' expr ';' { printf(">> Syntax valid: Assignment (RHS value = %d)\n", $3); }
;

expr_stmt:
expr ';' { printf("= %d\n", $1); }
;

expr:
NUMBER { $$ = $1; }
| ID { $$ = 0; } 
| expr '+' expr { $$ = $1 + $3; }
| expr '-' expr { $$ = $1 - $3; }
| expr '*' expr { $$ = $1 * $3; }
| expr '/' expr { 
if ($3 == 0) {
yyerror("Division by zero");
$$ = 0;
} else {
$$ = $1 / $3;
}
}
| '(' expr ')' { $$ = $2; }
;

%%

#include "lex.yy.c"

int main(void) {
printf("--- YACC Lab: Parser ---\n");
printf("Enter statements, declarations, or expressions followed by ';'\n");
yyparse();
return 0;
}

void yyerror(char *s) {
fprintf(stderr, "Parse Error: %s\n", s);
}
