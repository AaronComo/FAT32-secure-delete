#include<stdio.h>
#include<windows.h>
#include<string.h>
#include<stdbool.h>

void logInfo(bool ret) {
    ret ? printf("【 success 】\n") : printf("【 fail 】\n");
}

void clearFileContent(char *name, DWORD32 begin, DWORD32 size) {
    char temp[10] = "//./";
    int alignedSize = (size + 511) & ~511;
    char buff[alignedSize];
    LPCSTR volume = temp;
    HANDLE handler;
    DWORD dwBytesRead, dwBytesWritten, dwBytesReturned;
    strcat(temp, name);
    memset(buff, 0, alignedSize);

    logInfo(printf("Loading   @ handler.so\t"));
    printf("Openning  @ disk %c\t", name[0]);
    handler = CreateFile(
        volume,                             // lpFileName
        GENERIC_READ | GENERIC_WRITE,       // dwDesiredAccess
        FILE_SHARE_READ | FILE_SHARE_WRITE, // dwShareMode
        NULL,                               // lpSecurityAttributes
        OPEN_EXISTING,                      // dwCreationDisposition
        FILE_ATTRIBUTE_NORMAL,              // dwFlagsAndAttributes
        NULL                                // hTemplateFile
    );
    logInfo(handler != INVALID_HANDLE_VALUE);

    printf("Moving    @ 0x%x\t", begin);
    logInfo(SetFilePointer(
        handler, begin,
        NULL, FILE_BEGIN
    ));

    printf("Locking   @ disk %c\t", name[0]);
    logInfo(DeviceIoControl(
        handler,            // handle to a volume
        FSCTL_LOCK_VOLUME,  // dwIoControlCode
        NULL,               // lpInBuffer
        0,                  // nInBufferSize
        NULL,               // lpOutBuffer
        0,                  // nOutBufferSize
        &dwBytesReturned,   // number of bytes returned
        NULL                // OVERLAPPED structure
    ));

    printf("Erasing   @ 0x%x Bytes ", size);
    logInfo(WriteFile(handler, buff, alignedSize, &dwBytesWritten, NULL));
    // printf("%d bytes written\n", dwBytesWritten);

    printf("Unlocking @ disk %c\t", name[0]);
    logInfo(DeviceIoControl(
        handler,
        FSCTL_UNLOCK_VOLUME,
        NULL, 0, NULL, 0, NULL, NULL
    ));
    CloseHandle(handler);
}
