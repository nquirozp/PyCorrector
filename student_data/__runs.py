from io import StringIO
from typing import List

from student_data.__file import File
from student_data.__run import _Run


class Runs:
    def __init__(self):
        self.index = 0
        self.run_counter = 0
        self.runs: List[_Run] = []

    def new_run(self, save: bool, file: str, stdin: StringIO,
                run_name: str = None, run_description: str = None, extra_file: File = None):
        self.run_counter += 1
        if not run_name:
            name = f'RUN-{self.run_counter}'
        else:
            name = run_name
        argums = [name]
        if run_description:
            argums.append(run_description)
        new_run = _Run(*argums)

        if save:
            self.runs.append(new_run)
        kwargs = {'file': file, 'stdin': stdin}
        if extra_file:
            kwargs['extra_file'] = extra_file
        return new_run.run(**kwargs)

    def add_run(self, run_name, run_description, stdin, stdout, stderr):
        self.runs.append(_Run(run_name, run_description, stdin, stdout, stderr))
        self.run_counter += 1

    def __getitem__(self, item):
        return self.runs[item]

    def __iter__(self):
        return iter(self.runs)

    def __len__(self):
        return len(self.runs)

    def __str__(self):
        return '[STUDENT_NEW_RUN]\n'.join(list(map(str, self)))
