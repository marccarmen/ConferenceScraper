import sys
import getopt
from datetime import date


def usage():
    print("python -l <LANGUAGE> -y <YEAR>")


def run(argv):
    lang = "eng"
    year = str(date.today().year)
    month = "04" if date.today().month > 4 and date.today().month < 10 else "10"
    verbose = False

    try:
        opts, args = getopt.getopt(argv, "lymh:v", ["language=", "year=", "month="])
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
        elif opt in ("-y", "--year"):
            year = arg
        elif opt in ("-m", "--month"):
            month = arg
        elif opt == "-v":
            verbose = True
        else:
            assert False, "unhandled option"
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

    start_url = "https://www.churchofjesuschrist.org/study/general-conference/%s/%s?lang=%s" % (year, month, lang)
    print("Begin scraping %s/%s in %s ( %s )" % (month, year, lang, start_url))
