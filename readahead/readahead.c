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

int state_path(char* token, struct readahead_request* req)
{
	size_t len = 0;

	if (strcmp(token, "PATH")) return -1;

	token = strtok(NULL, ":");
	len = strlen(token);
	if (req->path) {
		free(req->path);
		req->path = NULL;
	}
	req->path = malloc(len);
	strcpy(req->path, token);
	return 0;
}

int state_size(char* token, struct readahead_request* req)
{
	if (strcmp(token, "SIZE")) return -1;
	token = strtok(NULL, ":");
	req->size = atol(token);
	return 0;
}

int state_off(char* token, struct readahead_request* req)
{
	if (strcmp(token, "OFFSET")) return -1;
	token = strtok(NULL, ":");
	build_request_off(req, token);
	return 0;
}

int state_end(char* token, struct readahead_request* req)
{
	if (strcmp(token, "END")) return -1;
	dump(req);
	return 0;
}

int (*state[])(char*, struct readahead_request*) = {
	state_path,
	state_size,
	state_off,
	state_end
};

enum state_code { path, size, off, end };

int main(int argc, char **argv)
{
	char* line = NULL, *token, *dup;
	size_t len = 0;
	ssize_t read;
	FILE* fp;
	int i = 0, ret;
	struct readahead_request* request;
	char* readahead_list = argv[1];
	enum state_code cur_state;
	int (* func_state)(char*, struct readahead_request*);

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

	cur_state = path;
	while ((read = getline(&line, &len, fp)) != -1) {
		dup = strdup(line);

		/* remove the tailing "\n" */
		dup[strcspn(dup, "\n")] = 0;

		token = strtok(dup, ":");

		func_state = state[cur_state];
		ret = func_state(token, request);
		if (ret) {
			/* any state fails, roll back to beginning */
			cur_state = path;
		}

		if (++cur_state > end)
			cur_state = path;
	}

	fclose(fp);

	if (request) free(request);
	if (line) free(line);
	exit(EXIT_SUCCESS);
}
