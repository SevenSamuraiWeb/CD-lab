%{
#include <stdio.h>
#include <string.h>
#include <ctype.h>

#define MAX_WORDS 1000
#define WORD_LENGTH 50

// Arrays to store words and their counts
char words[MAX_WORDS][WORD_LENGTH];
int count[MAX_WORDS];
int total_words = 0;

void to_lowercase(char *str) {
    for (int i = 0; str[i]; i++)
        str[i] = tolower(str[i]);
}

void add_word(char *word) {
    to_lowercase(word);

    for (int i = 0; i < total_words; i++) {
        if (strcmp(words[i], word) == 0) {
            count[i]++;
            return;
        }
    }

    // Add new word
    if (total_words < MAX_WORDS) {
        strcpy(words[total_words], word);
        count[total_words] = 1;
        total_words++;
    }
}
%}

%%

[a-zA-Z]+     { add_word(yytext); }   // Match words (letters only)
.|\n          { /* Ignore everything else */ }

%%

int main() {
    yylex(); 

    printf("\nWord Frequency Count:\n");
    printf("---------------------\n");

    for (int i = 0; i < total_words; i++)
        printf("%s : %d\n", words[i], count[i]);

    return 0;
}

int yywrap() {
    return 1;
}
