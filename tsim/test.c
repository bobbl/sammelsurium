#include <stdio.h>
#include <stdlib.h>

int main()
{
    puts("Hello world!");

    char *p = malloc(32*1024);
    if (p==0) printf("Out of memory\n");
    else {
        free(p);
        printf("malloc() test passed.\n");
    }

    return 0;
}

