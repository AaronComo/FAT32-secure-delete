import os
import sys
import time
from pprint import pprint
from FAT.FAT32 import FAT32


def doc():
    print("\n============== FAT32 Secure Delete ==============")
    print("➤ Author: AaronComo")
    print("➤ Note: Please run this program as Administrator!")
    print("➤ Options: ")
    print("  1. Get clusters")
    print("  2. Secure delete")
    print("  3. Exit")
    print("==================================================\n")

if __name__ == "__main__":
    while True:
        platform = sys.platform
        os.system("cls") if platform.find("win") != -1 else os.system("clear")
        doc()
        option = input("Enter your choice: ")
        if option in ["1", "2"]:
            fat32 = FAT32(input("Please enter the file path: "))
            ret = fat32.get_cluster_dict()
            if not ret:
                del fat32
                input("Press ENTER to continue...")
                continue
            print("Clusters: ")
            pprint(ret)
            if option == "2":
                fat32.secure_delete()
            del fat32
            input("Press ENTER to continue...")
        elif option == "3":
            exit(0)
        else:
            print("Invalid option!")
            time.sleep(1)
