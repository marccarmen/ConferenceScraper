# ConferenceScraper

This project was started as a way to generate word list based on 
General Conference talks from The Church of Jesus Christ of Latter-day Saints 
for language learning purposes. The list is ordered by frequency in 
descending order.<br><br> This script uses several common techniques for 
linguistic processing including segmentation, tokenization, lemmatization, 
and part of speech tagging.

Segmentation and tokenization are the process of splitting large chunks of 
data into smaller chunks. In this case, segmentation is the process of breaking
the paragraphs into sentences. Tokenization is the process of breaking each
sentence into words.

Lemmatization is "the process of grouping together the inflected 
forms of a word, so they can be analysed as a single item, identified by the 
word's lemma, or dictionary form." (https://en.wikipedia.org/wiki/Lemmatisation) 
The simplemma Python library is being used for lemmatization and not all 
languages are supported.

Part of speech tagging is the process of determining the part of speech of each 
word. This is useful for this script because there are certain words that 
are very frequent and may not be useful in the output. The script currently 
excludes punctuation, proper nouns, numbers, and auxiliary words

The first time you run the script on a language that Stanza supports it will
download a language model for that language. This can take some time depending 
on the size of the model. Once that has been downloaded you will not need
to download that information for that language model again.

In a future update, I plan to add a caching mechanism that will save a local copy 
of the conference years that the user processes. This should speed up the process.

# Usage

The script has been developed using Python 3.10. There are several libraries 
that are required for the script. Please see 
[Required Libraries](#required-libraries)  for additional details. The script can 
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
If this parameter is included then the list of lemmas will be included 
in the output.</li>
<li><code>--includeTransliteration</code> By default the transliteration is 
not included. If this parameter is included and the target language is 
supported then the transliteration of the word will be included
in the output.</li>
<li><code>--translateMin=NUMBER</code>By default the translation is not
included. If this parameter is included along with an argument greater than 
0 and the target language is not English then the program will attempt
to provide a translation for any word that has a count larger than
<code>translationReq</code>.</li>
<li><code>--translateMax=NUMBER</code>By default this is set to the whatever
<code>translateMin</code> is set to. If set then only words that have a count between 
<code>translateMin</code> and <code>translateMax</code> will be 
translated.</li>
<li><code>--hideCount</code> will hide the count column in the output</li>
<li><code>--showPOS</code> includes the part of speech for each word</li>
<li><code>--showSentence</code> include a randomly chosen sample sentence for each word</li>


# Output
The output of this script is a tab separated list that looks like the table
below if all the fields are included<br>

| WORD COUNT | WORD | TRANSLITERATION | LEMMA | TRANSLATION |
|------------|------|-----------------|-------|-------------|
| 2763       | the  |                 |       |             |
| 1977       | and	 |                 |       |             |
| 1817	      | of   |                 |       |             |
| 1735       | to   |                 |       |             |
| 959        | in   |                 |       |             |
| 738        | a	 |                 |       |             |
<br>
TRANSLITERATION is included if <code>--includeTransliteration</code> is set.<br>
LEMMA is only included if <code>--includeLemma</code> is set.<br>
TRANSLATION is only included if <code>--translationMin</code> is set with a number 
greater than 0<br>

The data is output as a tab-delimited file and can be easily imported into 
most spreadsheet programs. Instructions for importing a txt file into Microsoft 
Excel are available https://support.microsoft.com/en-us/office/import-or-export-text-txt-or-csv-files-5250ac4c-663c-47ce-937b-339e391393ba 

I have added an output folder with some sample output files. The files that 
end in <code>.txt</code> are the tab-delimited files and would need to be viewed 
in a text editor or imported into a spreadsheet program. The files that end in 
<code>.csv</code> are comma separated files and should be able to be opened 
directly into most spreadsheet programs.

## How to Use the Output

You can obviously use the output as you see fit. One option would be to import the 
information into an Anki deck to practice the words. In the Output folder there is a file 
named 2019-2022_bul_ankiImport.csv that I created based on the output. I used that to create an
Anki deck that is shared at https://ankiweb.net/shared/info/955133302

# Language Details

A list of the most common languages spoken by members of The Church of Jesus 
Christ of Latter-day Saints can be found here 
https://www.churchofjesuschrist.org/study/ensign/1999/12/news-of-the-church/languages-spoken-by-members?lang=eng 
It is possible that General Conference is available in other languages. 
Additional languages could be added to the script by updating the 
<code>available_languages</code> variable. ISO 639 codes are used and more 
information can be found here https://www.loc.gov/standards/iso639-2/php/code_list.php

## Supported Languages
<li>Bulgarian</li>
<li>English</li>
<li>French</li>
<li>German</li>
<li>Italian</li>
<li>Japanese</li>
<li>Korean</li>
<li>Mandarin</li>
<li>Portuguese</li>
<li>Russian</li>
<li>Spanish</li>
<li>Cebuano</li>
<li>Hiligaynon</li>
<li>Ilokano</li>
<li>Samoan</li>
<li>Tagalog</li>
<li>Tongan</li>

## Transliteration

Transliteration is done using the <code>transliterate</code> library 
(https://github.com/barseghyanartur/transliterate) which supports 
the following languages:
<li>Armenian</li>
<li>Bulgarian (beta)</li>
<li>Georgian</li>
<li>Greek</li>
<li>Macedonian (alpha)</li>
<li>Mongolian (alpha)</li>
<li>Russian</li>
<li>Serbian (alpha)</li>
<li>Ukrainian (beta)</li>

## Translation

Translation is done using the <code>py-googletrans</code> library
(https://github.com/ssut/py-googletrans). The 
translation is only for non-English languages into English. The script takes
a number as input and only those words that have a higher count than 
<code>translationMin</code> will be translated. If no 
<code>translationMax</code> is specified then 
<code>translationMax=translationMin</code>. If the <code>translationMax</code>
is to large the script will take a very long time to complete.

# Required Libraries

The uses several libraries. Please use the commands below to install the 
necessary libraries.<br>
<code>pip install tqdm</code><br>
<code>pip install requests</code><br>
<code>pip install beautifulsoup4</code><br>
<code>pip install googletrans==4.0.0-rc1</code><br>
<code>pip install transliterate</code><br>
<code>pip install stanza</code><br>
<code>pip install nltk</code><br>
<code>pip install simplemma</code><br>
