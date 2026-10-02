#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_VARS 50
#define MAX_VAR_NAME_LEN 32
#define MAX_LINES 256
#define MAX_FUNCTIONS 20

typedef struct {
    char name[MAX_VAR_NAME_LEN];
    int val;
} Variable;

typedef struct {
    char name[32];
    int start_line;
    int end_line;
    char params[4][32]; // Up to 4 parameters
    int param_count;
} Function;

Variable variables[MAX_VARS];
char program_lines[MAX_LINES][256];
int total_program_lines = 0;

Function functions[MAX_FUNCTIONS];
int function_count = 0;

int find_var(const char *name) {
    for (int i = 0; i < MAX_VARS; i++) {
        if (strcmp(variables[i].name, name) == 0) {
            return variables[i].val;
        }
    }
    printf("Error: Variable '%s' nahi mili!\n", name);
    return 0;
}

void set_var(const char *name, int val) {
    for (int i = 0; i < MAX_VARS; i++) {
        if (strcmp(variables[i].name, name) == 0) {
            variables[i].val = val;
            return;
        }
    }
    for (int i = 0; i < MAX_VARS; i++) {
        if (variables[i].name[0] == '\0') {
            strcpy(variables[i].name, name);
            variables[i].val = val;
            return;
        }
    }
}

int get_value(const char* token) {
    char* endptr;
    int val = (int)strtol(token, &endptr, 10);
    if (*endptr == '\0') {
        return val;
    }
    return find_var(token);
}

int evaluate_condition(const char* arg1_str, const char* op, const char* arg2_str) {
    int v1 = get_value(arg1_str);
    int v2 = get_value(arg2_str);
    if (strcmp(op, ">") == 0) return (v1 > v2);
    if (strcmp(op, "<") == 0) return (v1 < v2);
    if (strcmp(op, ">=") == 0) return (v1 >= v2);
    if (strcmp(op, "<=") == 0) return (v1 <= v2);
    if (strcmp(op, "==") == 0) return (v1 == v2);
    if (strcmp(op, "!=") == 0) return (v1 != v2);
    return 0;
}

int interpret_block(int start_line, int end_line);
int interpret_line(int line_idx);

int find_block_end(int start_idx) {
    int block_end = start_idx;
    int brace_count = 1;
    while (block_end < total_program_lines && brace_count > 0) {
        char* l = program_lines[block_end];
        while(*l == ' ' || *l == '\t') l++;
        if (strchr(l, '{')) brace_count++;
        if (strchr(l, '}')) brace_count--;
        if (brace_count > 0) block_end++;
    }
    return block_end;
}

void scan_functions() {
    function_count = 0;
    for (int i = 0; i < total_program_lines; i++) {
        char* line = program_lines[i];
        while(*line == ' ' || *line == '\t') line++;
        
        if (strncmp(line, "kaam ", 5) == 0) {
            strcpy(functions[function_count].name, "");
            functions[function_count].param_count = 0;

            char* ptr = line + 5;
            while(*ptr == ' ') ptr++;
            
            int p_idx = 0;
            while(*ptr != '\0' && *ptr != '{' && *ptr != '\r' && *ptr != '\n') {
                char token[32];
                if (sscanf(ptr, "%s", token) == 1) {
                    if (functions[function_count].name[0] == '\0') {
                        strcpy(functions[function_count].name, token);
                    } else {
                        strcpy(functions[function_count].params[p_idx++], token);
                        functions[function_count].param_count++;
                    }
                    ptr += strlen(token);
                    while(*ptr == ' ') ptr++;
                } else {
                    break;
                }
            }

            functions[function_count].start_line = i + 1;
            int end = find_block_end(i + 1);
            functions[function_count].end_line = end - 1;
            function_count++;
            
            i = end;
        }
    }
}

int call_function(const char* name, char* args_str) {
    int f_idx = -1;
    for (int i = 0; i < function_count; i++) {
        if (strcmp(functions[i].name, name) == 0) {
            f_idx = i;
            break;
        }
    }

    if (f_idx == -1) return 0;

    int arg_vals[4] = {0};
    char* ptr = args_str;
    for (int i = 0; i < functions[f_idx].param_count; i++) {
        char arg_token[32];
        if (sscanf(ptr, "%s", arg_token) == 1) {
            arg_vals[i] = get_value(arg_token);
            ptr += strlen(arg_token);
            while(*ptr == ' ') ptr++;
        }
    }

    for (int i = 0; i < functions[f_idx].param_count; i++) {
        set_var(functions[f_idx].params[i], arg_vals[i]);
    }

    interpret_block(functions[f_idx].start_line, functions[f_idx].end_line);
    return 1;
}

int interpret_line(int line_idx) {
    char* line = program_lines[line_idx];
    while(*line == ' ' || *line == '\t' || *line == '\r' || *line == '\n') line++;
    if(*line == '\0' || *line == '#') return line_idx + 1;

    if (strncmp(line, "kaam ", 5) == 0) {
        return find_block_end(line_idx + 1) + 1;
    }

    char cmd[32];
    sscanf(line, "%s", cmd);

    if(strcmp(cmd, "bol") == 0) {
        char arg1[32], op[4], arg2[32];
        int scanned = sscanf(line + 3, "%s %s %s", arg1, op, arg2);

        if (scanned == 3) {
            int v1 = get_value(arg1);
            int v2 = get_value(arg2);
            int res = 0;
            if (strcmp(op, "+") == 0) res = v1 + v2;
            else if (strcmp(op, "-") == 0) res = v1 - v2;
            else if (strcmp(op, "*") == 0) res = v1 * v2;
            else if (strcmp(op, "/") == 0 && v2 != 0) res = v1 / v2;
            printf("%d\n", res);
        } else if (scanned == 1) {
            printf("%d\n", get_value(arg1));
        }
    }
    else if(strcmp(cmd, "rakho") == 0) {
        char* eq = strchr(line, '=');
        if (eq) {
            char lhs[64];
            strncpy(lhs, line + 5, eq - (line + 5));
            lhs[eq - (line + 5)] = '\0';
            
            char* vname = lhs;
            while(*vname == ' ') vname++;
            char* end = vname + strlen(vname) - 1;
            while(end > vname && (*end == ' ' || *end == '\t')) *end-- = '\0';

            char* rhs = eq + 1;
            while(*rhs == ' ' || *rhs == '\t') rhs++;
            char* r_end = rhs + strlen(rhs) - 1;
            while(r_end >= rhs && (*r_end == '\n' || *r_end == '\r' || *r_end == ' ')) *r_end-- = '\0';

            char arg1[32], op[4], arg2[32];
            int scanned = sscanf(rhs, "%s %s %s", arg1, op, arg2);
            int final_val = 0;

            if (scanned == 3) {
                int v1 = get_value(arg1);
                int v2 = get_value(arg2);
                if (strcmp(op, "+") == 0) final_val = v1 + v2;
                else if (strcmp(op, "-") == 0) final_val = v1 - v2;
                else if (strcmp(op, "*") == 0) final_val = v1 * v2;
                else if (strcmp(op, "/") == 0 && v2 != 0) final_val = v1 / v2;
            } else if (scanned == 1) {
                final_val = get_value(arg1);
            }
            set_var(vname, final_val);
        }
    }
    else if(strcmp(cmd, "agar") == 0 || strcmp(cmd, "jab_tak") == 0) {
        char arg1[32], op[4], arg2[32];
        sscanf(line + strlen(cmd), "%s %s %s", arg1, op, arg2);

        int block_start = line_idx + 1;
        int block_end = find_block_end(block_start);

        if (strcmp(cmd, "agar") == 0) {
            if (evaluate_condition(arg1, op, arg2)) {
                interpret_block(block_start, block_end - 1);
            }
        } 
        else if (strcmp(cmd, "jab_tak") == 0) {
            while (evaluate_condition(arg1, op, arg2)) {
                interpret_block(block_start, block_end - 1);
            }
        }
        return block_end + 1;
    }
    else {
        char* args_ptr = line + strlen(cmd);
        while(*args_ptr == ' ') args_ptr++;
        if (call_function(cmd, args_ptr)) {
            return line_idx + 1;
        }
    }

    return line_idx + 1;
}

int interpret_block(int start_line, int end_line) {
    int current = start_line;
    while (current <= end_line) {
        current = interpret_line(current);
    }
    return current;
}

int main(int argc, char* argv[]) {
    if (argc < 2) {
        printf("Istemaal ka tariqa: ./urdulang <file_name.urdu>\n");
        return 1;
    }

    FILE* file = fopen(argv[1], "r");
    if (!file) {
        printf("Error: File khul nahi saki!\n");
        return 1;
    }

    total_program_lines = 0;
    while (fgets(program_lines[total_program_lines], sizeof(program_lines[0]), file)) {
        total_program_lines++;
    }
    fclose(file);

    scan_functions();
    interpret_block(0, total_program_lines - 1);
    return 0;
}