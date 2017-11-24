import os
import subprocess
from io import StringIO

from bs4 import UnicodeDammit

from student_data.__file import File


class _Run:
    def __init__(self, run_name, run_description='', stdin: str = None, stdout: str = None, stderr: str = None):
        self.run_name = run_name
        self.run_description = run_description
        self.stdin = stdin
        self.stdout = stdout
        self.stderr = stderr

    def run(self, file: str, stdin: StringIO, extra_file: File = None):
        pyfile = open('runner.py', 'w', encoding='utf-8')
        pyfile.write(file)
        pyfile.close()

        if extra_file:
            samplefile = open(extra_file.nombre, 'w', encoding='utf-8')
            samplefile.write(extra_file.archivo)
            samplefile.close()

        pipe = subprocess.Popen(['python', 'runner.py'],
                                stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        stdout, stderr = pipe.communicate(bytes(stdin.getvalue(), 'utf-8'))
        pipe.kill()

        os.remove('runner.py')
        if extra_file:
            os.remove(extra_file.nombre.split(os.sep)[-1])
        stdout = UnicodeDammit(stdout, ['utf-8', "latin-1", "iso-8859-1"]).unicode_markup
        stderr = UnicodeDammit(stderr, ['utf-8', "latin-1", "iso-8859-1"]).unicode_markup
        self.stdout = stdout
        self.stderr = stderr
        self.stdin = UnicodeDammit(stdin.getvalue(), ['utf-8', "latin-1", "iso-8859-1"]).unicode_markup
        return stdout, stderr

    def __str__(self):
        return f'{self.run_name}\n' \
               f'[STUDENT_RUN_DIVISION]\n' \
               f'{self.run_description}\n' \
               f'[STUDENT_RUN_DIVISION]\n' \
               f'{self.stdin}\n' \
               f'[STUDENT_RUN_DIVISION]\n' \
               f'{self.stdout}\n' \
               f'[STUDENT_RUN_DIVISION]\n' \
               f'{self.stderr}'
