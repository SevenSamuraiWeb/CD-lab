%{
#include <stdio.h>
%}

%%
[0-9]+              { printf("%s is an Integer\n", yytext); }
[0-9]+"."[0-9]+     { printf("%s is a Real Number\n", yytext); }
[a-zA-Z]+           { printf("%s is a Word\n", yytext); }
.|\n                { /* ignore other characters */ }
%%

int main() {
    yylex();
    return 0;
}

int yywrap() {
     return 1; 
}
