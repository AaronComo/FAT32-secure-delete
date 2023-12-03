import os
import ctypes


class FAT32:
    class DBR:
        def __init__(self, reader, to_int):
            raw = reader.read(512).hex()
            self.bytes_per_sector = to_int(raw[22:26])
            self.sectors_per_cluster = to_int(raw[26:28])
            self.reserved_sectors = to_int(raw[28:32])
            self.number_of_fat_table = to_int(raw[32:34])
            self.sectors_per_fat_table = to_int(raw[72:80])
            self.root_cluster = to_int(raw[88:96])
            self.root_dir_sector = (
                self.reserved_sectors
                + self.number_of_fat_table * self.sectors_per_fat_table
            )

    def __init__(self, file: str):
        """
        Initialize a FAT32 file system descriptor using the given file.
        - file: path/to/your/file. e.g. E:/directory/file.txt
        """
        self.file = file
        self.file_list = FAT32.handle_path(file)
        self.unicode_name = [
            self.file_list[i].encode().hex() for i in range(len(self.file_list))
        ]
        self.file_list[-1], self.suffix = self.file_list[-1].split(".")  # remove suffix
        self.reader = open(rf"//./{self.file_list[0]}", mode="+rb")
        self.DBR = self.DBR(self.reader, FAT32.to_int)

    def __del__(self):
        self.reader.close()

    def handle_path(path: str) -> list:
        return path.replace("\\", "/").replace("//", "/").split("/")

    def to_int(x: str) -> int:
        return int.from_bytes(bytes.fromhex(x), byteorder="little", signed=False)

    def FAT_read(FAT: bytes, p: int) -> list:
        l = [p]
        while True:
            p = p << 3
            p = FAT32.to_int(FAT[p : p + 8])
            if p == FAT32.to_int("ffffff0f"):
                break
            l.append(p)
        return l

    def get_cluster_list(self, return_size=False):
        size = list()
        cluster_list = [[self.DBR.root_cluster]]  # search from root
        self.reader.seek(self.DBR.reserved_sectors * self.DBR.bytes_per_sector)
        FAT_raw = self.reader.read(
            self.DBR.sectors_per_cluster * self.DBR.bytes_per_sector
        ).hex()

        for i in range(1, len(self.file_list)):
            name = (
                self.file_list[i].upper().encode().hex()
            )  # use uppercase for searching
            self.reader.seek(
                (
                    self.DBR.root_dir_sector
                    + (cluster_list[-1][0] - self.DBR.root_cluster)
                    * self.DBR.sectors_per_cluster
                )
                * self.DBR.bytes_per_sector
            )
            sector_raw = self.reader.read(
                self.DBR.sectors_per_cluster * self.DBR.bytes_per_sector
            ).hex()
            index = -1
            if len(name) < 17:
                index = sector_raw.find(name)
            else:
                # long filename, ~i in [~1, ~5]
                # Reverse concatenation of file name
                bias = [1, 3, 5, 7, 9, 14, 16, 18, 20, 22, 24, 28, 30]
                for n in range(1, 6):
                    index = sector_raw.find(name[:12] + bytes(f"~{n}", "utf-8").hex())
                    temp = str()
                    for j in range(int(len(self.unicode_name[i]) / 26) + 1):
                        for k in range(13):
                            begin = index - ((j + 1) << 6) + (bias[k] << 1)
                            temp += sector_raw[begin : begin + 2]
                    if temp[: len(self.unicode_name[i])] == self.unicode_name[i]:
                        break
            if index == -1:
                print("Cannot find a valid file.")
                return None

            first_cluster = (
                FAT32.to_int(sector_raw[index + 40 : index + 44]) << 16
            ) + FAT32.to_int(sector_raw[index + 52 : index + 56])
            cluster_list.append(FAT32.FAT_read(FAT_raw, first_cluster))
            size.append(FAT32.to_int(sector_raw[index + 56 : index + 64]))

        return (cluster_list, size[-1]) if return_size else cluster_list

    def get_cluster_dict(self) -> dict:
        file_list = self.file_list.copy()
        file_list[-1] += f".{self.suffix}"
        l = self.get_cluster_list()
        return dict(zip(file_list, l)) if l else None

    def secure_delete(self):
        file_list, size = self.get_cluster_list(return_size=True)
        begin = (
            self.DBR.root_dir_sector
            + (file_list[-1][0] - self.DBR.root_cluster) * self.DBR.sectors_per_cluster
        ) * self.DBR.bytes_per_sector
        self.reader.close()
        print(f"Securely deleting '{self.file}'")
        lib = ctypes.CDLL("lib/handler.so")
        lib.clearFileContent("E:".encode("utf-8"), begin, size)
        os.remove(self.file)
        print("The file has been deleted.")
