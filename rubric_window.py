import sys
from io import StringIO

from PyQt5 import uic
from PyQt5.QtWidgets import QApplication, QFileDialog

from student_data import Correction

dialog = uic.loadUiType('rubric_dialog.ui')


class RubricDialog(dialog[0], dialog[1]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.itemListWidget.currentItemChanged.connect(self.update_values)
        self.maxSpinBox.valueChanged.connect(self.set_score)
        self.rubDialogDesc.textChanged.connect(self.set_desc)
        self.objective.textChanged.connect(self.set_obj)
        self.rubDialogComments.textChanged.connect(self.set_com)
        self.rubButtonBox.button(self.rubButtonBox.Discard).clicked.connect(self.dismiss)
        self.rubButtonBox.button(self.rubButtonBox.Save).clicked.connect(self.save)
        self.newItem.clicked.connect(self.add_r_item)
        self.delItem.clicked.connect(self.del_r_item)
        self.correction_copy: Correction = None
        self.saveAs.clicked.connect(self.save_self)
        self.saved = False

    def set_obj(self):
        if len(self.correction_copy.rubrica) > 0:
            self.correction_copy.rubrica[self.itemListWidget.currentRow()].objective = self.objective.text()

    def set_score(self):
        if len(self.correction_copy.rubrica) > 0:
            self.correction_copy.rubrica[self.itemListWidget.currentRow()].multiplier = self.maxSpinBox.value()

    def set_desc(self):
        if len(self.correction_copy.rubrica) > 0:
            self.correction_copy.rubrica[
                self.itemListWidget.currentRow()].description = self.rubDialogDesc.toPlainText()

    def set_com(self):
        if len(self.correction_copy.rubrica) > 0:
            self.correction_copy.rubrica[
                self.itemListWidget.currentRow()].comment = self.rubDialogComments.toPlainText()

    def save(self):
        self.saved = True
        self.accept()

    def dismiss(self):
        self.saved = False
        self.reject()

    def load_correcion(self, correction: Correction):
        self.correction_copy = Correction()
        if len(self.correction_copy.rubrica) > 0:
            string_io = StringIO()
            correction.save(string_io)
            self.correction_copy.load(string_io)
            self.itemListWidget.clear()
            self.itemListWidget.addItems(r_item.combo_item() for r_item in self.correction_copy.rubrica)

    def add_r_item(self):
        index = self.itemListWidget.currentRow()
        if index == -1:
            index = self.itemListWidget.count()
            self.correction_copy.rubrica.append()
            for student in self.correction_copy.students:
                student.evaluacion.append()
            self.itemListWidget.insertItem(index, self.correction_copy.rubrica[index].combo_item())
            self.itemListWidget.setCurrentRow(0)
            self.itemListWidget.visualItemRect(self.itemListWidget.item(0))
        else:
            self.correction_copy.rubrica.insert(index)
            for student in self.correction_copy.students:
                student.evaluacion.insert(index)
            for i in range(index, len(self.correction_copy.rubrica) + 1):
                self.itemListWidget.takeItem(index + 1)
            self.itemListWidget.insertItems(index + 1,
                                            [r_item.combo_item() for r_item in
                                             self.correction_copy.rubrica[index + 1:]])
            self.itemListWidget.setCurrentRow(index + 1)
            self.itemListWidget.visualItemRect(self.itemListWidget.item(index + 1))
        self.update_values()

    def del_r_item(self):
        index = self.itemListWidget.currentRow()
        print(index)
        if index == -1:
            index = self.itemListWidget.count() - 1
        for i in range(index, len(self.correction_copy.rubrica) + 1):
            self.itemListWidget.takeItem(index)
        self.correction_copy.rubrica.pop(index)
        self.itemListWidget.insertItems(index,
                                        [r_item.combo_item() for r_item in self.correction_copy.rubrica[index:]])
        print(repr(self.correction_copy.rubrica))
        for student in self.correction_copy.students:
            student.evaluacion.pop(index)
        if self.itemListWidget.count() == 0:
            self.maxSpinBox.setValue(1)
            self.rubDialogDesc.setPlainText('')
            self.rubDialogComments.setPlainText('')
            self.objective.setEnabled(False)
            self.maxSpinBox.setEnabled(False)
            self.rubDialogDesc.setEnabled(False)
            self.rubDialogComments.setEnabled(False)
        else:
            self.update_values()

    def update_values(self):
        if self.itemListWidget.count() > 0:
            self.objective.setEnabled(True)
            self.maxSpinBox.setEnabled(True)
            self.rubDialogDesc.setEnabled(True)
            self.rubDialogComments.setEnabled(True)
        self.maxSpinBox.setValue(self.correction_copy.rubrica[self.itemListWidget.currentRow()].multiplier)
        self.objective.setText(self.correction_copy.rubrica[self.itemListWidget.currentRow()].objective)
        self.rubDialogDesc.setPlainText(self.correction_copy.rubrica[self.itemListWidget.currentRow()].description)
        self.rubDialogComments.setPlainText(self.correction_copy.rubrica[self.itemListWidget.currentRow()].comment)

    def save_self(self):
        path = QFileDialog.getSaveFileName('Exportar rubrica', filter='Rubrica (*.crubr)')
        self.correction_copy.rubrica.save_to_file(path[0])


if __name__ == '__main__':
    app = QApplication([])
    form = RubricDialog()
    form.show()
    sys.exit(app.exec_())
