%{
#include <stdio.h>
#include <stdlib.h>
int sum = 0, count = 0;
%}

%%
[0-9]+  {
            sum += atoi(yytext);
            count++;
        }
.|\n    { /* ignore */ }
%%

int main() {
    yylex();
    if(count > 0)
        printf("Average = %.2f\n", (float)sum/count);
    else
        printf("No numbers entered.\n");
    return 0;
}

int yywrap() {
     return 1; 
}
