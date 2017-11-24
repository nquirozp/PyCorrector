import os
from io import StringIO
from typing import List

from bs4 import UnicodeDammit

from student_data.__managing import find_python_files
from student_data.rubrica import Rubrica
from student_data.student import Student

inverted = {'\\': '/', '/': '\\'}


class Correction:
    def __init__(self, nombre: str = None):
        self.nombre = nombre
        self.students: List[Student] = []
        self.rubrica: Rubrica = Rubrica()
        self.new_file = True

    def new(self, path, nombre: str = None):
        self.nombre = nombre
        self.create_students(path)

    def create_students(self, path):
        self.students = []
        if not Rubrica:
            raise EnvironmentError('No rubrica created')
        filenames = find_python_files(path)
        for filename in filenames:
            with open(path + os.sep + filename, 'rb') as file:
                read = file.read()
                file_data = UnicodeDammit(read, ['utf-8', "latin-1", "iso-8859-1"], )
                self.students.append(Student(filename, file_data.unicode_markup, True))

    def get_student(self, numero: str):
        for student in self.students:
            if student.numero == numero:
                return student

    def add_rubric_item(self, multiplier: int = 1, description=None, comment=None, objective=None):
        self.rubrica.append(multiplier, description, comment, objective)
        for student in self.students:
            student.evaluacion.append()

    def remove_rubric_item(self, index):
        self.rubrica.pop(index)
        for student in self.students:
            student.evaluacion.pop(index)

    def load(self, file):
        self.new_file = False
        if isinstance(file, StringIO):
            data = file.getvalue().split('[MASTER_DIVISION]\n')
        elif hasattr(file, 'read'):
            data = file.read().split('[MASTER_DIVISION]\n')
        else:
            raise TypeError('No StringIO or file given.')
        self.nombre = data[0].strip()
        rubric_data = data[1].splitlines()
        for line in rubric_data:
            item = line.strip().split(';')
            multiplier = int(item[0])
            objective = item[1]
            description = item[2]
            comment = item[3]
            self.rubrica.append(multiplier, description, comment, objective)
        all_student_data = data[2].split('[MASTER_NEW_STUDENT]\n')
        for student in all_student_data:
            student_data = student.strip().split('[STUDENT_DIVISION]\n')
            nombre_archivo = student_data[0].splitlines()[0].rstrip()
            prev_ev = student_data[1]
            archivo = student_data[2].rstrip()
            try:
                runs = student_data[3].rstrip()
            except IndexError:
                runs = None
            self.students.append(Student(nombre_archivo, archivo, new=False, previous_evaluacion=prev_ev, runs=runs))

    def swap(self, nombre: str, rubrica: Rubrica, students: List[Student]):
        self.nombre = nombre
        self.rubrica = rubrica
        self.students = students

    def save(self, file):
        string = ''
        string += f'{self.nombre}\n'
        string += '[MASTER_DIVISION]\n'
        string += f'{self.rubrica}\n'
        string += '[MASTER_DIVISION]\n'
        students = list(map(str, self.students))
        string += '[MASTER_NEW_STUDENT]\n'.join(students)
        file.write(string)


if __name__ == '__main__':
    tarea1 = Correction()
    current_path = os.getcwd()
    tarea1.new('C:\\Users\\nicol\\OneDrive\\Documentos\\Universidad\Ayudantías\IIC1103\\t3\\64')
    print(tarea1.nombre)
