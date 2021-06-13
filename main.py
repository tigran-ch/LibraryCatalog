from book import Book

# A small flow for the running implemented methods
if __name__ == '__main__':
    book = Book()
    ISBN1 = "0140449264"
    ISBN2 = "0156012197"
    ISBN3 = "0122334455"
    user1 = "1234"
    user2 = "1235"
    user3 = "1236"
    user4 = "1237"

    book.user_checkout_book(ISBN1, user1)
    book.user_checkout_book(ISBN1, user2)
    book.user_checkout_book(ISBN2, user1)
    book.user_reserve_book(ISBN1, user3)
    book.user_return_book(ISBN1, user2)
    book.get_subscribers_of_the_book(ISBN1)
    book.get_overdue_books_of_the_user(user4)
    book.get_fine_for_overdue_book_of_the_user(ISBN3, user4)
    book.get_total_fine(user4)
    book.get_users_who_checked_out_book(ISBN2)
    book.check_book_is_available(ISBN2)
    book.add_user()
    book.add_book()
    book.remove_user('1238')
    book.remove_book('000000')