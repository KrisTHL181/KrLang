import os
import shutil
import sys


def delete_files(directory, delete_name, delete_files: bool = False):
    for root, dirs, files in os.walk(directory, topdown=False):
        if delete_files:
            for name in files:
                if name in delete_name:
                    file_path = os.path.join(root, name)
                    os.remove(file_path)
                    print(f"Deleted file: {file_path}")
        for name in dirs:
            if name in delete_name:
                dir_path = os.path.join(root, name)
                shutil.rmtree(dir_path)
                print(f"Deleted directory: {dir_path}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"Usage: python {__file__} <directory> <names>")
    else:
        directory = sys.argv[1]
        delete_names = sys.argv[2:]
        print(f"Remove directory: {directory}, Remove names: {', '.join(delete_names)}\n")
        delete_files(directory, delete_names)
