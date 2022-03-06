import imdb
from os import path
import os
import webbrowser
import urllib.request
from PIL import Image
from termcolor import colored
import mariadb

terminal_size = os.get_terminal_size()
terminal_size = terminal_size[0]

current_directory = os.getcwd()
final_directory = os.path.join(current_directory, r'thumbnails')
if not os.path.exists(final_directory):
    os.makedirs(final_directory)


ia = imdb.IMDb()

os.system('cls' if os.name == 'nt' else 'clear')

moviedb = mariadb.connect(user='connector-user',
                          password='connector-password',
                          host='localhost',
                          database='connector')

moviecursor = moviedb.cursor()

class FileRelated:
    def __init__(self):
        try:
            moviecursor.execute("DESCRIBE WATCHED")
        except mariadb.ProgrammingError:
            moviecursor.execute("CREATE TABLE WATCHED(Title varchar(50), Year int(4), Kind varchar(10))")
        try:
            moviecursor.execute("DESCRIBE TOWATCH")
        except mariadb.ProgrammingError:
            moviecursor.execute("CREATE TABLE TOWATCH(Title varchar(50), Year int(4), Kind varchar(10))")

    def add(self, toadd, path_to_add):
        self.toadd = toadd
        self.path_to_add = path_to_add
        if path_to_add == "WATCHED":
            insert_command = "INSERT INTO WATCHED VALUES(%s, %s, %s)"
        else:
            insert_command = "INSERT INTO TOWATCH VALUES(%s, %s, %s)"
        moviecursor.execute(insert_command, toadd)

    def get_watched(self):
        temp_list = []
        moviecursor.execute("SELECT Title FROM WATCHED")
        for item in moviecursor:
            temp_list.append(item)
        return temp_list

    def get_to_watch(self):
        temp_list = []
        moviecursor.execute("SELECT Title FROM TOWATCH")
        for item in moviecursor:
            temp_list.append(item)
        return temp_list

    def print_all(self):
        rows = []
        print()
        print(colored(" Titles you have watched ".center(terminal_size, '+'), 'red', attrs=['bold']))
        moviecursor.execute("SELECT * FROM WATCHED")
        for item in moviecursor:
            rows.append(item)
        for row in rows:
            print(f"{row[0]}({row[1]}) - {row[2].title()}".center(terminal_size))
        print()
        rows = []
        print(colored(" Titles you want to watch ".center(terminal_size, '+'), 'red', attrs=['bold']))
        moviecursor.execute("SELECT * FROM TOWATCH")
        for item in moviecursor:
            rows.append(item)
        for row in rows:
            print(f"{row[0]}({row[1]}) - {row[2].title()}".center(terminal_size))


class Imdbsearch:
    def __init__(self):
        pass

    def search_on(self):
        to_search = input("\nWhat are you looking for (on IMDb): ")
        searched_result = ia.search_movie(to_search)
        target = searched_result[0]['full-size cover url']
        print(colored(
            f"\n{searched_result[0]['title']} ({searched_result[0]['year']})", attrs=['bold']))
        file_name = searched_result[0]['title'] + ".png"
        file_name = os.path.join(final_directory, file_name)
        if path.exists(file_name) == True:
            image = Image.open(file_name)
            image.show()
        else:
            urllib.request.urlretrieve(target, file_name)
            image = Image.open(file_name)
            image.show()
        correct = input(colored(
            "\nIs this thumbnail matching your media? (y/n):", 'white', attrs=['reverse']))
        correct = correct.upper()
        if correct == "Y":
            return searched_result[0]
        else:
            print("\n")
            print(colored("Try A More Specific Search Term(s)".center(
                terminal_size, '*'), 'yellow'))
            return self.search_on()

    def title_kind_year(self, searched_passed_value):
        self.searched_passed_value = searched_passed_value
        to_add = []
        to_add.append(searched_passed_value['title'])
        to_add.append(searched_passed_value['year'])
        to_add.append(searched_passed_value['kind'].title())
        return to_add


imdbsearch = Imdbsearch()
files_op = FileRelated()
list_watched = []
list_to_watch = []


def get_all_lists():
    list_watched = files_op.get_watched()
    list_to_watch = files_op.get_to_watch()


def print_main():
    print(colored(" Movies/Series CSV Based Management System ".center(terminal_size,
          "-"), 'blue', attrs=['bold', 'reverse']))


def clr_scr():
    os.system('cls' if os.name == 'nt' else 'clear')


print_main()

y_n = "y"
while(y_n == "y"):
    choice = input(colored(
        "\nEnter A to add, V to view, T for Top 250,  Q to quit: ", 'green', attrs=['underline']))
    choice = choice.lower()
    get_all_lists()
    if choice == "a":
        list_watched = files_op.get_watched()
        list_to_watch = files_op.get_to_watch()
        toadd = imdbsearch.title_kind_year(imdbsearch.search_on())
        if (toadd[0] in list_watched) or (toadd[0] in list_to_watch):
            print(colored(
                "\nThe Movie/Series is already in Watchlist or Watch History".center(terminal_size), 'red'))
        else:
            path_temp = int(
                input(colored("\nWhere to add? (1 for Watched, 2 for Watchlist): ", 'magenta')))
            if path_temp == 1:
                files_op.add(toadd, "WATCHED")
                files_op.print_all()
            elif path_temp == 2:
                files_op.add(toadd, "TOWATCH")
                files_op.print_all()
            else:
                print(colored("\nWrong Input".center(terminal_size, '*'), 'red'))
            get_all_lists()
    elif choice == "v":
        files_op.print_all()
        get_all_lists()
    elif choice == "q":
        y_n = "n"
        get_all_lists()
        to_commit = input("Commit Changes to Database? ")
        if to_commit.upper() in ['YES', 'Y']:
            moviedb.commit()
    elif choice == 't':
        target_top = int(
            input("Enter 1 for Top 250 Movies, 2 for Top 250 Series: "))
        if target_top == 1:
            webbrowser.open("https://www.imdb.com/chart/top")
        elif target_top == 2:
            webbrowser.open("https://www.imdb.com/chart/toptv")
        else:
            print("\n")
            print(colored("Wrong Input".center(terminal_size, "*"), 'red'))
    else:
        print("\n")
        print(colored("Wrong Input".center(terminal_size, '*'), 'red'))
        get_all_lists()

print(colored("Thanks for using! -- By Ansh Goel".center(terminal_size),
      'grey', 'on_yellow', attrs=['bold']))
