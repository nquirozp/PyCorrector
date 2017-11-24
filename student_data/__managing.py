import glob
import os


def find_python_files(path):
    current_dir = os.getcwd()
    os.chdir(path)
    files = glob.glob('*.py')
    os.chdir(current_dir)
    return files


if __name__ == '__main__':
    pass
