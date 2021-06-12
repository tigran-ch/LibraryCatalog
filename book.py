import configparser
import datetime
import time

class Book:
    __books_info_file__ = 'books_info.ini'
    __users_info_file__ = 'users_info.ini'

    def __init__(self):
        self.books = configparser.ConfigParser()
        self.users = configparser.ConfigParser()

    def __read_files__(self):
        self.books.read(self.__books_info_file__)
        print(self.books.sections())
        self.users.read(self.__users_info_file__)
        print(self.users.sections())

    def __write_file__(self):
        with open(self.__books_info_file__, 'w') as booksfile:
            self.books.write(booksfile)
        with open(self.__users_info_file__, 'w') as usersfile:
            self.users.write(usersfile)

    def user_checkout_book(self, ISBN, user_id):
        self.__read_files__()

        if not self.books.has_section(ISBN): print("No such book " + ISBN); return
        if not self.users.has_section(user_id): print("No such user with " + user_id + " user id"); return
        if self.users.has_option(user_id,'books'):
            if str(self.users[user_id]['books']).find(ISBN) != -1:
                print("The user already took a copy of the book " + ISBN)
                return
            else:
                self.users.set(user_id, 'books', self.users[user_id]['books'] + " " + ISBN)
        else:
            self.users.set(user_id, 'books', ISBN)

        self.books[ISBN]['available_copies'] = str(int(self.books[ISBN]['available_copies']) - 1)

        today = time.strftime("%d/%m/%y")
        self.users.set(user_id,ISBN,str(today))

        self.__write_file__()

    def user_return_book(self, ISBN, user_id):
        self.__read_files__()
        if not self.books.has_section(ISBN): print("No such book " + ISBN); return
        if not self.users.has_section(user_id): print("No such user with " + user_id + " user id"); return

        self.books[ISBN]['available_copies'] = str(int(self.books[ISBN]['available_copies']) + 1)

        self.users.remove_option(user_id, ISBN)

        user_books_list = str(self.users[user_id]['books']).split(" ")
        user_books_list.remove(ISBN)
        self.users[user_id]['books'] = " ".join(user_books_list)

        self.__write_file__()

    def user_reserve_book(self, ISBN, user_id):
        self.__read_files__()
        if not self.books.has_section(ISBN): print("No such book " + ISBN); return
        if not self.users.has_section(user_id): print("No such user with " + user_id + " user id"); return

        if int(self.books[ISBN]['available_copies']) > 0 :
            print("The book " + ISBN + " is available")
        else:
            if self.users.has_option(user_id, 'reserves'):
                if str(self.users[user_id]['reserves']).find(ISBN) != -1:
                    print("The user already reserved the book " + ISBN)
                    return
                else:
                    self.users.set(user_id, 'reserves', self.users[user_id]['reserves'] + " " + ISBN)
            else:
                self.users.set(user_id, 'reserves', ISBN)

        self.__write_file__()

    def get_subscribers_of_the_book(self, ISBN):
        self.__read_files__()
        if not self.books.has_section(ISBN): print("No such book " + ISBN); return

        subscribers_list = []
        for id in self.users.sections():
            if str(self.users[id]['reserves']).find(ISBN) != -1:
                subscribers_list.append(self.users[id]['name'])
        if len(subscribers_list)==0: print("No reservations for the book " + ISBN); return subscribers_list
        print(subscribers_list)
        return subscribers_list




    def get_overdue_books_of_the_user(self, user_id):
        self.__read_files__()
        if not self.users.has_section(user_id): print("No such user with " + user_id + " user id"); return
        user_books_list = str(self.users[user_id]['books']).split(" ")
        if len(user_books_list) == 0: print("The user have not books on account " + user_id); return

        today_str = time.strftime("%d/%m/%y")
        today = datetime.datetime.strptime(today_str, '%d/%m/%y')
        overdue_books = []
        for book in user_books_list:
            user_book_date_str = str(self.users[user_id][book])
            user_book_date = datetime.datetime.strptime(user_book_date_str, '%d/%m/%y')
            return_date = user_book_date + datetime.timedelta(days=93)
            if return_date<today:
                overdue_books.append(self.books[book]['title'])
        if len(overdue_books)== 0: print("User " + user_id + " has no overdue books"); return overdue_books
        print(overdue_books)
        return overdue_books









if __name__ == '__main__':
    k = Book()
    ISBN = "0140449264"
    #ISBN = "0156012197"
    user = "1234"
    #k.user_checkout_book(ISBN, user)
    #k.user_return_book(ISBN,user)
    #k.user_reserve_book(ISBN,user)
    #k.get_subscribers_of_the_book(ISBN)
    #k.get_overdue_books_of_the_user(user)
