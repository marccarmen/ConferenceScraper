import sys
import getopt
from datetime import date
import re
import requests
from bs4 import BeautifulSoup
from nltk import sent_tokenize, word_tokenize
import simplemma
from transliterate import translit, get_available_language_codes
from translate import Translator

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

    show_lemma = False
    show_transliteration = False
    show_translation = False
    min_translation = 0
    max_translation = sys.maxsize
    verbose = False

    # process the input from the command line
    try:
        opts, args = getopt.getopt(argv, "l:y:m:o:hv", ["language=", "year=", "month=", "output=", "verbose", "includeLemma", "includeTransliteration", "translateMin=", "translateMax="])
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
            year = arg.replace(" ", "")
        elif opt in ("-m", "--month"):
            month = arg.replace(" ", "")
        elif opt == ("-v", "--verbose"):
            verbose = True
        elif opt in ("-o", "--output"):
            output = arg
        elif opt == "--includeLemma":
            show_lemma = True
        elif opt == "--includeTransliteration":
            show_transliteration = True
        elif opt == "--translateMin":
            min_translation = int(arg)
            show_translation = True if min_translation > 0 else False
        elif opt == "--translateMax":
            max_translation = int(arg)
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

    # turn off translation if the language is english
    show_translation = show_translation and lang != "eng"

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

    # the final dictionaries we are going to output. Will contain a word as a key along with a count
    word_list = {}

    # Get the url setup
    lang_url = lang
    site_url = "https://www.churchofjesuschrist.org"

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

            # get a list of all the talks
            talks = base_soup.findAll("a", {"class": lambda l: l and l.startswith('listTile')})

            # these variables are only used for providing progress update
            talk_count = 0
            talk_total = len(talks)

            # iterate over each talk URL
            for talk_link in talks:
                talk_count += 1
                print("Processing talk %d of %d" % (talk_count, talk_total))
                talk_url = talk_link["href"]
                # the name of the URL always ends with digits and then the last name of the speaker

                talk_url = "%s?lang=%s" % (talk_url, lang_url)
                if verbose:
                    print("PROCESSING: %s " % talk_url)
                # load the talk page and convert to a BeautifulSoup object
                talk_page = requests.get("%s%s" % (site_url, talk_url))
                talk_soup = BeautifulSoup(talk_page.content, "html.parser")
                # Get the talk metadata
                title = talk_soup.find("title").text
                speaker = \
                    talk_soup.find("p", class_="author-name").text if talk_soup.find("p", class_="author-name") else ""
                role = \
                    talk_soup.find("p", class_="author-role").text if talk_soup.find("p", class_="author-role") else ""
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

                                    if word not in word_list:
                                        word_list[word] = 0
                                    word_list[word] += 1

    if word_list is not None:
        iso_one = available_languages[lang]["iso_one"]

        transliteration_languages = None
        if show_transliteration:
            transliteration_languages = get_available_language_codes()
        show_transliteration = show_transliteration and transliteration_languages is not None and iso_one in transliteration_languages

        language_data = None
        if show_lemma:
            language_data = simplemma.load_data(iso_one)
        show_lemma = show_lemma and language_data is not None

        translator = None
        if show_translation:
            translator = Translator(provider="mymemory", to_lang="en", from_lang=iso_one)
        show_translation = show_translation and translator is not None

        header = "WORD COUNT\tWORD"
        if show_transliteration:
            header = "%s\t%s" % (header, "TRANSLITERATION")
        if show_lemma and language_data is not None and len(language_data) > 0:
            header = "%s\t%s" % (header, "LEMMA")
        if show_translation:
            header = "%s\t%s" % (header, "TRANSLATION")
        header = "%s\n" % header
        f = None
        if output is not None:
            f = open(output, mode="w", encoding="utf-8")
            f.write(header)
        else:
            print(header)

        word_list = {k: v for k, v in sorted(word_list.items(), key=lambda item: item[1], reverse=True)}
        for word in word_list:
            output_line = "%s\t%s" % (word_list[word], word)

            transliteration = None
            if show_transliteration:
                transliteration = translit(word, iso_one, reversed=True)
                output_line = "%s\t%s" % (output_line, transliteration if transliteration is not None else "")

            lemma = None
            if show_lemma and language_data is not None and len(language_data) > 0:
                lemma = simplemma.lemmatize(word, language_data)
                output_line = "%s\t%s" % (output_line, lemma if lemma is not None else "")

            translation = None
            if show_translation and max_translation > word_list[word] > min_translation > 0:
                translation = translator.translate(word)
                output_line = "%s\t%s" % (output_line, translation if translation is not None else "")

            if output_line is not None:
                if output is not None:
                    f.write("%s%s" % (output_line, "\n"))
                else:
                    if output_line is not None:
                        print(output_line)