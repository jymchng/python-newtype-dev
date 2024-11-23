#ifndef DEBUG_H
#define DEBUG_H

#define ANSI_COLOR_BLUE    "\x1b[34m"
#define ANSI_COLOR_RESET   "\x1b[0m"

#ifdef __DEBUG_PRINT__
#include <stdio.h>
#include <stdarg.h>

#define DEBUG_PRINT(format, ...) \
    fprintf(stderr, "%s[DEBUG] %s:%d %s(): " format "%s\n", \
            ANSI_COLOR_BLUE, __FILE__, __LINE__, __func__, ##__VA_ARGS__, ANSI_COLOR_RESET)
#else
#define DEBUG_PRINT(...)
#endif

#endif // DEBUG_H