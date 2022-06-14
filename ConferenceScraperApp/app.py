import sys
import getopt
from datetime import date
import requests
from bs4 import BeautifulSoup
import re
from nltk import sent_tokenize, word_tokenize
#import simplemma

def usage():
    print("python -l <LANGUAGE> -y <YEAR> -m <MONTH>")


def run(argv):
    #ISO 639 information
    AVAILABLE_LANGUAGES = {
        "en" : {
            "iso_name": "English",
            "iso_three": "eng"},
        "es" : {
            "iso_name": "Spanish",
            "iso_three": "spa"
        },
        "bg": {
            "iso_name": "Bulgarian",
            "iso_three": "bul"
        }
    }
    #eng/spa/bul
    lang = "en"
    #four digit year
    year = str(date.today().year)
    #should be 04 or 10
    month = "04" if date.today().month > 4 and date.today().month < 10 else "10"

    verbose = False

    try:
        opts, args = getopt.getopt(argv, "l:y:m:hv", ["language=", "year=", "month="])
    except getopt.GetoptError as err:
        print(err)
        usage()
        sys.exit(2)
    for opt, arg in opts:
        if opt == "-h":
            usage()
            sys.exit()
        elif opt in ("-l", "--language"):
            lang = arg
            if lang not in AVAILABLE_LANGUAGES.keys():
                assert False, "Language unavailable. Please choose from %s" % AVAILABLE_LANGUAGES.keys()
        elif opt in ("-y", "--year"):
            year = arg
            if int(year) < 1971 or int(year) > date.today().year:
                assert False, "Invalid year. Please enter a 4 digit year between 1971 and %s" %str(date.today().year)
        elif opt in ("-m", "--month"):
            month = arg
            if month != "04" or month != "10":
                assert False, "Invalid month option. Please use 04 or 10"
        elif opt == "-v":
            verbose = True
        else:
            assert False, "unhandled option"

    if verbose:
        print("RUNNING IN VERBOSE")

    arg_error = False
    if lang is None:
        arg_error = True
        print("No language is specified")
    if year is None:
        arg_error = True
        print("No year is specified")
    if arg_error:
        usage()
        sys.exit(2)

    lang_url = AVAILABLE_LANGUAGES[lang]["iso_three"]
    site_url = "https://www.churchofjesuschrist.org"
    base_url = "%s/study/general-conference/%s/%s?lang=%s" % (site_url, year, month, lang_url)
    if verbose:
        print("Begin scraping %s/%s in %s ( %s )" % (month, year, lang_url, base_url))

    #load the URL based on the input
    base_page = requests.get(base_url)

    #load the page HTML into beautiful soup
    base_soup = BeautifulSoup(base_page.content, "html.parser")

    #get a list of all of the talks
    #TODO Make sure that the class is going to be the same no matter what or find a different way to distinguish
    talks = base_soup.findAll("a", class_="listTile-WHLxI")

    #langdata = simplemma.load_data("bg")

    #iterate over each talk URL
    for talk_link in talks:
        talk_url = talk_link["href"]
        #the name of the URL always ends with digits and then the last name of the speaker
        if re.search("/study/general-conference/2022/04/\d+.*", talk_url):
            talk_url = "%s?lang=%s" % (talk_url, lang_url)
            if verbose:
                print("PROCESSING: %s " % talk_url)
            #load the talk page and convert to a BeautifulSoup object
            talk_page = requests.get("%s%s" % (site_url, talk_url))
            talk_soup = BeautifulSoup(talk_page.content, "html.parser")
            #Get the talk meta data
            title = talk_soup.find("title").text
            speaker = talk_soup.find("p", class_="author-name").text if talk_soup.find("p", class_="author-name") else ""
            role = talk_soup.find("p", class_="author-role").text if talk_soup.find("p", class_="author-role") else ""
            summary = talk_soup.find("p", class_="kicker").text if talk_soup.find("p", class_="kicker") else ""
            if verbose:
                print("%s\n%s\n%s\n%s" % (title, speaker, role, summary))
            paragraphs = []
            talk_paragraphs = talk_soup.findAll("p", id=re.compile(".*"))
            #iterate over all of the paragraphs looking for p# or title# which are the text of the talk
            for talk_para in talk_paragraphs:
                if "id" in talk_para.attrs and (re.search("^p\d+$", talk_para["id"]) or re.search("^title\d+$", talk_para["id"])):
                    paragraph = talk_para.text
                    if verbose:
                      print(paragraph)
                    sentences = sent_tokenize(paragraph)
                    for sentence in sentences:
                        if sentence:
                            words = word_tokenize(sentence)
                            for word in words:
                                #lemma = simplemma.lemmatize(word, langdata)
                                lemma = ""
                                print("%s -> %s" % (word, lemma))
        else:
            if verbose:
                print("SKIPPING: %s" %talk_url)