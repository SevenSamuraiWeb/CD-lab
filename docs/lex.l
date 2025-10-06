%{
    #include<stdio.h>
    #include<string.h>
    int count = 0;
%}

%%
if |
else |
while |
for |
int |
double |
return {count++; printf("%s is a keyword",yytext);}
[a-zA-Z]+   { /* ignore other words */ }
.|\n        { /* ignore newline */ }
%%

int main()
{   
    // The function that starts the analysis
    printf("Type keywords (Ctrl+D to end):\n");
    yylex();
    printf("Keywords found:%d",count);
    return 0;
}

int yywrap() {
    return 1; // tell scanner: no more input
}
