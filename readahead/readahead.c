#define _GNU_SOURCE
#include <stdio.h>
#include <fcntl.h>
#include <string.h>
#include <stdlib.h>
#include <errno.h>

struct readahead_request {
	char* path;
	int size;
	off64_t* offset;
};

void build_request_path(struct readahead_request* request, char* path)
{
	size_t len = 0;

	len = strlen(path);
	if (request->path) {
		free(request->path);
		request->path = NULL;
	}
	request->path = malloc(len);
	strcpy(request->path, path);
}

void build_request_off(struct readahead_request* request, char* ofs)
{
	char *token = strdup(ofs);
	off64_t value = 0;
	int i = 0;

	if (request->offset) {
		free(request->offset);
		request->offset = NULL;
	}
	request->offset = malloc(sizeof(off64_t) * request->size);

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
	printf("Num: %d\n", request->size);
	for (i = 0; i < request->size; i++)
		printf("%jd ", request->offset[i]);
	printf("\n");
}

int make_request(struct readahead_request* request)
{
	int fd, i;
	ssize_t ret;

	fd = open(request->path, O_RDONLY);
	if (fd < 0) {
		printf("open %s: %s\n", request->path, strerror(errno));
		goto fail;
	}

	for (i = 0; i < request->size; i++) {
		ret = readahead(fd, request->offset[i], 1);
		if (ret)
			printf("%s fails: %s\n", __func__, strerror(errno));
	}
fail:
	return -1;
}

int main(int argc, char **argv)
{
	char* line = NULL, *token, *dup;
	size_t len = 0;
	ssize_t read;
	FILE* fp;
	int i = 0;
	struct readahead_request* request;
	char* readahead_list = argv[1];

	if (argc < 2) {
		printf("Use: readahead list\n");
		exit(EXIT_FAILURE);
	}

	fp = fopen(readahead_list, "r");
	if (fp == NULL) {
		printf("Can't open readahead_list: %s\n", strerror(errno));
		exit(EXIT_FAILURE);
	}

	request = malloc(sizeof(struct readahead_request));
	memset(request, 0, sizeof(*request));

	while ((read = getline(&line, &len, fp)) != -1) {
		dup = strdup(line);
		dup[strcspn(dup, "\n")] = 0;		/* remove the tailing "\n" */
		token = strtok(dup, ":");

		if (strcmp(token, "PATH") == 0) {
			token = strtok(NULL, ":");
			build_request_path(request, token);
		} else if (strcmp(token, "SIZE") == 0) {
			token = strtok(NULL, ":");
			request->size = atol(token);
		} else if (strcmp(token, "OFFSET") == 0) {
			token = strtok(NULL, ":");
			build_request_off(request, token);
		}

		if ((++i % 3) == 0) {
			dump(request);
			make_request(request);
		}
	}

	fclose(fp);

	if (request) free(request);
	if (line) free(line);
	exit(EXIT_SUCCESS);
}
