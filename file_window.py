from PyQt5 import uic
from student_data import Student

dialog = uic.loadUiType('file_dialog.ui')


class FileDialog(dialog[0], dialog[1]):
    def __init__(self, student: Student = None):
        super().__init__()
        self.student = student
        self.setupUi(self)
        self.accepted.connect(self.close)
        self.pushButton.clicked.connect(self.close)

    def load(self):
        if not self.student:
            raise EnvironmentError('No student given')
        else:
            self.textBrowser.setText(self.student.file)
            self.label.setText(self.student.nombre_archivo)


if __name__ == '__main__':
    pass
