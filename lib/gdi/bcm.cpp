/*
  Interface to the Dreambox dm800/dm8000 proprietary accel interface.
*/

#include <stdio.h>
#include <stdlib.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/fb.h>
#include <sys/mman.h>
#include <sys/ioctl.h>

#define FBIO_ACCEL  0x23

static unsigned int displaylist[1024];
static int ptr;

#define P(x, y) do { displaylist[ptr++] = x; displaylist[ptr++] = y; } while (0)
#define C(x) P(x, 0)

static int fb_fd;
static int exec_list(void);

int bcm_accel_init(void)
{
	fb_fd = open("/dev/fb/0", O_RDWR);
	if (fb_fd < 0)
	{
		perror("/dev/fb/0");
		return 1;
	}
	if (exec_list())
	{
		fprintf(stderr, "BCM accel interface not available - %m\n");
		close(fb_fd);
		return 1;
	}
	return 0;
}

void bcm_accel_close(void)
{
	close(fb_fd);
}

static int exec_list(void)
{
	int ret;
	struct
	{
		void *ptr;
		int len;
	} l;

	l.ptr = displaylist;
	l.len = ptr;
	ret = ioctl(fb_fd, FBIO_ACCEL, &l);
	ptr = 0;
	return ret;
}

void bcm_accel_blit(
		int src_addr, int src_width, int src_height, int src_stride, int src_format,
		int dst_addr, int dst_width, int dst_height, int dst_stride,
		int src_x, int src_y, int width, int height,
		int dst_x, int dst_y, int dwidth, int dheight,
		int pal_addr)
{
	C(0x43); // reset source
	C(0x53); // reset dest
	C(0x5b);  // reset pattern
	C(0x67); // reset blend
	C(0x75); // reset output

	P(0x0, src_addr); // set source addr
	P(0x1, src_stride);  // set source pitch
	P(0x2, src_width); // source width
	P(0x3, src_height); // height
	switch (src_format)
	{
	case 0:
		P(0x4, 0x7e48888); // format: ARGB 8888
		break;
	case 1:
		P(0x4, 0x12e40008); // indexed 8bit
		P(0x78, 256);
		P(0x79, pal_addr);
		P(0x7a, 0x7e48888);
		break;
	}

	C(0x5); // set source surface (based on last parameters)

	P(0x2e, src_x); // define  rect
	P(0x2f, src_y);
	P(0x30, width);
	P(0x31, height);

	C(0x32); // set this rect as source rect

	P(0x0, dst_addr); // prepare output surface
	P(0x1, dst_stride);
	P(0x2, dst_width);
	P(0x3, dst_height);
	P(0x4, 0x7e48888);
	
	C(0x69); // set output surface
	
	P(0x2e, dst_x); // prepare output rect
	P(0x2f, dst_y);
	P(0x30, dwidth);
	P(0x31, dheight);

	C(0x6e); // set this rect as output rect

	C(0x77);  // do it

	exec_list();
}

void bcm_accel_fill(
		int dst_addr, int dst_width, int dst_height, int dst_stride,
		int x, int y, int width, int height,
		unsigned long color)
{
//	printf("unimplemented bcm_accel_fill\n");
}

