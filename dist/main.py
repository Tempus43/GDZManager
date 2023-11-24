import shutil
import requests
import sys
import sqlite3
import os
from PIL import Image
from bs4 import BeautifulSoup
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QInputDialog, QCheckBox
from gdz_manager import Ui_MainWindow


class ManagerGDZ(QMainWindow, Ui_MainWindow):
    def __init__(self, list_sorting_attribute):
        super().__init__()
        self.setupUi(self)
        self.setWindowTitle("GDZ Manager")

        self.tusks = 0
        self.list_sorting_attributes = list_sorting_attribute

        self.con = sqlite3.connect("manager_gdz.sqlite")
        cur = self.con.cursor()
        textbooks = cur.execute("""SELECT * FROM textbooks""").fetchall()
        class_and_subjects = sorted(cur.execute("""SELECT class, subject 
                                                   FROM textbooks""").fetchall(), key=lambda b: b[0])

        if class_and_subjects:
            self.label_sort = QLabel("Сортировка\nучебников", self.widget)
            self.label_sort.setStyleSheet("font-size: 15px")
            self.label_sort.move(10, 5)

            check_class = set()
            y = 50
            for cls, sub in class_and_subjects:
                if cls not in check_class:
                    x = 10
                    sort_box = QCheckBox(f"{cls} Класс", self.widget)
                    if cls in self.list_sorting_attributes:
                        sort_box.setChecked(True)
                    sort_box.stateChanged.connect(self.add_attribute_sort)
                    sort_box.move(x, y)
                    sort_box.setStyleSheet("font-size: 15px")
                    y += 20
                    check_class.add(cls)
                if f"{cls}-{sub}" not in check_class:
                    x = 20
                    sort_box = QCheckBox(f"{cls}-{sub}", self.widget)
                    if f"{cls}-{sub}" in self.list_sorting_attributes:
                        sort_box.setChecked(True)
                    sort_box.stateChanged.connect(self.add_attribute_sort)
                    sort_box.setStyleSheet("font-size: 15px")
                    sort_box.move(x, y)
                    check_class.add(f"{cls}-{sub}")
                    y += 20

            clear_sort_button = QPushButton("Убрать все галочки", self.widget)
            clear_sort_button.move(10, y + 10)
            clear_sort_button.resize(120, 40)
            clear_sort_button.clicked.connect(self.clear_all_attribute_sort)
            clear_sort_button.setStyleSheet("""
                color: rgb(0, 0, 255);
                background-color: rgb(255, 255, 255);
                border-radius: 15px;
                border: 5px solid orange
            """)

            sort_button = QPushButton("Отсортировать", self.widget)
            sort_button.resize(120, 40)
            sort_button.move(10, y + 60)
            sort_button.clicked.connect(self.sorted_books)
            sort_button.setStyleSheet("""
                color: rgb(0, 0, 255);
                background-color: rgb(255, 255, 255);
                border-radius: 15px;
                border: 5px solid orange
            """)

        count_textbooks = len(textbooks)
        y = 0
        x = 0
        self.widget.setMinimumHeight(int(count_textbooks / 3 * 280 + 100))
        while count_textbooks != 0:
            book = textbooks[len(textbooks) - count_textbooks]
            class_book = book[2]
            subject = str(class_book) + "-" + book[1]
            if (class_book in self.list_sorting_attributes or subject in self.list_sorting_attributes)\
                    or not self.list_sorting_attributes:
                book_button = QPushButton(self.widget)
                book_button.resize(95 * 2, 135 * 2)
                book_button.move(self.widget.x() + 150 + x * 200, self.widget.y() + y * 280)
                id_book, title, image = book[0], book[4], book[3]
                book_button.setText(str(id_book))
                book_button.setStyleSheet("color: transparent;")
                icon = QIcon(f"./textbooks/{title}/{image}")
                book_button.setIcon(icon)
                book_button.setIconSize(icon.actualSize(book_button.size()))
                book_button.setStyleSheet("background-color: transparent;")
                book_button.setAutoFillBackground(True)
                book_button.setFlat(True)
                book_button.clicked.connect(self.view_book)
                if count_textbooks == 0:
                    break
                x += 1
                if x == 4:
                    x = 0
                    y += 1
            count_textbooks -= 1
        else:
            book_button = QPushButton(self.widget)
            book_button.resize(95 * 2, 135 * 2)
            book_button.move(self.widget.x() + 150 + x * 200, self.widget.y() + y * 280)
            book_button.clicked.connect(self.add_new_book)

    def clear_all_attribute_sort(self):
        self.list_sorting_attributes = []
        self.hide()
        self.__init__(self.list_sorting_attributes)
        self.show()

    def sorted_books(self):
        self.hide()
        self.__init__(self.list_sorting_attributes)
        self.show()

    def add_attribute_sort(self):
        attribute = self.sender().text()
        if "Класс" in attribute:
            attribute = int(''.join([i for i in attribute if i.isdigit()]))
        if attribute not in self.list_sorting_attributes:
            self.list_sorting_attributes.append(attribute)
        else:
            self.list_sorting_attributes.remove(attribute)

    def add_new_book(self):
        name, ok_pressed = QInputDialog.getText(self, "Введите адрес", "Ссылка на сайт с учебником gdz.ru:")
        if ok_pressed and name and "gdz.ru" in name:
            cur = self.con.cursor()
            check = cur.execute("""SELECT * FROM textbooks WHERE link = ?""", (name, )).fetchall()
            if not check:
                response = requests.get(name)
                soup = BeautifulSoup(response.text, 'html.parser')
                img_tags = soup.find_all('img')
                img_book = ''
                for img in img_tags:
                    if 'gdz' in img['src']:
                        img_book = 'https:' + img['src']
                        break

                inf_of_book = name[8:].split('/')
                subject, title, image = inf_of_book[2], inf_of_book[-2], inf_of_book[-2] + '.jpg'
                cls = int(''.join([i for i in inf_of_book[1] if i.isdigit()]))

                cur.execute("""INSERT INTO textbooks(subject,class,image,title,link) 
                               VALUES(?,?,?,?,?)""", (subject, cls, image, title, name))
                self.con.commit()

                new_folder_path = f"./textbooks/{title}"  # создаём папку, в которой будут хранится изображения учебника
                os.mkdir(new_folder_path)
                new_folder_path += "/tasks"
                os.mkdir(new_folder_path)
                out = open(f"./textbooks/{title}/out.jpg", "wb")        # скачиваем изображение учебника
                out.write(requests.get(img_book).content)
                out.close()
                new_image = Image.open(f"./textbooks/{title}/out.jpg")  # измения размер изображения
                resized_image = new_image.resize((190, 270))
                resized_image.save(f"./textbooks/{title}/{image}")
                os.remove(f"./textbooks/{title}/out.jpg")               # удаляем оригинальное изображение

                links = soup.find_all('a')
                cur = self.con.cursor()
                id_book = int(cur.execute(
                    """SELECT id, title 
                       FROM textbooks 
                       WHERE title = ?""",
                    (title, )).fetchone()[0])
                for link in links:
                    i = link.get('href')
                    if i:
                        if name[15:] in i and 'user' not in i:
                            title_img = i.split('/')[-2]
                            cur.execute("""INSERT INTO tasks(id,number) VALUES(?,?)""",
                                        (id_book, title_img))
                self.con.commit()
                self.hide()
                self.__init__(self.list_sorting_attributes)
                self.show()

    def view_book(self):
        height, width, x, y = self.height(), self.width(), self.geometry().x(), self.geometry().y()
        self.tusks = ListOfTasks(height, width, x, y, self, self.sender().text())
        self.hide()
        self.tusks.show()


class ListOfTasks(QMainWindow, Ui_MainWindow):
    def __init__(self, height, width, x, y, *args):
        super(ListOfTasks, self).__init__()
        self.setupUi(self)
        self.setGeometry(x, y, width, height)
        self.setWindowTitle("Список заданий")

        self.back_button = QPushButton("Вернуться к списку\nучебников", self.widget)
        self.back_button.setStyleSheet("""
            color: rgb(0, 0, 255);
            background-color: rgb(255, 255, 255);
            border-radius: 15px;
            border: 5px solid orange
        """)
        self.back_button.resize(120, 40)
        self.back_button.move(10, 10)
        self.back_button.clicked.connect(self.go_back)

        self.textbooks = args[0]
        self.id_book = args[1]
        self.task_img = 0
        self.con = sqlite3.connect("manager_gdz.sqlite")

        cur = self.con.cursor()
        book = cur.execute("""
            SELECT title,link,image 
            FROM textbooks 
            WHERE id = ?""", (self.id_book, )).fetchall()[0]
        list_of_tasks = cur.execute("""
            SELECT * 
            FROM tasks 
            WHERE id = ?""", (self.id_book,)).fetchall()

        im = Image.open(f"./textbooks/{book[0]}/{book[2]}")
        width, height = im.size
        pixmap = QPixmap(f"./textbooks/{book[0]}/{book[2]}")
        self.textbook = QLabel(self.widget)
        self.textbook.move(10, 60)
        self.textbook.resize(width, height)
        self.textbook.setPixmap(pixmap)

        self.download_button = QPushButton("Скачать все задания", self.widget)
        self.download_button.setStyleSheet("""
            color: rgb(0, 0, 255);
            background-color: rgb(255, 255, 255);
            border-radius: 15px;
            border: 5px solid orange
        """)
        self.download_button.move(10, 345)
        self.download_button.resize(120, 40)
        self.download_button.clicked.connect(self.download_all_tasks)

        self.delete_button = QPushButton("Удалить учебник", self.widget)
        self.delete_button.setStyleSheet("""
            color: rgb(0, 0, 255);
            background-color: rgb(255, 255, 255);
            border-radius: 15px;
            border: 5px solid orange
        """)
        self.delete_button.resize(120, 40)
        self.delete_button.move(10, 395)
        self.delete_button.clicked.connect(self.delete_textbook)

        self.path_directory = "./textbooks/" + book[0] + "/tasks"
        self.link_on_book = book[1]

        count_tasks = len(list_of_tasks)

        self.widget.setMinimumHeight(int(count_tasks / 8 * 50 + 50))
        self.scrollArea.setMinimumWidth(8 * 100 + 240)
        self.widget.setMinimumWidth(8 * 100 + 240)
        self.scrollAreaWidgetContents.setMinimumWidth(8 * 100 + 240)

        y = 0
        if not count_tasks:
            message = QLabel("Ошибка загрузки.", self.widget)
            message.move(500, 20)
            message.setStyleSheet("font-size: 20px")
        while count_tasks != 0:
            for x in range(8):
                task = list_of_tasks[len(list_of_tasks) - count_tasks]
                task_button = QPushButton(task[1], self.widget)
                task_button.resize(75, 40)
                task_button.move(self.widget.x() + 210 + x * 100, self.widget.y() + y * 50)
                task_button.clicked.connect(self.view_task)
                task_button.setStyleSheet("""
                    color: rgb(0, 0, 255);
                    background-color: rgb(255, 255, 255);
                    border-radius: 15px;
                    border: 5px solid orange
                """)
                count_tasks -= 1
                if count_tasks == 0:
                    break
            y += 1

    def delete_textbook(self):
        cur = self.con.cursor()
        book = cur.execute("""
            SELECT title
            FROM textbooks 
            WHERE id = ?""", (self.id_book,)).fetchall()[0]
        tasks = cur.execute("""
            SELECT number
            FROM tasks
            WHERE id = ?""", (self.id_book,)).fetchall()
        for task in tasks:
            cur.execute("""
                DELETE 
                FROM image_task
                WHERE id = ?""", (book[0] + task[0], ))
        cur.execute("""
            DELETE
            FROM tasks
            WHERE id = ?""", (self.id_book, ))
        cur.execute("""
            DELETE
            FROM textbooks
            WHERE id = ?""", (self.id_book, ))
        self.con.commit()
        shutil.rmtree(f"./textbooks/{book[0]}")
        self.textbooks = ManagerGDZ([])
        self.textbooks.setGeometry(self.geometry().x(), self.geometry().y(), self.width(), self.height())
        self.hide()
        self.textbooks.show()

    def download_all_tasks(self):
        cur = self.con.cursor()
        book = cur.execute("""
            SELECT title,link,image 
            FROM textbooks 
            WHERE id = ?""", (self.id_book,)).fetchall()[0]
        response = requests.get(book[1])
        soup = BeautifulSoup(response.text, 'html.parser')
        links = soup.find_all('a')
        for link in links:
            i = link.get('href')
            if i:
                if book[1][15:] in i and 'user' not in i:
                    img_response = requests.get(f"https://gdz.ru{i}")
                    all_img_tasks = BeautifulSoup(img_response.text, 'html.parser').find_all('img')
                    x = 0
                    number = i.split('/')[-2]
                    for img in all_img_tasks:
                        if 'gdz' in img['src'] and 'tasks' in img['src']:
                            if not cur.execute("""SELECT * 
                                                  FROM image_task 
                                                  WHERE id = ?""", (book[1] + number, )).fetchall():
                                try:
                                    os.mkdir(f"./textbooks/{book[0]}/tasks/{number}")
                                except FileExistsError:
                                    pass
                                out = open(f"./textbooks/{book[0]}/tasks/{number}/{x}.jpg", "wb")
                                out.write(requests.get("https:" + img['src']).content)
                                out.close()
                                cur.execute("""INSERT INTO image_task(id,title) VALUES(?,?)""", (book[0] + number, x))
                                x += 1
        self.con.commit()

    def view_task(self):
        height, width, x, y = self.height(), self.width(), self.geometry().x(), self.geometry().y()
        self.task_img = TaskImages(self, self.sender().text(), self.path_directory, self.link_on_book,
                                   x, y, width, height)
        self.hide()
        self.task_img.show()

    def go_back(self):
        self.textbooks.setGeometry(self.geometry().x(), self.geometry().y(), self.width(), self.height())
        self.hide()
        self.textbooks.show()


class TaskImages(QMainWindow, Ui_MainWindow):
    def __init__(self, list_of_tasks, number, path_directory, link_on_book, x, y, width, height):
        super(TaskImages, self).__init__()
        self.setupUi(self)
        self.setGeometry(x, y, width, height)
        self.setWindowTitle(f"Задание {number}")

        self.path_directory = path_directory
        self.link_on_book = link_on_book
        self.list_of_tasks = list_of_tasks

        self.pushButton = QPushButton("Вернуться к списку\nзаданий", self.widget)
        self.pushButton.resize(120, 40)
        self.move(10, 10)
        self.pushButton.clicked.connect(self.go_back)
        self.pushButton.setStyleSheet("""
            color: rgb(0, 0, 255);
            background-color: rgb(255, 255, 255);
            border-radius: 15px;
            border: 5px solid orange
        """)

        self.con = sqlite3.connect("manager_gdz.sqlite")
        cur = self.con.cursor()
        check = cur.execute("""
            SELECT * 
            FROM image_task 
            WHERE id = ?""", (path_directory.split('/')[-2] + number, )).fetchall()

        close_numbers = cur.execute("""
            SELECT number
            FROM tasks
            WHERE id = (SELECT id 
                        FROM tasks 
                        WHERE number = ?)""", (number, )).fetchall()

        index_number = close_numbers.index((number, ))
        a = []
        for i in range(len(close_numbers) - 5):
            a = close_numbers[i:i + 5]
            if index_number - 1 < 0 and a[0][0] == number:
                a[0] = ("...", )
                break
            elif index_number - 2 == -1 and a[1][0] == number:
                a[1] = ("...", )
                break
            elif index_number + 1 == len(close_numbers) - 1 and a[4][0] == number:
                a[4] = ("...", )
                break
            elif index_number + 2 == len(close_numbers) - 1 and a[3][0] == number:
                a[3] = ("...", )
                break
            else:
                if a[2][0] == number:
                    a[2] = ("...", )
                    break

        for i in range(5):
            another_number_button = QPushButton(a[i][0], self.widget)
            another_number_button.move(200 + i * 100, 10)
            if a[i][0] != "...":
                another_number_button.clicked.connect(self.view_another_task)
            another_number_button.resize(80, 40)
            another_number_button.setStyleSheet("""
                color: rgb(0, 0, 255);
                background-color: rgb(255, 255, 255);
                border-radius: 15px;
                border: 5px solid orange
            """)

        y = 60
        x = 0
        if not check and not os.path.exists(f"{self.path_directory}/{number}"):
            new_response = requests.get(self.link_on_book + f"{number}/")
            all_img_tasks = BeautifulSoup(new_response.text, 'html.parser').find_all('img')
            os.mkdir(f"{self.path_directory}/{number}")
            for img in all_img_tasks:
                if 'gdz' in img['src'] and 'tasks' in img['src']:
                    out = open(f"{self.path_directory}/{number}/{x}.jpg", "wb")
                    out.write(requests.get("https:" + img['src']).content)
                    out.close()
                    cur.execute("""
                        INSERT 
                        INTO image_task(id,title) 
                        VALUES(?,?)""", (self.path_directory.split('/')[-2] + number, x))
                    im = Image.open(f"{self.path_directory}/{number}/{x}.jpg")
                    width, height = im.size
                    image = QLabel(self.widget)
                    image.move(100, y)
                    image.resize(width, height)
                    pixmap = QPixmap(f"{self.path_directory}/{number}/{x}.jpg")
                    image.setPixmap(pixmap)
                    y += height + 30
                    x += 1
            self.con.commit()
        else:
            for i in range(len(check)):
                im = Image.open(f"{path_directory}/{number}/{check[i][-1]}.jpg")
                width, height = im.size
                image = QLabel(self.widget)
                image.move(100, y)
                image.resize(width, height)
                pixmap = QPixmap(f"{path_directory}/{number}/{check[i][-1]}.jpg")
                image.setPixmap(pixmap)
                y += height
        self.widget.setMinimumHeight(y + 60)

    def view_another_task(self):
        self.hide()
        self.__init__(self.list_of_tasks, self.sender().text(), self.path_directory, self.link_on_book,
                      self.geometry().x(), self.geometry().y(), self.width(), self.height())
        self.show()
        print(self.sender().text())

    def go_back(self):
        self.hide()
        self.list_of_tasks.setGeometry(self.geometry().x(), self.geometry().y(), self.width(), self.height())
        self.list_of_tasks.show()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = ManagerGDZ([])
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
