%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "y.tab.h"

void yyerror(const char *s);

%}
ID     [a-zA-Z_][a-zA-Z0-9_]*
NUMBER [0-9]+

%%
"while"   { return WHILE; }

"<"     { yylval.sval = strdup(yytext); return RELOP; }
"<="    { yylval.sval = strdup(yytext); return RELOP; }
">"     { yylval.sval = strdup(yytext); return RELOP; }
">="    { yylval.sval = strdup(yytext); return RELOP; }
"=="    { yylval.sval = strdup(yytext); return RELOP; }
"!="    { yylval.sval = strdup(yytext); return RELOP; }

{ID}      { yylval.sval = strdup(yytext); return ID; }

{NUMBER}  { yylval.sval = strdup(yytext); return NUMBER; }

[ \t]     { /* Skip whitespace */ }

\n        { yylineno++; }

.         { return yytext[0]; }

%%
int yywrap() {
    return 1;
}
