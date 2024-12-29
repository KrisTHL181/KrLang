import os
import sys


def count_py_lines(directory: str) -> int:
    total_lines = 0

    # 遍历目录下的所有文件和子目录
    for root, _dirs, files in os.walk(directory):
        for file in files:
            # 检查文件是否以.py结尾
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                with open(file_path, encoding="utf-8") as f:
                    for _line in f:
                        total_lines += 1

    return total_lines


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: python {__file__} <directory>")
    else:
        directory = sys.argv[1]
        total_lines = count_py_lines(directory)
        print(f"Total lines in .py files: {total_lines}")
