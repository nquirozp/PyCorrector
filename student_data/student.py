import os

from student_data.__evaluacion import Evaluacion
from student_data.__runs import Runs


class Student:
    def __init__(self,
                 nombre_archivo: str,
                 archivo: str,
                 new: bool = True,
                 previous_evaluacion: str = None,
                 runs: str = None):
        self.numero = nombre_archivo.split('_')[0].split(os.sep)[-1]
        self.nombre_archivo = nombre_archivo
        self.file = archivo.strip()
        self.runs: Runs = Runs()
        self.run_counter = 0
        if new:
            if previous_evaluacion:
                raise AttributeError('Previous evaluation passed to new student')
            else:
                self.evaluacion = Evaluacion()
        else:
            if not previous_evaluacion:
                raise AttributeError('Creating previous evaluation without data')
            else:
                datos = previous_evaluacion.splitlines()
                self.evaluacion = Evaluacion()
                for numero, dato in enumerate(datos[:-1], 1):
                    answer = int(dato.split(';')[0])
                    comment = dato.split(';')[1]
                    self.evaluacion.append(answer, comment)
                self.evaluacion.general_comments = datos[-1]
                if runs:
                    runs = runs.split('[STUDENT_NEW_RUN]\n')
                    for run in runs:
                        name, description, stdin, stdout, stderr = run.split('[STUDENT_RUN_DIVISION]\n')
                        self.runs.add_run(name.strip(), description.strip(), stdin.strip(), stdout.strip(),
                                          stderr.strip())

    def get_comentarios(self):
        return str(self.evaluacion)

    def __str__(self):
        string = ''
        string += f'{self.nombre_archivo}\n'
        string += '[STUDENT_DIVISION]\n'
        for item in self.evaluacion:
            string += f'{item}\n'
        string += f'{self.evaluacion.general_comments}\n'
        string += f'[STUDENT_DIVISION]\n{self.file}'
        if len(self.runs) > 0:
            string += f'\n[STUDENT_DIVISION]\n'
            string += f'{self.runs}'
        return string
