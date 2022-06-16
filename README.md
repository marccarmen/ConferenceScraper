# ConferenceScraper

This project was started as a way to generate word and lemma lists based on 
General Conference talks from The Church of Jesus Christ of Latter-day Saints. 
The lists are ordered by frequency in descending order. The purpose of these 
lists is to generate word lists related to The Church of Jesus Christ of 
Latter-day Saints for language learning purposes. 
In linguistics, lemmatization is "the process of grouping together the inflected 
forms of a word, so they can be analysed as a single item, identified by the 
word's lemma, or dictionary form." (https://en.wikipedia.org/wiki/Lemmatisation) 
The simplemma Python library is being used for lemmatization and not all 
languages are supported.

# Usage

The script has been developed using Python 3.10. There are several libraries 
that are required for the script. Please see 
[Required Libraries](#required-libraries) and 
[NLTK Requirements](#nltk-requirements) for additional details. The script can 
be run with the following parameters:
<li><code>-l</code> or <code>--language</code> which is the ISO 639-2 Code 
(e.g., <code>eng</code> or <code>spa</code>
for the language you want to process</li>
<li><code>-y</code> or <code>--year</code> is the year(s) you want to process. 
This can be a single 4-digit year (e.g., <code>2022</code>), a range (e.g., 
<code>2021-2022</code>), or a comma separated list 
(e.g., <code>2019,2021</code>)</li>
<li><code>-m</code> or <code>--month</code> has three options <code>04</code>,
<code>10</code>, or <code>04,10</code></li>
<li><code>-o</code> or <code>--output</code> will be the path to the text file
where the data should be saved. If no output file is specified then the 
data will be output to the console</li>

The default parameters would make the command look like the following 
command:<br>
<code>python ConferenceScraperApp/_main_.py -l eng -m 04,10 -y <CURRENT_YEAR></code>

## Optional Parameters

<li><code>--includeLemma</code> By default the lemma is not included. 
If this parameter is included then the list of lemmas will be included in the output</li>

# Output
The output of this script is a tab separated list that looks like this<br>

| Word | Word Count |     | Lemma | Lemma Count |
|------|------------|-----|-------|-------------|
| the  | 2763       |     | the   | 2089        |
| and  | 1977	     |     | and   | 2067        |
| of	| 1817	     |     | be	   | 1840        |
| to   | 1735       |     | of    | 1826        |
| in   | 959	     |     | to    | 1754        |
| a    | 738	     |     | we	   | 1196        |
<br>
Lemma/Lemma Count are only included if the <code>--includeLemma</code> parameter
is set. The Word/Word Count and Lemma/Lemma Count are not related. I output them this
way so that all the data can be easily imported into a spreadsheet and 
manipulated as needed. Instructions for importing a txt file into Microsoft 
Excel are available https://support.microsoft.com/en-us/office/import-or-export-text-txt-or-csv-files-5250ac4c-663c-47ce-937b-339e391393ba 

I have added an output folder with some sample output files. The files that 
end in <code>.txt</code> are the tab-delimited files and would need to be viewed 
in a text editor or imported into a spreadsheet program. The files that end in 
<code>.csv</code> are comma separated files and should be able to be opened 
directly into most spreadsheet programs.
# Supported Language Details

A list of the most common languages spoken by members of The Church of Jesus 
Christ of Latter-day Saints can be found here 
https://www.churchofjesuschrist.org/study/ensign/1999/12/news-of-the-church/languages-spoken-by-members?lang=eng 
It is possible that General Conference is available in other languages. 
Additional languages could be added to the script by updating the 
<code>available_languages</code> variable. ISO 639 codes are used and more 
information can be found here https://www.loc.gov/standards/iso639-2/php/code_list.php

The script currently supports the following languages
<li>Bulgarian</li>
<li>Cebuano</li>
<li>German</li>
<li>English</li>
<li>Spanish</li>
<li>French</li>
<li>Hiligaynon</li>
<li>Ilokano</li>
<li>Korean</li>
<li>Italian</li>
<li>Portuguese</li>
<li>Russian</li>
<li>Samoan</li>
<li>Tagalog</li>
<li>Tongan</li>
<br>
General Conference proceedings are available in the following languages but are 
not supported by the script because they cannot be easily split into paragraphs 
and words.
<li>Mandarin</li>
<li>Japanese</li>
<br>
Lemmatization is not supported for the following languages
<li>Cebuano</li>
<li>Hiligaynon</li>
<li>Ilokano</li>
<li>Korean</li>
<li>Samoan</li>
<li>Tagalog</li>
<li>Tongan</li>

# Required Libraries

The uses several libraries. Please use the commands below to install the 
necessary libraries.<br>
<code>pip install beautifulsoup4</code><br>
<code>pip install nltk</code><br>
<code>pip install simplemma</code><br>
<code>pip install requests</code><br>

# NLTK Requirements

After you have installed NLTK you will need to install the following 
resources:
<br>
<code>import nltk</code><br>
<code>nltk.download('punkt')</code>

# Known Issues

- [X] Compatible with talks 2019 and on. System is filtering out older talks
  due to the filename format<br>
- [X] Year and Month parameters support a variety of formats. It needs more
  error checking to prevent issues. Specifically spaces should be stripped

# Potential Features
- [ ] More linguistic processing. Part of speech
- [ ] Executable version so anyone can use it without programming knowledge