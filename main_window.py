import os
import platform
import sys
from decimal import Decimal, getcontext
from io import StringIO
from subprocess import Popen
from time import sleep

from PyQt5 import uic
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QFileDialog, QComboBox, QMessageBox, QShortcut

from file_window import FileDialog
from new_window import NewDialog
from rubric_window import RubricDialog
from student_data import Correction, Student
from student_data.__file import File

mainwindow = uic.loadUiType("mainwindow.ui")
getcontext().prec = 20
inverted = {'\\': '/', '/': '\\'}


class MainWindow(mainwindow[0], mainwindow[1]):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        self.rubric_dialog = None

        self.correcion: Correction = Correction()
        self.current_file: File = None
        self.save_changes_when_quit = False
        self.loaded_path = None
        self.saved_label = QLabel()
        self.saved_label.setText("No hay archivo abierto")

        self.save_shorcut = QShortcut(self)
        self.quit_shorcut = QShortcut(self)
        self.run_shorcut = QShortcut(self)
        self.move_left_shorcut = QShortcut(self)
        self.move_left_student = QShortcut(self)
        self.move_right_shorcut = QShortcut(self)
        self.move_right_student = QShortcut(self)
        self.focus_spin = QShortcut(self)
        self.lose_focus = QShortcut(self)
        self.focus_in_run = QShortcut(self)
        self.focus_in_comment = QShortcut(self)
        self.focus_in_stdin = QShortcut(self)
        self.check_save_run = QShortcut(self)

        self.save_shorcut.setKey(Qt.CTRL + Qt.Key_S)
        self.quit_shorcut.setKey(Qt.CTRL + Qt.Key_Q)
        self.run_shorcut.setKey(Qt.CTRL + Qt.Key_R)
        self.move_left_shorcut.setKey(Qt.CTRL + Qt.Key_Left)
        self.move_right_shorcut.setKey(Qt.CTRL + Qt.Key_Right)
        self.focus_in_run.setKey(Qt.CTRL + Qt.SHIFT + Qt.Key_R)
        self.focus_in_comment.setKey(Qt.CTRL + Qt.SHIFT + Qt.Key_P)
        self.check_save_run.setKey(Qt.CTRL + Qt.Key_G)
        self.lose_focus.setKey(Qt.Key_Escape)
        self.move_left_student.setKey(Qt.CTRL + Qt.SHIFT + Qt.Key_Left)
        self.move_right_student.setKey(Qt.CTRL + Qt.SHIFT + Qt.Key_Right)
        self.focus_spin.setKey(Qt.CTRL + Qt.SHIFT + Qt.Key_S)
        self.focus_in_stdin.setKey(Qt.CTRL + Qt.Key_D)

        self.save_shorcut.activated.connect(self.save)
        self.quit_shorcut.activated.connect(self.quit)
        self.run_shorcut.activated.connect(self.new_run)
        self.move_left_shorcut.activated.connect(
            lambda: move_combo('left', self.sItemCombo))
        self.move_right_shorcut.activated.connect(
            lambda: move_combo('right', self.sItemCombo))
        self.move_left_student.activated.connect(
            lambda: move_combo('left', self.alumnoCombo))
        self.move_right_student.activated.connect(
            lambda: move_combo('right', self.alumnoCombo))
        self.focus_in_run.activated.connect(
            lambda: self.scriptTestingDescTedit.setFocus())
        self.focus_in_comment.activated.connect(
            lambda: self.sItemTEdit.setFocus())
        self.check_save_run.activated.connect(lambda: self.scriptTestingSaveBox.setChecked(False)
        if self.scriptTestingSaveBox.isChecked()
        else self.scriptTestingSaveBox.setChecked(True))
        self.lose_focus.activated.connect(
            lambda: self.remove_focus())
        self.focus_spin.activated.connect(
            lambda: self.scoreSpin.setFocus()
        )
        self.focus_in_stdin.activated.connect(
            lambda: self.scriptTestingStdinTEdit.setFocus()
        )

        self.statusbar.addWidget(self.saved_label)

        self.actionCargar_Correccion.triggered.connect(self.cargar_correccion)
        self.actionEditar_Rubrica.triggered.connect(self.edit_rubrica)
        self.actionNueva_Correccion.triggered.connect(self.new_correcion)
        self.actionEditar_Rubrica.setDisabled(True)
        self.actionGuardar.triggered.connect(self.save)
        self.actionGuardar_Como.triggered.connect(self.save_as)
        self.actionCerrar_Correccion.triggered.connect(self.cerrar_correccion)
        self.actionExportar_Correccion.triggered.connect(self.export)
        self.actionSalir.triggered.connect(self.quit)

        # NEXT AND PREVIOUS BUTTONS CONFIG

        self.sItemNextBtn.clicked.connect(
            lambda: move_combo('right', self.sItemCombo))
        self.sItemPreviousBtn.clicked.connect(
            lambda: move_combo('left', self.sItemCombo))

        self.alumnoNextBtn.clicked.connect(
            lambda: move_combo('right', self.alumnoCombo))
        self.alumnoPreviousBtn.clicked.connect(
            lambda: move_combo('left', self.alumnoCombo))

        self.runsNextBtn.clicked.connect(
            lambda: move_combo('right', self.runsCombo))
        self.runsPreviousBtn.clicked.connect(
            lambda: move_combo('left', self.runsCombo))

        self.rubNextBtn.clicked.connect(
            lambda: move_combo('right', self.rubCombo))
        self.rubPreviousBtn.clicked.connect(
            lambda: move_combo('left', self.rubCombo))

        self.connect_widgets()

    def remove_focus(self):
        try:
            QApplication.focusWidget().clearFocus()
        except AttributeError:
            pass

    def connect_widgets(self):
        self.alumnoCombo.currentIndexChanged.connect(self.load_student)
        self.runsCombo.currentIndexChanged.connect(self.load_run)
        self.rubCombo.currentIndexChanged.connect(self.load_rubrica_item)
        self.sItemCombo.currentIndexChanged.connect(self.load_alumno_eval_item)

        self.scoreSpin.valueChanged.connect(self.calculate_score)
        self.scoreSpin.editingFinished.connect(self.update_eval_score)
        self.sItemTEdit.textChanged.connect(self.change_s_item_comment)
        self.alumnoCommentTEdit.textChanged.connect(
            self.change_student_comment)

        self.viewFBtn.clicked.connect(self.see_file)
        self.scriptTestingRunBtn.clicked.connect(self.new_run)
        self.scriptTestingRunBtn_2.clicked.connect(new_console)
        self.filePushButton.clicked.connect(self.load_sample)
        self.fExplorerIncludeEd.clicked.connect(self.allow_edit_include)
        self.fExplorerInclude.clicked.connect(self.disable_edit_include)
        self.fExplorerNotInclude.clicked.connect(self.disable_edit_not_include)

    def disconnect_widgets(self):
        self.alumnoCombo.currentIndexChanged.disconnect()
        self.runsCombo.currentIndexChanged.disconnect()
        self.rubCombo.currentIndexChanged.disconnect()
        self.sItemCombo.currentIndexChanged.disconnect()

        self.scoreSpin.valueChanged.disconnect()
        self.scoreSpin.editingFinished.disconnect()
        self.sItemTEdit.textChanged.disconnect()
        self.alumnoCommentTEdit.textChanged.disconnect()

        self.viewFBtn.clicked.disconnect()
        self.scriptTestingRunBtn.clicked.disconnect()
        self.scriptTestingRunBtn_2.clicked.disconnect()
        self.filePushButton.clicked.disconnect()
        self.fExplorerIncludeEd.clicked.disconnect()
        self.fExplorerInclude.clicked.disconnect()
        self.fExplorerNotInclude.clicked.disconnect()

    def change_s_item_comment(self):
        student = self.correcion.get_student(self.alumnoCombo.currentText())
        index = self.sItemCombo.currentIndex()
        student.evaluacion[index].comment = self.sItemTEdit.toPlainText()
        self.rename_to_not_save()

    def change_student_comment(self):
        student = self.correcion.students[self.alumnoCombo.currentIndex()]
        student.evaluacion.general_comments = self.alumnoCommentTEdit.toPlainText()
        self.rename_to_not_save()

    def quit(self):
        self.cerrar_correccion()
        sys.exit()

    def check_changes(self):
        print('called')
        if len(self.correcion.students) > 0:
            if self.loaded_path:
                with open(self.loaded_path, encoding='utf-8') as file:
                    file_saved = file.read()
                try:
                    with open('EVAL_DELETE_ME.txt', 'w', encoding='utf-8') as file:
                        self.correcion.save(file)
                except PermissionError:
                    sleep(0.0005)
                    value = self.check_changes()
                    return value
                with open('EVAL_DELETE_ME.txt', 'r', encoding='utf-8') as file:
                    boolean = file.read() == file_saved
                os.remove('EVAL_DELETE_ME.txt')
                return not boolean
        else:
            print('ERROR: CALLING WITHOUT STUDENTS')
            return False

    def rename_to_not_save(self):
        changed = self.check_changes()
        if changed:
            if self.saved_label.text()[-1] != '*':
                self.saved_label.setText(self.saved_label.text() + '*')
                self.setWindowTitle(self.windowTitle() + '*')

    def save(self):
        if self.actionGuardar.isEnabled():
            if not self.loaded_path:
                self.save_as()
            else:
                with open(self.loaded_path, 'w', encoding='utf-8') as file:
                    self.correcion.save(file)
                    if self.saved_label.text()[-1] == '*':
                        self.saved_label.setText(self.saved_label.text()[:-1])
                        self.setWindowTitle(self.windowTitle()[:-1])

    def save_as(self):
        if self.actionGuardar.isEnabled():
            path = QFileDialog.getSaveFileName(caption='Seleccione dónde desea guardar el archivo',
                                               filter='Correccion(*.crcn)')
            with open(path[0], 'w', encoding='utf-8') as file:
                self.loaded_path = path[0]
                self.correcion.save(file)
                previous = self.saved_label.text()
                self.saved_label.setText("Archivo guardado.")
                sleep(3)
                self.saved_label.setText(previous)
                self.rename_to_not_save()

    def update_eval_score(self):
        eval_item = self.correcion.students[self.alumnoCombo.currentIndex(
        )].evaluacion[self.sItemCombo.currentIndex()]
        eval_item.answer = self.scoreSpin.value()
        self.calculate_score()

    def calculate_score(self):
        r_item = self.correcion.rubrica[self.sItemCombo.currentIndex()]
        eval_item = self.correcion.students[self.alumnoCombo.currentIndex(
        )].evaluacion[self.sItemCombo.currentIndex()]
        self.scoreLineEdit.clear()
        self.scoreLineEdit.setText(
            str(Decimal(eval_item.answer * r_item.multiplier / 3)))
        self.rename_to_not_save()

    def refresh(self):
        if self.rubric_dialog.saved:
            self.correcion = self.rubric_dialog.correction_copy
            self.rubric_dialog.destroy()
        self.load_students()
        self.load_student()
        self.load_rubrica_items()
        self.rename_to_not_save()

    def edit_rubrica(self):
        self.rubric_dialog = RubricDialog()
        self.rubric_dialog.load_correcion(self.correcion)
        self.rubric_dialog.rejected.connect(self.refresh)
        self.rubric_dialog.accepted.connect(self.refresh)
        self.rubric_dialog.show()

    def get_current_student(self, student_numero):
        for student in self.correcion.students:
            if student.numero == student_numero:
                return student

    def enable_all(self, boolean=False):
        self.alumnoGroup.setEnabled(boolean)
        self.runsGroup.setEnabled(boolean)
        self.rubGroup.setEnabled(boolean)
        self.scriptTestingGroup.setEnabled(boolean)
        self.runsDescGroup.setEnabled(boolean)
        self.runsStdinGroup.setEnabled(boolean)
        self.runsStdoutGroup.setEnabled(boolean)
        self.runsStderrGroup.setEnabled(boolean)
        self.runsDescTEdit.setEnabled(boolean)
        self.runsStdinTBrowser.setEnabled(boolean)
        self.runsStdoutTBrowser.setEnabled(boolean)
        self.runsStderrTBrowser.setEnabled(boolean)
        self.fExplorerGroup.setEnabled(boolean)

    def clear_and_disable_all(self):
        self.disconnect_widgets()
        self.alumnoCombo.clear()
        self.sItemCombo.clear()
        self.sfName.setText('--')
        self.scoreSpin.setValue(1)
        self.scoreLineEdit.setText('0')
        self.sItemTEdit.setPlainText('')
        self.alumnoCommentTEdit.setPlainText('')
        self.runsCombo.clear()
        self.runsDescTEdit.setPlainText('')
        self.runsStdinTBrowser.setText('')
        self.runsStdoutTBrowser.setText('')
        self.runsStderrTBrowser.setText('')
        self.rubCombo.clear()
        self.rubObjective.setText('--')
        self.rubDescTEdit.setPlainText('')
        self.rubComTEdit.setPlainText('')
        self.fileLineEdit.setText('')
        self.fExplorerTEdit.setPlainText('')
        self.fExplorerTEdit.setReadOnly(True)
        self.fExplorerTEdit.setStyleSheet('background:rgb(234, 234, 234)')
        self.fExplorerIncludeEd.setDown(False)
        self.fExplorerNotInclude.setDown(True)
        self.fExplorerInclude.setDown(False)
        self.scriptTestingName.setText('')
        self.scriptTestingSaveBox.setDown(False)
        self.scriptTestingDescTedit.setPlainText('')
        self.scriptTestingStdinTEdit.setPlainText('')
        self.scriptTestingStdoutTEdit.setPlainText('')
        self.scriptTestingStderrTEdit.setPlainText('')
        self.connect_widgets()
        self.enable_all(False)

    def set_save(self, boolean):
        self.save_changes_when_quit = boolean

    def cerrar_correccion(self):
        self.actionGuardar.setDisabled(True)
        self.actionGuardar_Como.setDisabled(True)
        self.actionEditar_Rubrica.setDisabled(True)
        show = self.check_changes()
        if show or (not self.loaded_path and len(self.correcion.students) > 0):
            quit_no_save = QMessageBox()
            quit_no_save.setIcon(QMessageBox.Warning)
            quit_no_save.setWindowTitle('Advertencia!')
            quit_no_save.setText('Desea guardar antes de salir?')
            quit_no_save.setStandardButtons(QMessageBox.Ok | QMessageBox.No)
            quit_no_save.buttonClicked.connect(
                lambda x: self.set_save(True) if x.text() == 'Ok' else self.set_save(False))
            quit_no_save.exec_()
            if self.save_changes_when_quit:
                self.save()
        self.actionCerrar_Correccion.setDisabled(True)
        self.correcion: Correction = Correction()
        self.clear_and_disable_all()

    def new_correcion(self):
        def refresh():
            self.load_students()
            self.alumnoCombo.setCurrentIndex(0)
            self.load_rubrica_items()
            self.load_runs(self.correcion.students[0])
            self.actionEditar_Rubrica.setDisabled(False)

        new_dialog = NewDialog(self.correcion)
        new_dialog.accepted.connect(refresh)
        new_dialog.exec_()
        if new_dialog.loaded_correctly:
            self.actionGuardar.setDisabled(False)
            self.actionGuardar_Como.setDisabled(False)
            self.enable_all(True)
            show = new_dialog.path.split(inverted[os.sep])[-1]
            self.saved_label.setText(f'Editando archivo {show}')
            self.setWindowTitle(show)
            self.hide()
            self.showMaximized()

    def cargar_correccion(self):
        archivo = QFileDialog.getOpenFileName(
            self, "Seleccione la partida existente", filter='Correccion(*.crcn)')
        if len(archivo[0]) <= 0:
            return
        self.loaded_path = archivo[0]
        self.correcion: Correction = Correction()
        with open(archivo[0], 'r', encoding='utf-8') as file:
            self.correcion.load(file)
        self.load_students()
        self.load_student()
        self.load_rubrica_items()
        self.load_rubrica_item()
        self.load_alumno_eval_item()
        self.load_runs(self.correcion.students[0])
        self.actionEditar_Rubrica.setDisabled(False)
        self.actionGuardar.setDisabled(False)
        self.actionGuardar_Como.setDisabled(False)
        self.enable_all(True)
        show = self.loaded_path.split(inverted[os.sep])[-1]
        self.saved_label.setText(f'Editando archivo {show}')
        self.setWindowTitle(show)
        self.hide()
        self.showMaximized()
        return True

    def load_sample(self):
        archivo = QFileDialog.getOpenFileName(
            self, "Seleccione archivo", filter='Archivos de Texto(*.txt)')
        if len(archivo[0]) == 0:
            return
        with open(archivo[0], 'r', encoding='utf-8') as file:
            nombre = archivo[0].split(inverted[os.sep])[-1]
            self.current_file = File(nombre, file.read())

        self.fileLineEdit.setText(
            '...' + os.sep + self.current_file.nombre.split(inverted[os.sep])[-1])
        with open(archivo[0], 'r', encoding='utf-8') as file:
            self.fExplorerTEdit.setPlainText(file.read())

    def load_students(self):
        self.alumnoCombo.clear()
        self.disconnect_widgets()
        self.alumnoCombo.addItems(
            student.numero for student in self.correcion.students)
        self.connect_widgets()
        self.alumnoCombo.setCurrentIndex(0)
        self.load_student()

    def load_student(self):
        item_n = self.alumnoCombo.currentIndex()
        current_student = self.correcion.students[item_n]
        self.sfName.setText(current_student.nombre_archivo)
        self.disconnect_widgets()
        self.sItemCombo.clear()
        self.sItemCombo.addItems(item.combo_item()
                                 for item in current_student.evaluacion)
        self.connect_widgets()
        self.alumnoCommentTEdit.setPlainText(
            current_student.evaluacion.general_comments)
        self.load_runs(current_student)
        self.load_alumno_eval_item()

    def load_alumno_eval_item(self):
        item_n = self.sItemCombo.currentIndex()
        eval_item = self.correcion.students[self.alumnoCombo.currentIndex(
        )].evaluacion[item_n]
        self.rubCombo.setCurrentIndex(item_n)
        self.load_rubrica_item()
        self.scoreSpin.setValue(eval_item.answer)
        self.calculate_score()
        self.sItemTEdit.setPlainText(eval_item.comment)

    def load_rubrica_items(self):
        self.disconnect_widgets()
        self.rubCombo.clear()
        self.rubCombo.addItems(item.combo_item()
                               for item in self.correcion.rubrica)
        self.connect_widgets()
        self.rubCombo.setCurrentIndex(0)

    def load_rubrica_item(self):
        item_n = self.rubCombo.currentIndex()
        self.rubObjective.setText(self.correcion.rubrica[item_n].objective)
        self.rubDescTEdit.setPlainText(
            self.correcion.rubrica[item_n].description)
        self.rubComTEdit.setPlainText(self.correcion.rubrica[item_n].comment)

    def load_runs(self, student: Student):
        self.disconnect_widgets()
        index = self.runsCombo.currentIndex()
        if index == -1:
            index = 0
        self.runsCombo.clear()
        self.runsDescTEdit.setPlainText('')
        self.runsStdinTBrowser.setText('')
        self.runsStdoutTBrowser.setText('')
        self.runsStderrTBrowser.setText('')
        self.runsCombo.addItems(run.run_name for run in student.runs)
        self.runsCombo.setCurrentIndex(index)
        self.connect_widgets()
        if self.runsCombo.count() > 0:
            self.load_run()

    def load_run(self):
        student = self.get_current_student(str(self.alumnoCombo.currentText()))
        set_run = student.runs[self.runsCombo.currentIndex()]
        self.runsDescTEdit.setPlainText(set_run.run_description)
        self.runsStdinTBrowser.setText(set_run.stdin)
        self.runsStdoutTBrowser.setText(set_run.stdout)
        self.runsStderrTBrowser.setText(set_run.stderr)

    def see_file(self):
        file_dialog = FileDialog(self.get_current_student(
            self.alumnoCombo.currentText()))
        file_dialog.load()
        file_dialog.exec_()

    def allow_edit_include(self):
        self.fExplorerTEdit.setStyleSheet('')
        self.fExplorerCheckLabel_2.setText('[MODO EDICION] Para volver al original, cambiar de opcion a incluir o no '
                                           'incluir')
        self.fExplorerTEdit.setReadOnly(False)

    def disable_edit_include(self):
        self.fExplorerTEdit.setStyleSheet('background:rgb(234, 234, 234)')
        self.fExplorerCheckLabel_2.setText('')
        self.fExplorerTEdit.setReadOnly(True)

    def disable_edit_not_include(self):
        self.fExplorerTEdit.setStyleSheet('background:rgb(234, 234, 234)')
        self.fExplorerCheckLabel_2.setText('')
        self.fExplorerTEdit.setReadOnly(True)

    def export(self):
        dialog = QFileDialog.getSaveFileName(caption='Seleccione donde desea cuardar la exportacion',
                                             filter='CSV (*.csv)')
        with open(dialog[0], 'w', encoding='utf-8') as file:
            for student in self.correcion.students:
                multipliers = self.correcion.rubrica.get_multipliers()
                student_values = student.evaluacion.get_values()
                calc_values = ','.join(f'{str(Decimal(multiplier*answer/3))}'
                                       for multiplier, answer in zip(multipliers, student_values))
                file.write(
                    f'{student.numero},{calc_values},{student.evaluacion}\n')

    def new_run(self):
        if self.scriptTestingGroup.isEnabled():
            student = self.get_current_student(self.alumnoCombo.currentText())
            nombre = str(self.scriptTestingName.text())
            archivo = student.file
            guardar = self.scriptTestingSaveBox.isChecked()
            descripcion = str(self.scriptTestingDescTedit.toPlainText())
            stdin = StringIO()
            stdin.write(str(self.scriptTestingStdinTEdit.toPlainText()))
            kwargs = {'save': guardar, 'file': archivo, 'stdin': stdin}
            if len(nombre) > 0:
                kwargs['run_name'] = nombre
            if len(descripcion) > 0:
                kwargs['run_description'] = descripcion
            if self.fExplorerInclude.isChecked():
                if len(self.fileLineEdit.text()) > 0:
                    kwargs['extra_file'] = self.current_file
            elif self.fExplorerIncludeEd.isChecked():
                if len(self.fileLineEdit.text()) > 0:
                    kwargs['extra_file'] = self.current_file
                    self.current_file.archivo = self.fExplorerTEdit.toPlainText()

            stdout, stderr = student.runs.new_run(**kwargs)
            self.scriptTestingStdoutTEdit.clear()
            self.scriptTestingStderrTEdit.clear()
            self.scriptTestingStdoutTEdit.setPlainText(stdout)
            self.scriptTestingStderrTEdit.setPlainText(stderr)
            self.scriptTestingSaveBox.setChecked(False)
            if guardar:
                self.load_runs(student)
            self.rename_to_not_save()
        else:
            print('CALLING WITHOUT FILE')

    def closeEvent(self, event):
        self.quit()


def new_console():
    directory = QFileDialog.getExistingDirectory()
    curr_dir = os.getcwd()
    os.chdir(directory)
    system = platform.system()
    if system == 'Windows':
        from subprocess import CREATE_NEW_CONSOLE
        Popen('cmd.exe', creationflags=CREATE_NEW_CONSOLE)
    else:
        with open('DELETE_ME.sh', 'w') as file:
            file.write('#!/bin/sh\n'
                       'osascript -e \'tell app \"Terminal\" to do script \"uptime\"')
    os.chdir(curr_dir)


def move_combo(direction: str, combo: QComboBox):
    current_index = combo.currentIndex()
    if direction == 'left':
        if current_index == 0:
            combo.setCurrentIndex(combo.count() - 1)
        else:
            combo.setCurrentIndex(current_index - 1)
    if direction == 'right':
        if current_index == combo.count() - 1:
            combo.setCurrentIndex(0)
        else:
            combo.setCurrentIndex(current_index + 1)


if __name__ == '__main__':
    app = QApplication([])
    form = MainWindow()
    form.showMaximized()
    form.hide()
    form.showMaximized()
    sys.exit(app.exec_())
