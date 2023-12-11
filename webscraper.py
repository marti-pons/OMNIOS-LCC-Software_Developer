import requests
from bs4 import BeautifulSoup
import csv


def fix_title(title):
    '''
    Takes in a title in html format.
    Modifies it to contain only the meaningful part.
    Returns the modified title.
    '''

    # Initialize an index
    i = 0

    # Remove the first blank spaces
    while title[i] == '\n' or title[i] == ' ':
        i += 1

    # Define new title
    new_title = '' 

    # Add characters to new_title until a '|' is found
    # Assume the title doesn't contain '|'
    while title[i] != '|': 
        new_title += title[i]
        i += 1

    # Remove trailing spaces at the end of the new_title
    while new_title[-1] == ' ':
        new_title = new_title[:-1]

    return new_title


def fix_title2(title):
    '''
    Takes in a title in html format.
    Assumes the format is constant.
    Returns the modified title.
    '''

    return title[5:-29]


def stars2int(stars):
    '''
    Takes in a string containing the star rating.
    Returns the stars as an int. 
    '''

    if stars == 'Zero':
        return 0
    elif stars == 'One':
        return 1
    elif stars == 'Two':
        return 2
    elif stars == 'Three':
        return 3
    elif stars == 'Four':
        return 4
    elif stars == 'Five':
        return 5


def find_attrs(short_link, soup):
    '''
    Takes if the short_link of the catalogue and the BeautifulSoup element of the page.
    Finds the following attributes of every book on the page:
        - Title 
        - Stars rating
        - Image url
        - Price (in pounds)
    Returns the list of book attributes of the books on the page.
    '''

    # Initialize an empty list to store the books attributes
    books_attrs = []

    # Find all the book entries on the page 
    books = soup.find_all('h3')  # <h3> elements are the books

    # Iterate the books
    for book in books: 
        # Move to the book page
        bookpage = requests.get(short_link+book.find('a',href=True)['href'])
        booksoup = BeautifulSoup(bookpage.content, 'html.parser') 

        # Get book attributes
        title = fix_title2(booksoup.title.string)
        stars = stars2int(booksoup.find(class_ ='star-rating')['class'][1])
        img = booksoup.find('img')['src']
        price = booksoup.find(class_='price_color').string

        # Add book attributes to the list
        books_attrs.append([title, stars, img, float(price[1:])])
        # books_attrs.append({'Title': title, 'Stars': stars, 'Img': img, 'Price (£)': float(price[1:])})

    return books_attrs


def travel_pages(link, soup):
    '''
    Takes in a link to a page and the BeautifulSoup element of the page.
    Travles around the "next page" and add the book attributes of every book
    of every page.
    Returns the list of book attributes.
    '''

    # Define auxiliary variables
    nextsoup = soup
    short_link = link[:36]  # 'http://books.toscrape.com/catalogue/'

    # Initialize an empty list to store the books attributes
    books = [] 

    i = 1   # just for keeping track of the loop
    
    # Travel around the "next pages"
    while(nextsoup.find(class_='next') != None):
        i += 1
        if i % 5 == 0:               # just to have an idea of the progess of the loop
            print("....", i, sep='')
        
        # Find attributes of all the book of the current page and
        # add them to the list
        books += find_attrs(short_link, nextsoup)

        # Move to the next page
        nextbutton = nextsoup.find(class_='next')
        nextlink = link[:36] + nextbutton.find('a')['href']
        nextpage = requests.get(nextlink) 
        nextsoup = BeautifulSoup(nextpage.content, 'html.parser') 
        
    # Find attributes of all the book of the last page and
    # add them to the list
    books += find_attrs(short_link, nextsoup)
    
    return books


def save_csv(data, csv_name):
    '''
    Takes in the book attributes list as data and the name of the csv.
    Saves data into csv file.
    Doesn't return anything.
    '''

    # Define csv column names
    csv_columns = ['Title', 'Stars', 'Img_url', 'Price (pounds)']
    try:
        # Open the csv
        with open(csv_name, 'w') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write the header
            writer.writerow(csv_columns)

            # Write data as rows
            writer.writerows(data)
            
    except IOError:
        print("I/O error")


def main():
    # Connect to target website
    # link = 'http://books.toscrape.com/index.html'
    link = 'http://books.toscrape.com/catalogue/page-1.html'
    page = requests.get(link)

    # Check connection (200 means OK)
    print("Checking connection (it should be 200):", page.status_code)

    # Parse the HTML document
    soup = BeautifulSoup(page.text, 'html.parser')

    # Travel the pages of the web and add the book attributes
    books_attrs = travel_pages(link, soup)

    # Save the list as a csv file
    csv_name = 'scraping.csv'
    save_csv(books_attrs, csv_name)


main()
