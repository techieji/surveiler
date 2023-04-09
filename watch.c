#include <Python.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/inotify.h>

#define EVENT_SIZE (sizeof (struct inotify_event))
#define BUF_LEN (1024 * EVENT_SIZE + 16)

void perror_and_exit(int fd, int code, char* s) {
	perror(s);
	close(fd);
	exit(code);
}

int get_fd(void) {
	int fd = inotify_init();
	if (fd < 0)
		perror_and_exit(1, fd, "inotify_init");
	return fd;
}

void add_watch(int fd, char* path) {
	if (inotify_add_watch(fd, path, IN_MODIFY | IN_MOVE | IN_DELETE | IN_CREATE) < 0)
		perror_and_exit(1, fd, "inotify_add_watch");
}

void handle_events(int fd) {
	char buf[BUF_LEN];
	int len = read(fd, buf, BUF_LEN);
	if (len < 0)
		perror_and_exit(1, fd, "read");
	int i = 0;
	struct inotify_event* event;
	while (i < len) {
		event = (struct inotify_event*) &buf[i];
		if (event->mask & IN_CREATE) puts("Create");
		else if (event->mask & IN_MODIFY ) puts("Modify");
		else if (event->mask & IN_DELETE) puts("Delete");
		i += EVENT_SIZE + event->len;
	}
}

int main(void) {
	int fd = get_fd();
	add_watch(fd, "testdirec");
	while (1) {
		handle_events(fd);
	}
	return 0;
}
