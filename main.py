import traceback

from PyQt6.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, \
	QGridLayout, QPushButton, QMainWindow, QTableWidget, QTableWidgetItem, \
	QDialog, QVBoxLayout, QComboBox, QToolBar, QStatusBar, QMessageBox
from PyQt6.QtGui import QAction, QIcon
import sys
import sqlite3


class MainWindow(QMainWindow):
	def __init__(self):
		super().__init__()
		# Add title
		self.setWindowTitle("Student Management System")

		# Set a minimum size for the main window
		self.setMinimumSize(800, 600)

		# Add menu bar
		file_menu_item = self.menuBar().addMenu("&File")
		help_menu_item = self.menuBar().addMenu("&Help")
		edit_menu_item = self.menuBar().addMenu("&Edit")

		# Add actions for each menu bar
		# self will connect QAction to the actual class (MainWindow)
		add_student_action = QAction(QIcon("icons/add.png"), "Add Student", self)
		add_student_action.triggered.connect(self.insert)
		file_menu_item.addAction(add_student_action)

		about_action = QAction("About", self)
		help_menu_item.addAction(about_action)
		# about_action.setMenuRole(QAction.MenuRole.NoRole) ---> If help item doesn't come up
		about_action.triggered.connect(self.about)

		search_action = QAction(QIcon("icons/search.png"), "Search", self)
		edit_menu_item.addAction(search_action)
		edit_menu_item.triggered.connect(self.search)

		# Add table widget
		self.table = QTableWidget()
		self.table.setColumnCount(4)
		self.table.setHorizontalHeaderLabels(("ID", "Name", "Course", "Mobile"))
		self.table.verticalHeader().setVisible(False) # It hides the built-in id columns
		self.setCentralWidget(self.table)

		# Create toolbar and add elements
		toolbar = QToolBar()
		toolbar.setMovable(True)
		self.addToolBar(toolbar) # self == main_window object
		toolbar.addAction(add_student_action)
		toolbar.addAction(search_action)

		# Create status bar and add status bar elements
		self.statusbar = QStatusBar()
		self.setStatusBar(self.statusbar)

		# Detect a cell click
		self.table.cellClicked.connect(self.cell_clicked)

	def cell_clicked(self):
		edit_button = QPushButton("Edit Record")
		edit_button.clicked.connect(self.edit)

		delete_button = QPushButton("Delete Record")
		delete_button.clicked.connect(self.delete)

		children = self.findChildren(QPushButton)
		if children:
			for child in children:
				self.statusbar.removeWidget(child)

		self.statusbar.addWidget(edit_button)
		self.statusbar.addWidget(delete_button)

	def load_data(self):
		connection = sqlite3.connect("database.db")
		result = connection.execute("SELECT * FROM students") # Connection will create cursor everytime. Since we have only
		# one operation, it's okay to use connection instead of cursor
		# print(list(result)) ----> prints out a list of tuples
		self.table.setRowCount(0)
		for row_number, row_data in enumerate(result):
			self.table.insertRow(row_number)
			for column_number, data in enumerate(row_data):
				self.table.setItem(row_number, column_number, QTableWidgetItem(str(data)))
		connection.close()

	def insert(self):
		dialog = InsertDialog()
		dialog.exec()

	def search(self):
		dialog = SearchDialog()
		dialog.exec()

	def edit(self):
		dialog = EditDialog(self)
		dialog.exec()

	def delete(self):
			dialog = DeleteDialog(self)
			dialog.exec()

	def about(self):
		dialog = AboutDialog()
		dialog.exec()


class AboutDialog(QMessageBox):
	def __init__(self):
		super().__init__()
		self.setWindowTitle("About")

		content = f"""
		This app was created during the course "The Python Mega Course"
		Feel free to modify and reuse this app
		"""
		self.setText(content)


class EditDialog(QDialog):
	def __init__(self, main_window):
		super().__init__()

		# Add a title
		self.setWindowTitle("Update Student Data")

		self.main_window = main_window

		# Set fixed width and height
		self.setFixedWidth(300)
		self.setFixedHeight(300)

		layout = QVBoxLayout()

		# Get index of the selected row
		index = self.main_window.table.currentRow()

		# Get the student name from selected row
		student_name = main_window.table.item(index, 1).text()

		# Get id from selected row
		self.student_id = main_window.table.item(index, 0).text()

		# Add student name widget
		self.student_name = QLineEdit(student_name)
		self.student_name.setPlaceholderText("Name")
		layout.addWidget(self.student_name)

		# Add combo box of courses
		course_name = main_window.table.item(index, 2).text()
		self.course_name = QComboBox()
		courses = ["Biology", "Math", "Astronomy", "Physics"]
		self.course_name.addItems(courses)
		self.course_name.setCurrentText(course_name)
		layout.addWidget(self.course_name)

		# Add mobile widget
		mobile = main_window.table.item(index, 3).text()
		self.mobile = QLineEdit(mobile)
		self.mobile.setPlaceholderText("Mobile")
		layout.addWidget(self.mobile)

		# Add submit button
		update_button = QPushButton("Update")
		update_button.clicked.connect(self.update_student)
		layout.addWidget(update_button)

		self.setLayout(layout)

	def update_student(self):
		connection = sqlite3.connect("database.db")
		cursor = connection.cursor()
		cursor.execute("UPDATE students SET name = ?, course = ?, mobile = ? WHERE id = ?",
					   (self.student_name.text(),
						self.course_name.itemText(self.course_name.currentIndex()),
						self.mobile.text(),
						self.student_id))
		connection.commit()
		cursor.close()
		connection.close()
		# Refresh the table
		main_window.load_data()

	def cell_clicked(self):
		edit_button = QPushButton("Edit Record")
		edit_button.clicked.connect(self.edit)

		delete_button = QPushButton("Delete Record")
		delete_button.clicked.connect(self.delete)

		children = self.findChildren(QPushButton)
		if children:
			for child in children:
				self.statusbar.removeWidget(child)

		self.statusbar.addWidget(edit_button)
		self.statusbar.addWidget(delete_button)


class DeleteDialog(QDialog):
	def __init__(self, main_window):
		super().__init__()

		# Add a title
		self.setWindowTitle("Delete Student Data")

		self.main_window = main_window

		layout = QGridLayout()

		confirmation = QLabel("Are you sure you want to delete?")
		yes = QPushButton("Yes")
		no = QPushButton("No")

		# Add widgets
		layout.addWidget(confirmation, 0, 0, 1, 2)
		layout.addWidget(yes, 1, 0)
		layout.addWidget(no, 1, 1)

		self.setLayout(layout)

		yes.clicked.connect(self.delete_student)

	def delete_student(self):
		# Get index from the selected row
		index = self.main_window.table.currentRow()

		# Get id from the selected row
		student_id = main_window.table.item(index, 0).text()

		connection = sqlite3.connect("database.db")
		cursor = connection.cursor()
		cursor.execute("DELETE FROM students WHERE id = ?", (student_id, ))
		connection.commit()
		cursor.close()
		connection.close()

		# Refresh the main window
		main_window.load_data()

		self.close()

		confirmation_widget = QMessageBox()
		confirmation_widget.setWindowTitle("Success")
		confirmation_widget.setText("The record was deleted successfully!")
		confirmation_widget.exec()


class InsertDialog(QDialog):
	def __init__(self):
		super().__init__()

		# Add a title
		self.setWindowTitle("Insert Student Data")

		# Set fixed width and height
		self.setFixedWidth(300)
		self.setFixedHeight(300)

		layout = QVBoxLayout()

		# Add student name widget
		self.student_name = QLineEdit()
		self.student_name.setPlaceholderText("Name")
		layout.addWidget(self.student_name)

		# Add combo box of courses
		self.course_name = QComboBox()
		courses = ["Biology", "Math", "Astronomy", "Physics"]
		self.course_name.addItems(courses)
		self.course_name.setPlaceholderText("Course")
		layout.addWidget(self.course_name)

		# Add mobile widget
		self.mobile = QLineEdit()
		self.mobile.setPlaceholderText("Mobile")
		layout.addWidget(self.mobile)

		# Add submit button
		submit_button = QPushButton("Register")
		submit_button.clicked.connect(self.add_student)
		layout.addWidget(submit_button)

		self.setLayout(layout)

	def add_student(self):
		name = self.student_name.text()
		course = self.course_name.itemText(self.course_name.currentIndex())
		mobile = self.mobile.text()
		connection = sqlite3.connect("database.db")
		cursor = connection.cursor()
		cursor.execute("INSERT INTO students (name, course, mobile) VALUES (?, ?, ?)",
					   (name, course, mobile))
		connection.commit()
		cursor.close()
		connection.close()
		main_window.load_data()


class SearchDialog(QDialog):
	def __init__(self):
		super().__init__()

		# Add a title
		self.setWindowTitle("Search Student")

		# Set fixed width and height
		self.setFixedWidth(300)
		self.setFixedHeight(300)

		search_layout = QVBoxLayout()

		# Add a student name widget
		self.student_name = QLineEdit()
		self.student_name.setPlaceholderText("Name")
		search_layout.addWidget(self.student_name)

		# Add a search button
		search_button = QPushButton("Search")
		search_button.clicked.connect(self.search)
		search_layout.addWidget(search_button)

		self.setLayout(search_layout)

	def search(self):
		name = self.student_name.text()

		connection = sqlite3.connect("database.db")
		cursor = connection.cursor()
		result = cursor.execute("SELECT * FROM students WHERE name = (?)", (name,))
		rows = list(result)
		print(rows)
		items = main_window.table.findItems(name, Qt.MatchFlag.MatchFixedString)
		for item in items:
			print(item)
			main_window.table.item(item.row(), 1).setSelected(True)

		cursor.close()
		connection.close()


app = QApplication(sys.argv)
main_window = MainWindow()
main_window.show()
main_window.load_data()
sys.exit(app.exec())