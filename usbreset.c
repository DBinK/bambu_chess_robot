#include <stdio.h>
#include <fcntl.h>
#include <unistd.h>
#include <linux/usbdevice_fs.h>
#include <sys/ioctl.h>

int main(int argc, char **argv) {
    const char *filename;
    int fd;
    int rc;

    if (argc != 2) {
        fprintf(stderr, "Usage: usbreset device-filename\n");
        return 1;
    }
    filename = argv[1];
    fd = open(filename, O_WRONLY);
    if (fd < 0) {
        perror("Error opening output file");
        return 1;
    }

    printf("Resetting USB device %s\n", filename);
    rc = ioctl(fd, USBDEVFS_RESET, 0);
    if (rc < 0) {
        perror("Error in ioctl");
        return 1;
    }
    printf("Reset successful\n");
    close(fd);
    return 0;
}

// 3. 找到设备对应的 /dev/bus/usb 设备文件
// 根据 lsusb 的 Bus 和 Device 信息，设备路径形如：

// /dev/bus/usb/BBB/DDD
// 其中 BBB 是总线号（Bus）三位数，DDD 是设备号（Device）三位数。

// 比如 Bus 001 Device 005，对应 /dev/bus/usb/001/005

// 4. 执行重置
// bash
// sudo ./usbreset /dev/bus/usb/001/005
// 执行后，如果成功，摄像头就相当于被断开重连了。