from dotenv import load_dotenv
import configparser
import datetime
import time
import os

class Book:
    __fine_unit__ = 5
    __term__ = datetime.timedelta(days=90)
    __term_of_a_fine__ = datetime.timedelta(weeks=1)

    def __init__(self):
        load_dotenv()
        self.books = configparser.ConfigParser()
        self.users = configparser.ConfigParser()

    def __read_files__(self):
        self.books.read(os.getenv('BOOKS_INFO_FILE'))
        self.users.read(os.getenv('USERS_INFO_FILE'))

    def __write_file__(self):
        with open(os.getenv('BOOKS_INFO_FILE'), 'w') as booksfile:
            self.books.write(booksfile)
        with open(os.getenv('USERS_INFO_FILE'), 'w') as usersfile:
            self.users.write(usersfile)

    def __book_not_exists_in_lib__(self, ISBN):
        # Print a message if given book is not exists in library
        if not self.books.has_section(ISBN):
            print("No such book in the library: " + ISBN)
            return 1
        return 0

    def __user_not_exists_in_lib__(self, user_id):
        # Print a message if there is no user with given user_id
        if not self.users.has_section(user_id):
            print("No such user in the library " + user_id)
            return 1
        return 0

    def __get_current_date__(self):
        # Get today date with "dd/mm/yy" format
        today_str = time.strftime("%d/%m/%y")
        today = datetime.datetime.strptime(today_str, '%d/%m/%y')
        return today

    def __get_book_return_date__(self, ISBN, user_id):
        # Calculation of the book return date
        user_book_date_str = str(self.users[user_id][ISBN])
        user_book_date = datetime.datetime.strptime(user_book_date_str, '%d/%m/%y')
        return_date = user_book_date + self.__term__
        return return_date

    def __get_notification_for_reserved_books__(self, ISBN):
        # Give notification if returned book which had reserved by other user(s)
        book_subscribers = self.get_subscribers_of_the_book(ISBN, False)
        if len(book_subscribers) == 0:
            return
        print("Note: Following users had reserved the returned book " + ISBN + ": " + str(book_subscribers))

    def __add_or_append_option__(self, ISBN, user_id, option, keyword):
        # Adds option into user info file. If option exists appends to value.
        if self.users.has_option(user_id, option):
            if str(self.users[user_id][option]).find(ISBN) != -1:
                print('The user "' + user_id + '" already ' + keyword + ' the book: ' + ISBN)
                return False
            else:
                self.users.set(user_id, option, self.users[user_id][option] + " " + ISBN)
        else:
            self.users.set(user_id, option, ISBN)
        return True

    def user_checkout_book(self, ISBN, user_id):
        self.__read_files__()
        if self.__book_not_exists_in_lib__(ISBN): return
        if self.__user_not_exists_in_lib__(user_id): return

        if not self.__add_or_append_option__(ISBN, user_id, 'books', 'took'): return
        # Reduce number available_copies of the book
        self.books[ISBN]['available_copies'] = str(int(self.books[ISBN]['available_copies']) - 1)
        # Add book taking date into user info
        today = time.strftime("%d/%m/%y")
        self.users.set(user_id,ISBN,str(today))
        # If the user had reserved the book, the reservation will be deleted
        if self.users.has_option(user_id, 'reserves'):
            user_reserves_str = str(self.users[user_id]['reserves'])
            if user_reserves_str.find(ISBN) != -1:
                user_reserves_list = user_reserves_str.split(" ")
                user_reserves_list.remove(ISBN)
                self.users[user_id]['reserves'] = " ".join(user_reserves_list)
        self.__write_file__()

    def user_return_book(self, ISBN, user_id):
        self.__read_files__()
        if self.__book_not_exists_in_lib__(ISBN): return
        if self.__user_not_exists_in_lib__(user_id): return

        # If returned book was not available before, give notification
        available_copies = int(self.books[ISBN]['available_copies'])
        if available_copies == 0:
            self.__get_notification_for_reserved_books__(ISBN)
        # Increase the available_copies of the book
        self.books[ISBN]['available_copies'] = str(int(self.books[ISBN]['available_copies']) + 1)
        # Remove the returned book date from the user info
        self.users.remove_option(user_id, ISBN)
        # Check that user had gaven the book
        user_books_str = str(self.users[user_id]['books'])
        if user_books_str.find(ISBN) == -1:
            print("User " + user_id + " have not such book in account " + ISBN)
            return
        # Remove the returned book from the user info books list
        user_books_list = user_books_str.split(" ")
        user_books_list.remove(ISBN)
        self.users[user_id]['books'] = " ".join(user_books_list)

        self.__write_file__()

    def user_reserve_book(self, ISBN, user_id):
        self.__read_files__()
        if self.__book_not_exists_in_lib__(ISBN): return
        if self.__user_not_exists_in_lib__(user_id): return

        # Check that book is not available and do reservation
        if not self.check_book_is_available(ISBN):
            if not self.__add_or_append_option__(ISBN, user_id, 'reserves', 'reserved'):
                return
        print("Reservation done for " + user_id + " user")
        self.__write_file__()

    def get_subscribers_of_the_book(self, ISBN, files_open=True):
        if files_open: self.__read_files__()
        if self.__book_not_exists_in_lib__(ISBN): return

        # Get list of users who reserved the book
        subscribers_list = []
        for id in self.users.sections():
            if self.users.has_option(id, 'reserves'):
                if str(self.users[id]['reserves']).find(ISBN) != -1:
                    subscribers_list.append(self.users[id]['name'])
        if len(subscribers_list)==0:
            print("No reservations for the book " + ISBN)
            return subscribers_list
        if files_open: print("The book " + ISBN + " subscribers are: " + str(subscribers_list))
        return subscribers_list

    def get_overdue_books_of_the_user(self, user_id):
        self.__read_files__()
        if self.__user_not_exists_in_lib__(user_id): return

        # Check that the user have book(s)
        user_books_list = str(self.users[user_id]['books']).split(" ")
        if len(user_books_list) == 0:
            print("The user have not books on account " + user_id)
            return
        # Get list of overdue books
        today = self.__get_current_date__()
        overdue_books = []
        for book in user_books_list:
            return_date = self.__get_book_return_date__(book, user_id)
            if return_date<today:
                overdue_books.append(self.books[book]['title'])

        if len(overdue_books)== 0:
            print("User " + user_id + " has no overdue books")
            return overdue_books
        print("The user " + user_id + " overdue books are: " + str(overdue_books))
        return overdue_books

    def get_fine_for_overdue_book_of_the_user(self, ISBN, user_id, files_open=True):
        if files_open: self.__read_files__()
        if self.__book_not_exists_in_lib__(ISBN): return
        if self.__user_not_exists_in_lib__(user_id): return

        # Check that the user have the given book in account
        if not self.users.has_option(user_id, ISBN):
            print("User " + user_id + " has not " + ISBN + " book in account")
            return 0
        # Calculate the fine for the given book
        today = self.__get_current_date__()
        return_date = self.__get_book_return_date__(ISBN, user_id)
        fine = 0
        fine_date = return_date + self.__term_of_a_fine__
        while fine_date < today:
            fine += self.__fine_unit__
            fine_date += self.__term_of_a_fine__
        print("User " + user_id + " should pay " + str(fine) + "$ fine for the book " + ISBN)
        return fine

    def get_total_fine(self, user_id):
        self.__read_files__()
        if self.__user_not_exists_in_lib__(user_id): return

        # Get list of the user books and calculate the total fine
        user_books_list = str(self.users[user_id]['books']).split(" ")
        total_fine = 0
        for book in user_books_list:
            total_fine += self.get_fine_for_overdue_book_of_the_user(book,user_id, False)
        print("Total fine is " + str(total_fine) + "$")
        return total_fine

    def check_book_is_available(self, ISBN):
        self.__read_files__()
        if self.__book_not_exists_in_lib__(ISBN): return

        if int(self.books[ISBN]['available_copies']) > 0 :
            print("The book " + ISBN + " is available")
            return True
        else:
            print("The book " + ISBN + " is not available")
            return False

    def get_users_who_checked_out_book(self,ISBN):
        self.__read_files__()
        if self.__book_not_exists_in_lib__(ISBN): return

        users_list = []
        for user in self.users.sections():
            if self.users.has_option(user, 'books'):
                if str(self.users[user]['books']).find(ISBN) != -1:
                    users_list.append(user)
        print("The book " + ISBN + " checked out by users: " + str(users_list))
        return users_list

    def add_user(self):
        self.__read_files__()
        user_name = str(input("Type user name: "))
        user_id = str(int(max(self.users.sections())) + 1)
        self.users.add_section(user_id)
        self.users.set(user_id, 'name', user_name)
        self.__write_file__()

    def add_book(self):
        self.__read_files__()
        book_ISBN = str(input("Type book ISBN: "))
        book_title = str(input("Type book title: "))
        book_pages = str(input("Type book pages: "))
        book_copies = str(input("Type book count: "))
        self.books.add_section(book_ISBN)
        self.books.set(book_ISBN, 'title', book_title)
        self.books.set(book_ISBN, 'pages', book_pages)
        self.books.set(book_ISBN, 'copies', book_copies)
        self.books.set(book_ISBN, 'available_copies', book_copies)
        self.__write_file__()

    def remove_user(self, user_id):
        self.__read_files__()
        self.users.remove_section(user_id)
        self.__write_file__()

    def remove_book(self, ISBN):
        self.__read_files__()
        self.books.remove_section(ISBN)
        self.__write_file__()
