%{
#include <stdio.h>
int num=0;
%}

%%
[0-9]+ {
int num = atoi(yytext);
    printf("Decimal: %s -> Hexadecimal: %X\n", yytext, num);
}
%%


int main(){
    yylex();
    return 0;
}

int yywrap() {
     return 1; 
}
