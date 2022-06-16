import sys
import getopt
from datetime import date
import re
import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize, word_tokenize
import simplemma


# provide the usage
def usage():
    print("python -l <LANGUAGE> -y <YEAR> -m <MONTH> -o <OUTPUT>")


def run(argv):
    """
    # Languages that don't support tokenization and lemmatization
        "zho": {
            "iso_name": "Chinese (Mandarin)",
            "iso_one": "zh"
        },
        "jpn": {
            "iso_name": "Japanese",
            "iso_one": "ja"
        },
    # Languages with no translation available
        "bik": {
            "iso_name": "Bikol",
            "iso_one": ""
        },
    """
    # ISO 639 information
    available_languages = {
        "bul": {
            "iso_name": "Bulgarian",
            "iso_one": "bg"
        },
        "ceb": {
            "iso_name": "Cebuano",
            "iso_one": ""
        },
        "deu": {
            "iso_name": "German",
            "iso_one": "de"
        },
        "eng": {
            "iso_name": "English",
            "iso_one": "en"
        },
        "spa": {
            "iso_name": "Spanish",
            "iso_one": "es"
        },
        "fra": {
            "iso_name": "French",
            "iso_one": "fr"
        },
        "hil": {
               "iso_name": "Hiligaynon",
               "iso_one": ""
        },
        "ilo": {
            "iso_name": "Ilokano",
            "iso_one": ""
        },
        "kor": {
            "iso_name": "Korean",
            "iso_one": "ko"
        },
        "ita": {
            "iso_name": "Italian",
            "iso_one": "it"
        },
        "por": {
            "iso_name": "Portuguese",
            "iso_one": "pt"
        },
        "rus": {
            "iso_name": "Russian",
            "iso_one": "ru"
        },
        "smo": {
            "iso_name": "Samoan",
            "iso_one": "sm"
        },
        "tgl": {
            "iso_name": "Tagalog",
            "iso_one": "tl"
        },
        "ton": {
            "iso_name": "Tongan",
            "iso_one": "to"
        }
    }
    # ISO 639-2 Code
    lang = "eng"
    # four digit year, two four digit years separated by -, list of four digit year separated by comma
    year = str(date.today().year)
    # should be 04, 10, or 04,10
    month = "04,10"
    # by default output prints to the console
    output = None

    verbose = False

    # process the input from the command line
    try:
        opts, args = getopt.getopt(argv, "l:y:m:o:hv", ["language=", "year=", "month=", "output="])
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
            if lang not in available_languages.keys():
                assert False, "Language unavailable. Please choose from %s" % available_languages.keys()
        elif opt in ("-y", "--year"):
            year = arg
        elif opt in ("-m", "--month"):
            month = arg
        elif opt == "-v":
            verbose = True
        elif opt in ("-o", "--output"):
            output = arg
        else:
            assert False, "unhandled option"

    if verbose:
        print("RUNNING IN VERBOSE")

    # check the years variable and process as needed
    years = []
    if m := re.match(r"(\d\d\d\d)-(\d\d\d\d)", year):
        start_year = int(m.group(1))
        end_year = int(m.group(2))
        while start_year <= end_year:
            years.append(str(start_year))
            start_year += 1
    elif "," in year:
        years = year.split(",")
    elif re.match(r"\d\d\d\d", year):
        years.append(year)

    # check the months variable and process as needed
    months = []
    if "," in month:
        months = month.split(",")
    elif re.match(r"\d\d", month):
        if month == "04" or month == "10":
            months.append(month)
        else:
            month = None
    else:
        month = None

    # exit the script if there are invalid arguments
    arg_error = False
    if lang is None:
        arg_error = True
        print("No language is specified")
    if years is None:
        arg_error = True
        print("No year is specified")
    if len(years) == 0:
        arg_error = True
        print("Invalid year specified")
    if month is None:
        arg_error = True
        print("No month specified")
    if arg_error:
        usage()
        sys.exit(2)

    # the final dictionaries we are going to output. Will contain a word/lemma as a key along with a count
    word_list = {}
    lemma_list = {}

    # Get the url setup
    lang_url = lang
    site_url = "https://www.churchofjesuschrist.org"
    language_data = simplemma.load_data(available_languages[lang]["iso_one"])

    # iterate over one or more years
    for year in years:
        # iterate over one or more months
        for month in months:
            print("Processing %s %s" % (month, year))
            base_url = "%s/study/general-conference/%s/%s?lang=%s" % (site_url, year, month, lang_url)
            if verbose:
                print("Begin scraping %s/%s in %s ( %s )" % (month, year, lang_url, base_url))

            # load the URL based on the input
            base_page = requests.get(base_url)

            # load the page HTML into beautiful soup
            base_soup = BeautifulSoup(base_page.content, "html.parser")

            # get a list of all of the talks
            # TODO class could change...update code to use different selector
            talks = base_soup.findAll("a", class_="listTile-WHLxI")

            # these variables are only used for providing progress update
            talk_count = 0
            talk_total = len(talks)

            # iterate over each talk URL
            for talk_link in talks:
                talk_count += 1
                print("Processing talk %d of %d" % (talk_count, talk_total))
                talk_url = talk_link["href"]
                # the name of the URL always ends with digits and then the last name of the speaker
                if re.search(r"/study/general-conference/\d\d\d\d/\d\d/\d+.*", talk_url):
                    talk_url = "%s?lang=%s" % (talk_url, lang_url)
                    if verbose:
                        print("PROCESSING: %s " % talk_url)
                    # load the talk page and convert to a BeautifulSoup object
                    talk_page = requests.get("%s%s" % (site_url, talk_url))
                    talk_soup = BeautifulSoup(talk_page.content, "html.parser")
                    # Get the talk metadata
                    title = talk_soup.find("title").text
                    speaker = \
                        talk_soup.find("p", class_="author-name").text if talk_soup.find("p", class_="author-name") \
                        else ""
                    role = \
                        talk_soup.find("p", class_="author-role").text if talk_soup.find("p", class_="author-role") \
                        else ""
                    summary = talk_soup.find("p", class_="kicker").text if talk_soup.find("p", class_="kicker") \
                        else ""
                    if verbose:
                        print("%s\n%s\n%s\n%s" % (title, speaker, role, summary))

                    talk_paragraphs = talk_soup.findAll("p", id=re.compile(".*"))
                    # iterate over all the paragraphs looking for p# or title# which are the text of the talk
                    for talk_para in talk_paragraphs:
                        if "id" in talk_para.attrs and \
                                (re.search(r"^p\d+$", talk_para["id"]) or re.search(r"^title\d+$", talk_para["id"])):
                            paragraph = talk_para.text
                            if verbose:
                                print(paragraph)
                            sentences = sent_tokenize(paragraph)
                            for sentence in sentences:
                                if sentence:
                                    words = word_tokenize(sentence)
                                    for word in words:
                                        if len(word) == 1 and re.search(r"\W", word):
                                            continue
                                        lemma = None
                                        if language_data is not None and len(language_data) > 0:
                                            lemma = simplemma.lemmatize(word, language_data)
                                        if verbose:
                                            print("%s -> %s" % (word, lemma))

                                        if word not in word_list:
                                            word_list[word] = 0
                                        word_list[word] += 1

                                        if lemma is not None:
                                            if lemma not in lemma_list:
                                                lemma_list[lemma] = 0
                                            lemma_list[lemma] += 1
                else:
                    if verbose:
                        print("SKIPPING: %s" % talk_url)

    if word_list is not None or lemma_list is not None:
        if word_list is not None:
            word_list = {k: v for k, v in sorted(word_list.items(), key=lambda item: item[1], reverse=True)}

        if lemma_list is not None:
            lemma_list = {k: v for k, v in sorted(lemma_list.items(), key=lambda item: item[1], reverse=True)}

        print_count = 0
        word_keys = list(word_list.keys())
        lemma_keys = list(lemma_list.keys())
        max_count = max(len(word_keys), len(lemma_keys))
        f = None
        header = "WORD\tWORD COUNT\t\tLEMMA\tLEMMA COUNT\n"
        if output is not None:
            f = open(output, mode="w", encoding="utf-8")
            f.write(header)
        else:
            print(header)
        while print_count <= max_count:
            word = word_keys[print_count] if print_count < len(word_keys) else ""
            word_count = word_list[word] if word != "" else ""
            lemma = lemma_keys[print_count] if print_count < len(lemma_keys) else ""
            lemma_count = lemma_list[lemma] if lemma != "" else ""
            line = "%s\t%s\t\t%s\t%s" % (word, word_count, lemma, lemma_count)
            if f is not None and output is not None:
                f.write("%s%s" % (line, "\n"))
            else:
                print(line)
            print_count += 1
        if f is not None and output is not None:
            f.close()
