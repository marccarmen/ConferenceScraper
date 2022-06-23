import sys
import os
import getopt
from datetime import date
import re
import random
# Progress bar
from tqdm import tqdm
# Web requests
import requests
# Web scraping
from bs4 import BeautifulSoup
# Transliteration
from transliterate import translit, get_available_language_codes
# Translation
from googletrans import Translator
# Linguistic Processing
import stanza
# Linguistic processing for other languages
from nltk import sent_tokenize, word_tokenize
import simplemma


# provide the usage
def usage():
    print("ConferenceScraper [-l <LANGUAGE>] [-y <YEAR>] [-m <MONTH>] [-o <OUTPUT>] "
          "[--includeLemma] [--includeTransliteration] [--translateMin <NUM>] [--translateMax <NUMBER>] "
          "[--hideCount] [-v] [-h] [--showPOS] [--showSentence] [--cache]")
    print("SUPPORTED LANGUAGES: bul, deu, eng, spa, fra, kor, ita, por, rus")
    print("SUPPORTED YEAR FORMATS: yyyy or yyyy-yyyy or yyyy,yyyy,yyyy")
    print("SUPPORTED MONTHS: 04 or 10 or 04,10")
    print("DEFAULT: ConferenceScraper -l eng -y <CURRENT_YEAR> -m 04,10")
    print("EXAMPLE Spanish from 2019-2021 to file: ConferenceScraper -l spa -y 2019-2021 -o output.txt")


def run(argv):
    """
    # Unsupported by stanza

    """
    # ISO 639 information
    available_languages = {
        "bul": {
            "iso_name": "Bulgarian",
            "iso_one": "bg",
            "pos": True,
            "lemma": True
        },
        "deu": {
            "iso_name": "German",
            "iso_one": "de",
            "pos": True,
            "lemma": True
        },
        "eng": {
            "iso_name": "English",
            "iso_one": "en",
            "pos": True,
            "lemma": True
        },
        "spa": {
            "iso_name": "Spanish",
            "iso_one": "es",
            "pos": True,
            "lemma": True
        },
        "fra": {
            "iso_name": "French",
            "iso_one": "fr",
            "pos": True,
            "lemma": True
        },
        "kor": {
            "iso_name": "Korean",
            "iso_one": "ko",
            "pos": True,
            "lemma": True
        },
        "ita": {
            "iso_name": "Italian",
            "iso_one": "it",
            "pos": True,
            "lemma": True
        },
        "por": {
            "iso_name": "Portuguese",
            "iso_one": "pt",
            "pos": True,
            "lemma": True
        },
        "rus": {
            "iso_name": "Russian",
            "iso_one": "ru",
            "pos": True,
            "lemma": True
        },
        "zho": {
            "iso_name": "Chinese (Mandarin)",
            "iso_one": "zh",
            "pos": True,
            "lemma": True
        },
        "jpn": {
            "iso_name": "Japanese",
            "iso_one": "ja",
            "pos": True,
            "lemma": True
        },
        "ceb": {
            "iso_name": "Cebuano",
            "iso_one": "",
            "pos": False,
            "lemma": False
        },
        "hil": {
            "iso_name": "Hiligaynon",
            "iso_one": "",
            "pos": False,
            "lemma": False
        },
        "ilo": {
            "iso_name": "Ilokano",
            "iso_one": "",
            "pos": False,
            "lemma": False
        },
        "smo": {
            "iso_name": "Samoan",
            "iso_one": "sm",
            "pos": False,
            "lemma": False
        },
        "tgl": {
            "iso_name": "Tagalog",
            "iso_one": "tl",
            "pos": False,
            "lemma": False
        },
        "ton": {
            "iso_name": "Tongan",
            "iso_one": "to",
            "pos": False,
            "lemma": False
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
    hide_count = False
    min_translation = 0
    max_translation = None
    verbose = False
    show_pos = False
    show_sentence = False
    cache_directory = None

    # process the input from the command line
    try:
        opts, args = getopt.getopt(argv, "l:y:m:o:hv", ["language=", "year=", "month=", "output=", "verbose",
                                                        "includeLemma", "includeTransliteration", "translateMin=",
                                                        "translateMax=", "hideCount", "showPOS", "showSentence",
                                                        "cache="])
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
        elif opt == "--hideCount":
            hide_count = True
        elif opt == "--showPOS":
            show_pos = True
        elif opt == "--showSentence":
            show_sentence = True
        elif opt == "--cache":
            if os.path.exists(arg) and not os.path.isdir(arg):
                cache_directory = arg
            else:
                assert False, "Cache directory doesn't exist"
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

    if min_translation > 0 and max_translation is None:
        max_translation = min_translation

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

    # Get the 639-1 code for the language
    iso_one = available_languages[lang]["iso_one"]
    pos_support = available_languages[lang]["pos"]

    transliteration_languages = None
    if show_transliteration:
        transliteration_languages = get_available_language_codes()
    show_transliteration = show_transliteration and transliteration_languages is not None and iso_one in transliteration_languages

    # Setup stanza/NLTK for the target language
    nlp = None
    language_data = None
    if pos_support:
        stanza.download(iso_one)
        nlp = stanza.Pipeline(lang=iso_one, processors='tokenize,pos,lemma')
    else:
        if show_lemma:
            language_data = simplemma.load_data(iso_one)

    # the final dictionaries we are going to output. Will contain a word as a key along with a count
    word_list = {}
    word_features = {}

    # Get the url setup
    lang_url = lang
    site_url = "https://www.churchofjesuschrist.org"

    transliteration_languages = None
    if show_transliteration:
        transliteration_languages = get_available_language_codes()
    show_transliteration = show_transliteration and transliteration_languages is not None and iso_one in transliteration_languages

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

            full_text_xml = ""
            # iterate over each talk URL
            for talk_link in tqdm(talks, unit=" talks"):
                talk_count += 1
                # print("Processing talk %d of %d" % (talk_count, talk_total))
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

                        if pos_support:
                            word_list, word_features = process_paragraph_stanza(nlp, paragraph, word_list, word_features, iso_one, show_transliteration)
                        else:
                            word_list, word_features = process_paragraph_nltk(language_data, paragraph, word_list, word_features, iso_one, show_lemma, show_transliteration)

    if word_list is not None:
        print_output(output, iso_one, word_list, word_features,
                     hide_count, show_transliteration, show_lemma,
                     show_translation, show_pos, show_sentence,
                     max_translation, min_translation
                     )


def get_transliteration(word, iso_one, show_transliteration):
    return translit(word, iso_one, reversed=True) if show_transliteration else ""


def process_paragraph_nltk(language_data, paragraph, word_list, word_features, iso_one, show_lemma, show_transliteration):
    sentences = sent_tokenize(paragraph)
    for sentence in sentences:
        if sentence:
            words = word_tokenize(sentence)
            for word in words:
                if len(word) == 1 and re.search(r"\W*", word):
                    continue

                lcase = word.lower()

                if lcase not in word_list:
                    word_list, word_features = create_lists(lcase, word_list, word_features, word, sentence,
                                                            "", "", "", "", simplemma.lemmatize(word, language_data) if show_lemma and language_data  else "",
                                                            get_transliteration(word, iso_one, show_transliteration))
                else:
                    word_list, word_features = update_lists(lcase, word_list, word_features, word, sentence)
    return word_list, word_features


def process_paragraph_stanza(nlp, paragraph, word_list, word_features, iso_one, show_transliteration):
    exclude_pos = ["PUNCT", "NUM", "AUX", "PROPN"]
    doc = nlp(paragraph)
    for i, sentence in enumerate(doc.sentences):
        for word in sentence.words:
            if word.pos not in exclude_pos:
                lcase = word.text.lower()
                if lcase not in word_list:
                    word_list, word_features = create_lists(lcase, word_list, word_features, word.text, sentence.text,
                                                            word.pos, word.upos, word.xpos, word.feats, word.lemma,
                                                            get_transliteration(word.text, iso_one, show_transliteration))
                else:
                    word_list, word_features = update_lists(lcase, word_list, word_features, word, sentence.text)
    return word_list, word_features


def create_lists(lcase, word_list, word_features, word, sentence, pos, upos, xpos, feats, lemma, transliteration):
    word_list[lcase] = 1

    word_features[lcase] = {
        'raw': [word],
        'sentences': [sentence],
        'pos': pos,
        'upos': upos,
        'xpos': xpos,
        'feats': feats,
        'lemma': lemma,
        'transliteration': transliteration
    }
    return word_list, word_features


def update_lists(lcase, word_list, word_features, word, sentence):
    word_list[lcase] += 1
    if word not in word_features[lcase]['raw']:
        word_features[lcase]['raw'].append(word)
    if sentence not in word_features[lcase]['sentences']:
        word_features[lcase]['sentences'].append(sentence)
    return word_list, word_features


def print_output(output, iso_one, word_list, word_features,
                 hide_count, show_transliteration, show_lemma,
                 show_translation, show_pos, show_sentence,
                 max_translation, min_translation):
    translator = None
    if show_translation:
        translator = Translator()
    show_translation = show_translation and translator is not None

    header = "WORD"
    if not hide_count:
        header = "WORD COUNT\t%s" % header
    if show_transliteration:
        header = "%s\tTRANSLITERATION" % header
    if show_lemma:
        header = "%s\tLEMMA" % header
    if show_translation:
        header = "%s\tTRANSLATION" % header
    if show_pos:
        # header = "%s\tPOS\tUPOS\tXPOS\tFEATURES" % header
        header = "%s\t\"Part of Speech\"" % header
    if show_sentence:
        header = "%s\tSENTENCE" % header
    header = "%s\n" % header
    f = None
    if output is not None:
        f = open(output, mode="w", encoding="utf-8")
        f.write(header)
    else:
        print(header)

    word_list = {k: v for k, v in sorted(word_list.items(), key=lambda item: item[1], reverse=True)}
    for word in tqdm(word_list, unit=" words", disable=True if output is None else False):
        output_line = "%s\t%s" % (word_list[word], word)

        features = word_features[word]

        if show_transliteration:
            output_line = "%s\t%s" % (output_line, features['transliteration'] if features['transliteration'] is not None else "")

        if show_lemma:
            output_line = "%s\t%s" % (output_line, features['lemma'] if features['lemma'] is not None else "")

        if show_translation and max_translation >= word_list[word] >= min_translation > 0:
            translation = translator.translate(word, dest="en").text
            output_line = "%s\t%s" % (output_line, translation if translation is not None else "")

        if show_pos:
            # output_line = "%s\t%s\t%s\t%s\t%s" % (output_line, features['pos'], features['upos'], features['xpos'], features['feats'])
            output_line = "%s\t%s" % (output_line, features['pos'])

        if show_sentence:
            random_int = random.randint(1, len(features['sentences'])) - 1
            output_line = "%s\t\"%s\"" % (output_line, features['sentences'][random_int])

        if output_line is not None:
            if output is not None:
                f.write("%s%s" % (output_line, "\n"))
            else:
                if output_line is not None:
                    print(output_line)


def get_filename(lang, year, month):
    return "%s_%s_%s.txt" % (lang, year, month)


def check_cache_exists(cache, filename):
    return os.path.exists(os.path.join(cache, filename))
