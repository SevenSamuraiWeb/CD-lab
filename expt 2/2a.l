%{
#include <stdio.h> 
#include <stdlib.h> 
#include <string.h>
%}

digit	[0-9]
id	[A-Za-z_][A-Za-z0-9_]* 
int_const {digit}+
float_const {digit}+"."{digit}+ 
char_const \'([^\\\n]|(\\.))\' 
string_const \"([^\\\n]|(\\.))*\"
phone_num (\+{digit}{1,3}[- ]?)?{digit}{10}
email_addr [A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,} 
ws	[ \t\r]+

%%
(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|inline|int|long|register|restrict|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while) { printf("Keyword: %s\n", yytext); }

phone		{ printf("Keyword: phone\n"); } 
email	{ printf("Keyword: email\n"); }

{id}	{ printf("Identifier: %s\n", yytext); }
{int_const}	{ printf("Integer Constant: %s\n", yytext); }
{float_const} { printf("Float Constant: %s\n", yytext); }
{char_const}	{ printf("Char Constant: %s\n", yytext); }
{string_const} { printf("String Constant: %s\n", yytext); }
{phone_num}	{ printf("Phone Number: %s\n", yytext); }
{email_addr}	{ printf("Email Address: %s\n", yytext); }

"=="	{ printf("Operator: ==\n"); }
"!="	{ printf("Operator: !=\n"); }
"<="	{ printf("Operator: <=\n"); }
">="	{ printf("Operator: >=\n"); }
"+"	{ printf("Operator: +\n"); }
"-"	{ printf("Operator: -\n"); }
"*"	{ printf("Operator: *\n"); }
"/"	{ printf("Operator: /\n"); }
"="	{ printf("Operator: =\n"); }
"<"	{ printf("Operator: <\n"); }
">"	{ printf("Operator: >\n"); }
"!"	{ printf("Operator: !\n"); }

";"	{ printf("Punctuator: ;\n"); }
","	{ printf("Punctuator: ,\n"); }
"{"	{ printf("Punctuator: {\n"); }
"}"	{ printf("Punctuator: }\n"); }
"("	{ printf("Punctuator: (\n"); }
")"	{ printf("Punctuator: )\n"); }

"//".*	{ printf("Single-line Comment: %s\n",yytext); } 
"/*"([^*]|\*[^/])*"*/" { printf("Multi-line Comment:%s\n",yytext); }

{ws}	;
.	{ printf("Unknown token: %s\n", yytext); }
%%

int main(int argc, char *argv[]) {
    if (argc > 1) {
        FILE *f = fopen(argv[1], "r"); 
        if (!f) {
            printf("Error: Could not open file %s\n", argv[1]); 
            return 1;
        }
        yyin = f;
    }
    yylex(); 
    return 0;
}

int yywrap() { 
    return 1;
}
