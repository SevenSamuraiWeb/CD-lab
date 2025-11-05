%{
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

char* new_temp();
char* new_label();
void gen_tac(const char *res, const char *arg1, const char *arg2, const char *op);

extern int yylex();
extern int yylineno;
extern char *yytext;
void yyerror(const char *s);

/* --- Stack for managing loop labels --- */
char *label_stack[100];
int label_top = -1;
void push_label(char *label) { label_stack[++label_top] = label; }
char *pop_label() { return label_stack[label_top--]; }

%}

/* Define the union to hold string pointers (for variable/temp names) */
%union {
    char *sval;
}

/* Tokens that carry a string value from the lexer */
%token <sval> ID NUMBER RELOP

/* Keyword token */
%token WHILE

/* * Non-terminals that will hold a string value */
%type <sval> expr condition assignment

/* Operator precedence and associativity for arithmetic expressions */
%left '+' '-'
%left '*' '/'

/* --- Grammar Start Symbol --- */
%start program

%%
/* --- Grammar Rules --- */
program: statements {
            printf("\n--- TAC Generation Complete ---\n");
            YYACCEPT;
         };

statements: /* empty */
          | statements statement
          ;

statement: assignment ';'
         | while_loop
         | expr ';' { gen_tac("print", $1, NULL, NULL); /* For testing */ }
         | error ';' { yyerrok; /* Error recovery */ }
         ;

/* --- Problem 2: While Loop --- */
while_loop: WHILE
            {
                /* Marker 1: Before condition */
                char *l_begin = new_label();
                printf("%s:\n", l_begin);
                push_label(l_begin); /* Push L_begin for the final 'goto' */
            }
            '(' condition ')'
            {
                /* Marker 2: After condition, before body */
                char *l_body = new_label();
                char *l_end = new_label();
                
                /* $4 is the temp var from 'condition' (e.g., t0) */
                printf("if (%s) goto %s\n", $4, l_body);
                printf("goto %s\n", l_end);
                printf("%s:\n", l_body);
                
                push_label(l_end);   /* Push L_end for the end of the loop */
            }
            '{' statements '}'
            {
                /* Marker 3: After body */
                char *l_end = pop_label();
                char *l_begin = pop_label();
                
                printf("goto %s\n", l_begin); /* Loop back to condition */
                printf("%s:\n", l_end);   /* Label for exiting the loop */
            }
            ;

/* Condition rule for the 'while' loop */
condition: expr RELOP expr
           {
               /* Create a new temp to hold the boolean result */
               $$ = new_temp();
               /* Generate TAC for the comparison (e.g., t0 = a < b) */
               gen_tac($$, $1, $3, $2);
           }
           ;

/* Assignment statement */
assignment: ID '=' expr
            {
                /* Generate TAC for assignment (e.g., a = t0) */
                gen_tac($1, $3, NULL, "=");
                $$ = $1;
            }
            ;

/* --- Problem 1: Arithmetic Expressions --- */
expr: expr '+' expr
      {
          $$ = new_temp();
          gen_tac($$, $1, $3, "+"); /* e.g., t0 = t1 + t2 */
      }
    | expr '-' expr
      {
          $$ = new_temp();
          gen_tac($$, $1, $3, "-");
      }
    | expr '*' expr
      {
          $$ = new_temp();
          gen_tac($$, $1, $3, "*");
      }
    | expr '/' expr
      {
          $$ = new_temp();
          gen_tac($$, $1, $3, "/");
      }
    | '(' expr ')'
      {
          $$ = $2; /* No new code, just pass the result up */
      }
    | ID
      {
          $$ = $1; /* The "value" is the variable name itself */
      }
    | NUMBER
      {
          $$ = $1; /* The "value" is the number string */
      }
    ;

%%

int temp_count = 0;
int label_count = 0;

/* Generates a new temporary variable name (e.g., t0, t1, ...) */
char* new_temp() {
    char *temp = (char*)malloc(10 * sizeof(char));
    sprintf(temp, "t%d", temp_count++);
    return temp;
}

/* Generates a new label name (e.g., L0, L1, ...) */
char* new_label() {
    char *label = (char*)malloc(10 * sizeof(char));
    sprintf(label, "L%d", label_count++);
    return label;
}

/* Prints a single Three-Address Code instruction */
void gen_tac(const char *res, const char *arg1, const char *arg2, const char *op) {
    if (strcmp(op, "=") == 0) {
        printf("%s = %s\n", res, arg1);
    } else if (arg2 == NULL) {
        /* For unary operations or print */
        printf("%s %s\n", res, arg1);
    } else {
        /* Standard binary operation */
        printf("%s = %s %s %s\n", res, arg1, op, arg2);
    }
}

int main() {
    printf("Enter code to generate TAC. Press Ctrl+D when done.\n");
    printf("---------------------------------------------------\n");
    if (yyparse() == 0) {
        /* yyparse() returns 0 on success */
    } else {
        printf("\n[FAILURE] Parsing failed.\n");
    }
    return 0;
}

void yyerror(const char *s) {
    fprintf(stderr, "[ERROR] Line %d near '%s': %s\n", yylineno, yytext, s);
}
