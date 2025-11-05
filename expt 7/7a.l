%{
#include "y.tab.h"
#include <stdlib.h>

extern YYSTYPE yylval;
%}

%%

[ \t] ; 

"int" { return TYPE; }
"float" { return TYPE; }

[a-zA-Z_][a-zA-Z0-9_]* { return ID; }

[0-9]+ { 
    yylval.ival = atoi(yytext); 
    return NUMBER; 
}

[+\-*/=(),;] { return yytext[0]; } 

\n { return '\n'; } 

. { yyerror("Invalid character"); }

%%

int yywrap(void) {
    return 1;
}
