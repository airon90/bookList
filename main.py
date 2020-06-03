#!/usr/bin/python
# -*- coding: utf-8 -*-

import datetime
import json
from pathlib import Path
import pickle
import urllib.request


def check_double_books(isbn):
    for b in booklist:
        if (isbn == b["isbn"]):
            return 1
    return 0


def get_book(code):
    URL = "https://inventaire.io/api/entities?action=by-uris&uris=" + \
        str(code) + "&refresh=false"

    with urllib.request.urlopen(URL) as url:
        data = json.loads(url.read().decode())
    return data


def listBooks(booklist):
    for i in range(len(booklist)):
        b = booklist[i]
        if b["pages"] == "" or b["pages"] == "0":
            print(str(i + 1) + ". " +
                  "\"" + b["title"] + "\", " +
                  str(b["progress"]) + "p. Tags: " + ", ".join(b["tags"]))
        else:
            print(str(i + 1) + ". " +
                  "\"" + b["title"] + "\", " +
                  str(b["progress"]) + "/" + str(b["pages"]) + "p. (" +
                  str(round(int(b["progress"])*100/int(b["pages"]), 2)) +
                  "%) Tags: " + ", ".join(b["tags"]))


def enterDate():
    print("1. Today\n2. Another date")
    loop = True
    while loop:
        datachoice = input("Choice: ")
        if datachoice == "1":
            chosendate = datetime.date.today()
            loop = False
        elif datachoice == "2":
            loop2 = True
            while loop2:
                try:
                    Y = int(input("Insert year: "))
                    M = int(input("Insert month: "))
                    D = int(input("Insert day: "))
                    chosendate = datetime.date(Y, M, D)
                    if chosendate > datetime.date.today():
                        print("Date must not be in the future")
                    else:
                        loop2 = False
                except ValueError:
                    print("Wrong date")
            loop = False
        else:
            print("Wrong choice")
    return chosendate


loopMenu = True
FILENAME = "bookList.pkl"
booklist = []

if Path(FILENAME).is_file():
    datafile = open(FILENAME, 'rb')
    booklist = pickle.load(datafile)
    datafile.close()

k = len(booklist)

while(loopMenu):
    menu = input("1. Add a book\n2. List books" +
                 "\n3. Find book\n4. Edit book\n5. Exit\nChoice: ")
    if menu == "1":
        loopMenu2 = True
        while(loopMenu2):
            print("Type code (ISBN, Wikidata, Inventaire, ...) " +
                  "with prefix and eventually separated by a pipe.")
            print("ex.: isbn:XXXXXXXXXX|wd:QXXXXXX|inv:XXXXXXXXXXX")
            bookcode = input("Code: ")
            if (bookcode == ""):
                loopMenu2 = False
            if (bookcode[:4].isdigit() == True):
                bookcode = "isbn:" + str(bookcode)
            bookcode = "".join(bookcode.split("-"))

            bookdata = get_book(bookcode)
            if ("entities" in bookdata.keys()):
                data = bookdata["entities"]
                codes = bookcode.split("|")
                for c in codes:
                    if ("redirects" in bookdata.keys()
                            and c in bookdata["redirects"]):
                        c = bookdata["redirects"][c]
                    title = data[c]["claims"]["wdt:P1476"][0]
                    print(title)  # TODO: bttr
                print("Is/Are this/these your book(s)?")
                loopMenu3 = True
                while(loopMenu3):
                    menu3 = input("1. Yes\n2. No\nChoice: ")
                    if menu3 == "1":
                        doublebooks = check_double_books(
                            data[c]["claims"]["wdt:P212"][0])
                        if doublebooks == 0:
                            booklist.append({
                                "id": str(k),
                                "invid": data[c]["_id"],
                                "title": title,
                                "image": data[c]["image"]["url"] if "image" in data[c].keys() and "url" in data[c]["image"].keys() else "",
                                "pages": str(data[c]["claims"]["wdt:P1104"][0]) if "wdt:P1104" in data[c]["claims"].keys() else "",
                                "isbn": str(data[c]["claims"]["wdt:P212"][0]),
                                "progress": "0",
                                "tags": list(),
                                "added": datetime.date.today(),
                                "started": -1,
                                "finished": -1
                            })
                        else:
                            print("This book is already in list")
                        loopMenu2 = False
                        loopMenu3 = False
                    elif menu3 == "2":
                        print("Book not added")  # TODO: multiple returns
                        loopMenu2 = False
                        loopMenu3 = False
                    else:
                        print("Wrong choice")
            else:   # FIXME: handle wrong codes
                print(bookdata["status_verbose"])
                print("If you think that the code you typed " +
                      "is correct, then the book might not be " +
                      "in Inventaire.io database")
                loopMenu2 = False
        x = input("")

    elif menu == "2":
        listBooks(booklist)
        x = input("")

    elif menu == "3":
        loopMenu2 = True
        while(loopMenu2):
            print("1. By title\n2. By tag\n3. Go back")
            choice = input("Choice: ")
            if choice == "1":
                print("I'm sorry but this function has not been implemented yet.")
                loopMenu2 = False
            elif choice == "2":
                target = input("Insert tag: ")
                books = []
                for book in booklist:
                    for tag in book["tags"]:
                        if tag == target:
                            books.append(book)
                if len(books) == 0:
                    print("No book found")
                else:
                    listBooks(books)
                    # TODO: edit books?
                loopMenu2 = False
            elif choice == "3":
                loopMenu2 = False
            else:
                print("Wrong choice")
        x = input("")

    elif menu == "4":
        loopMenu2 = True
        while(loopMenu2):
            listBooks(booklist)
            chosenBook = input("Choice: ")
            if (chosenBook.isdigit() == False or int(chosenBook) not in range(1, len(booklist) + 1)):
                print("Wrong choice")
            else:
                loopMenu3 = True
                while(loopMenu3):
                    print("1. Edit data\n2. Remove book\n3. Go back")
                    editchoice = input("Choice: ")
                    if editchoice == "1":
                        print(
                            "1. Edit tags\n2. Change read pages\n3. Add start date\n4. Add end date")
                        editdataloop = True
                        while editdataloop:
                            editdatachoice = input("Choice: ")
                            if editdatachoice == "1":
                                tags = input("Add comma-separated tags: ")
                                booklist[int(chosenBook) -
                                         1]["tags"] = tags.split(",")
                                editdataloop = False
                            elif editdatachoice == "2":
                                readpages = "x"
                                while not readpages.isdigit() or int(readpages) < 0 or int(readpages) > int(booklist[int(chosenBook) - 1]["pages"]):
                                    readpages = input("Page: ")
                                booklist[int(chosenBook) -
                                         1]["progress"] = readpages
                                editdataloop = False
                            elif editdatachoice == "3":
                                booklist[int(chosenBook) -
                                         1]["started"] = enterDate()
                                editdataloop = False
                            elif editdatachoice == "4":
                                chosendate = enterDate()
                                if chosendate < booklist[int(chosenBook) - 1]["started"]:
                                    print("End date must be after start date")
                                else:
                                    booklist[int(chosenBook) -
                                             1]["finished"] = enterDate()
                                editdataloop = False
                            else:
                                print("Wrong choice")
                        loopMenu2 = False
                        loopMenu3 = False
                    elif editchoice == "2":
                        del(booklist[int(chosenBook) - 1])
                        print("Book removed")
                        loopMenu2 = False
                        loopMenu3 = False
                    elif editchoice == "3":
                        loopMenu3 = False
                    else:
                        print("Wrong choice")
        x = input("")

    elif menu == "5":
        output = open(FILENAME, 'wb')
        pickle.dump(booklist, output)
        output.close()
        print("Goodbye!")
        loopMenu = False
    else:
        print("Wrong choice")
