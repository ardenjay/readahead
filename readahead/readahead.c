#define _GNU_SOURCE
#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>

struct readahead_request {
	char* path;
	int size;
	off64_t* offset;
};

void make_request_path(struct readahead_request* request, char* path)
{
	size_t len = 0;

	len = strlen(path);
	if (request->path)
		free(request->path);
	request->path = malloc(len);
	strcpy(request->path, path);
}

void make_request_off(struct readahead_request* request, char* ofs)
{
	char *token = strdup(ofs);
	int nr_token = 0;
	off64_t value = 0;
	int i = 0;

	token = strtok(token, ",");
	while (token != NULL) {
		token = strtok(NULL, ",");
		nr_token++;
	}
	request->size = nr_token;

	if (request->offset)
		free(request->offset);
	request->offset = malloc(sizeof(off64_t) * nr_token);

	token = strdup(ofs);
	i = 0;
	token = strtok(token, ",");
	do {
		value = atol(token);
		request->offset[i++] = value;
		token = strtok(NULL, ",");
	} while (token != NULL);
}

void dump(struct readahead_request* request)
{
	int i;

	printf("dump:");
	printf("PATH - %s\n", request->path);
	for (i = 0; i < request->size; i++)
		printf("%ld ", request->offset[i]);
	printf("\n");
}

int main(int argc, char **argv)
{
	char* line = NULL, *token, *dup;
	size_t len = 0;
	ssize_t read;
	FILE* fp;
	struct readahead_request* request = malloc(sizeof(struct readahead_request));

	fp = fopen("readahead_list", "r");
	if (fp == NULL) {
		printf("Can't open file\n");
		exit(EXIT_FAILURE);
	}

	while ((read = getline(&line, &len, fp)) != -1) {
		dup = strdup(line);
		dup[strcspn(dup, "\n")] = 0;		/* remove the tailing "\n" */
		token = strtok(dup, ":");

		if (strcmp(token, "PATH") == 0) {
			token = strtok(NULL, ":");
			make_request_path(request, token);
		} else if (strcmp(token, "OFFSET") == 0) {
			token = strtok(NULL, ":");
			make_request_off(request, token);
		}

		dump(request);
	}

	fclose(fp);

	if (request) free(request);
	if (line) free(line);
	exit(EXIT_SUCCESS);
}
