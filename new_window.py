import os

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFileDialog

from rubric_window import RubricDialog
from student_data import Correction

inverted = {'\\': '/', '/': '\\'}
dialog = uic.loadUiType('new_dialog.ui')


class NewDialog(dialog[0], dialog[1]):
    def __init__(self, correction: Correction):
        super().__init__()
        self.correction = correction
        self.setupUi(self)
        self.setWindowFlags(Qt.Window)
        self.path = None
        self.loaded_correctly = False
        self.setWindowModality(Qt.WindowModal)
        self.lineEdit.textChanged.connect(self.update_name)
        self.lineEdit_2.textChanged.connect(self.enable_rubrica)
        self.buttonBox.button(self.buttonBox.Ok).clicked.connect(self.check)
        self.rubric_dialog = RubricDialog()
        self.rubric_dialog.accepted.connect(self.refresh)
        self.pushButton.clicked.connect(self.load_files)
        self.pushButton_2.clicked.connect(self.show_rubrica)
        self.pushButton_3.clicked.connect(self.cargar_rubrica)

    def update_name(self):
        if len(self.lineEdit.text()) > 0:
            self.correction.nombre = self.lineEdit.text()

    def load_files(self):
        self.path = QFileDialog.getExistingDirectory(caption='Seleccione la carpeta de tareas')
        self.correction.new(self.path, self.lineEdit.text())
        self.lineEdit_2.setText('...' + os.sep + self.path.split(inverted[os.sep])[-1])
        print(self.correction.students)

    def cargar_rubrica(self):
        path = QFileDialog.getOpenFileName(caption='Seleccione rubrica a cargar', filter='Rubrica (*.crubr)')
        if len(path[0]) > 0:
            self.correction.rubrica.load_from_crubr(path[0])
            for student in self.correction.students:
                for _ in range(len(self.correction.rubrica)):
                    student.evaluacion.append()
            self.loaded_correctly = True
        self.refresh()

    def show_rubrica(self):
        self.rubric_dialog.load_correcion(self.correction)
        self.rubric_dialog.exec_()

    def check(self):
        if len(self.lineEdit.text()) > 0:
            self.accept()
        else:
            self.label_3.setText('Debes ingresar algo!')

    def enable_rubrica(self):
        if len(self.correction.students) > 0:
            self.pushButton_2.setEnabled(True)
            self.pushButton_3.setEnabled(True)

    def refresh(self):
        if len(self.correction.rubrica) > 0:
            self.loaded_correctly = True
            self.buttonBox.setEnabled(True)
