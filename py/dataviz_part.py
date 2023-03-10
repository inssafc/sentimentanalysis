# -*- coding: utf-8 -*-
"""dataviz part (project).ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1chKMdWW6alrVm9Mz-XaDLwR-GItqiCZk
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
plt.style.use('ggplot')  #style sheet for the plots
import nltk

df = pd.read_excel('/content/amazondataset.xlsx')

df.drop(columns=['countryCode','reviewImages/0','reviewImages/1','reviewImages/2','reviewImages/3',
                 'reviewImages/4','reviewImages/5','reviewImages/6','reviewImages/7','reviewImages/8',
                 'reviewImages/9','reviewImages/10','reviewImages/11','reviewImages/12','reviewUrl',
                 'reviewedIn','productAsin'], axis =1,
                 level=None, inplace=True)

df.isnull().sum(axis=0)

df=df.dropna(subset=['reviewDescription']).reset_index(drop=True)

#merging reviews descriptions with their title
df["reviews"] = df['reviewTitle'] +"-"+ df["reviewDescription"]

df = df.drop(['reviewDescription','reviewTitle'],axis = 1)

from nltk.sentiment import SentimentIntensityAnalyzer
nltk.download('vader_lexicon')
nltk.download('punkt')
from tqdm.notebook import tqdm

sia = SentimentIntensityAnalyzer()

df = df.astype({'reviews':'string'})

nltk.download('averaged_perceptron_tagger')
nltk.download('maxent_ne_chunker')  #Chunking is defined as the process of natural language processing used to identify parts of speech and short phrases present in a given sentence.
nltk.download('words')
encoded = []
for str in df['reviews'] :
  tokens = nltk.word_tokenize(str)
  tagged = nltk.pos_tag(tokens)
  entities = nltk.chunk.ne_chunk(tagged)
  encoded.append(entities)
df['tokinized_reviews'] = encoded
#df.drop('reviewDescription',axis = 1,level=None, inplace=True)

# Run the polarity score on the entire dataset
res = {}
for i, row in tqdm(df.iterrows(), total=len(df)):
    text = row['reviews']
    id = row['position']  #reviewnum
    res[id] = sia.polarity_scores(text)

df_vaders = pd.DataFrame(res).T
df_vaders = df_vaders.reset_index().rename(columns={'index': 'position'})
df_vaders = df_vaders.merge(df, how='left')

ax = sns.barplot(data=df_vaders,x='ratingScore', y='compound')
ax.set_title('Compound Score by Amazon Star Review')
plt.show()

fig, axs = plt.subplots(1, 3, figsize=(12, 3))
sns.barplot(data=df_vaders, x='ratingScore', y='pos', ax=axs[0])
sns.barplot(data=df_vaders, x='ratingScore', y='neu', ax=axs[1])
sns.barplot(data=df_vaders, x='ratingScore', y='neg', ax=axs[2])
axs[0].set_title('Positive')
axs[1].set_title('Neutral')
axs[2].set_title('Negative')
plt.tight_layout()
plt.show()

score = df_vaders["compound"].values
sentiment = []
for i in score:
    if i >= 0.05 :
        sentiment.append('Positive')
    elif i <= -0.05 :
        sentiment.append('Negative')
    else:
        sentiment.append('Neutral')
df_vaders["sentiment"] = sentiment
df_vaders.head()

"""create more graphs ..."""

!pip install pywedge

"""word clouds"""

df_vaders['reviews'] = df_vaders['reviews'].str.lower()

"""some helper functions..."""

import re
from bs4 import BeautifulSoup
from html import unescape

def remove_urls(x):
    cleaned_string = re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', '', str(x), flags=re.MULTILINE)
    return cleaned_string

def unescape_stuff(x):
    soup = BeautifulSoup(unescape(x), 'lxml')
    return soup.text

def deEmojify(x):
    regrex_pattern = re.compile(pattern = "["
        u"\U0001F600-\U0001F64F"  # emoticons
        u"\U0001F300-\U0001F5FF"  # symbols & pictographs
        u"\U0001F680-\U0001F6FF"  # transport & map symbols
        u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           "]+", flags = re.UNICODE)
    return regrex_pattern.sub(r'', x)

def remove_symbols(x):
    cleaned_string = re.sub(r"[^a-zA-Z0-9]+", ' ', x)
    return cleaned_string

def unify_whitespaces(x):
    cleaned_string = re.sub(' +', ' ', x)
    return cleaned_string

#Swifter is a package that tries to efficiently apply any function to a
# Pandas Data Frame or Series object in the quickest available method

!pip install swifter

import re

def eliminate_contraction(text):
    # Use regular expressions to replace "doesn't" and "don't" with "does not" and "do not" respectively
    text = re.sub("doesn't", "does not", text)
    text = re.sub("didn't", "did not", text)
    text = re.sub("don't", "do not", text)
    return text

import swifter
df_vaders['reviews'] = df_vaders['reviews'].swifter.apply(eliminate_contraction)

import swifter

#df_vaders['reviews'] = df_vaders['reviews'].swifter.apply(remove_urls)
df_vaders['reviews'] = df_vaders['reviews'].swifter.apply(unescape_stuff)
df_vaders['reviews'] = df_vaders['reviews'].swifter.apply(deEmojify)
df_vaders['reviews'] = df_vaders['reviews'].swifter.apply(remove_symbols)
df_vaders['reviews'] = df_vaders['reviews'].swifter.apply(unify_whitespaces)

"""stopwords removal function"""

import spacy
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
sp = spacy.load('en_core_web_sm')

cachedStopWords = sp.Defaults.stop_words
cachedStopWords = [x.lower() for x in cachedStopWords]
#cachedStopWords.extend(list(stopwords.words('english')))
cachedStopWords = list(set(cachedStopWords))

def remove_stopwords(x):
    
    meaningful_words = []
    my_list = x
    
    tokenized_my_list = word_tokenize(my_list) 
    meaningful_words = [w for w in tokenized_my_list if not w in cachedStopWords]
        
    return " ".join(meaningful_words)

df_vaders['reviews'] = df_vaders['reviews'].swifter.apply(remove_stopwords)

"""NGram function"""

from nltk.tokenize import word_tokenize
from nltk.util import ngrams

def get_ngrams(text, n=2):
    #text = str(text)
    n_grams = ngrams(text.split(), n)
    returnVal = []
    
    try:
        for grams in n_grams:
            returnVal.append('_'.join(grams))
    except(RuntimeError):
        pass
        
    return ' '.join(returnVal).strip()

df_vaders.dtypes

#extract bigrams

df_vaders["bigram_text"] = df_vaders["reviews"].swifter.apply(get_ngrams, n=2)

"""Split the dataframe into three"""

# First, create a list of the unique labels in your dataframe
labels = df_vaders['sentiment'].unique().tolist()

labels

dfp = df_vaders.groupby('sentiment').apply(lambda x: x[x['sentiment'] == labels[0]])
dfn = df_vaders.groupby('sentiment').apply(lambda x: x[x['sentiment'] == labels[1]])
dfnt = df_vaders.groupby('sentiment').apply(lambda x: x[x['sentiment'] == labels[2]])

"""Lets put the bigrams in one long string"""

reviews_string_listP = dfp['bigram_text'].tolist()
reviews_stringP = ' '.join(reviews_string_listP)

reviews_string_listN = dfn['bigram_text'].tolist()
reviews_stringN = ' '.join(reviews_string_listN)

reviews_string_listNt = dfnt['bigram_text'].tolist()
reviews_stringNt = ' '.join(reviews_string_listNt)

from wordcloud import WordCloud   # for the wordcloud
wordcloudP = WordCloud(width = 2000, height = 1334, random_state=1, background_color='black', 
                      colormap='Pastel1', max_words = 75, collocations=False, 
                      normalize_plurals=False).generate(reviews_stringP)
#
wordcloudN = WordCloud(width = 2000, height = 1334, random_state=1, background_color='black', 
                      colormap='Pastel1', max_words = 75, collocations=False, 
                      normalize_plurals=False).generate(reviews_stringN)
#
wordcloudNt = WordCloud(width = 2000, height = 1334, random_state=1, background_color='black', 
                      colormap='Pastel1', max_words = 75, collocations=False, 
                      normalize_plurals=False).generate(reviews_stringNt)

"""Let's plot the bigrams"""

# create the wordcloud
import matplotlib.pyplot as plt   # for wordclouds & charts
from matplotlib.pyplot import figure

# Define a function to plot word cloud
def plot_cloud(wordcloud):
    fig = plt.figure(figsize=(25, 17), dpi=80)
    plt.tight_layout(pad=0)
    plt.imshow(wordcloud)
    plt.axis("off")
    plt.box(False)
    plt.show()
    plt.close() 
   
#Plot
plot_cloud(wordcloudP) 
plot_cloud(wordcloudN) 
plot_cloud(wordcloudNt)

#extract the trigrams
dfp["trigram_text"] = dfp["reviews"].swifter.apply(get_ngrams, n=3)
#
dfn["trigram_text"] = dfn["reviews"].swifter.apply(get_ngrams, n=3)
#
dfnt["trigram_text"] = dfnt["reviews"].swifter.apply(get_ngrams, n=3)

#Lets put the trigrams in one long string
reviews_string_listP2 = dfp['trigram_text'].tolist()
reviews_stringP2 = ' '.join(reviews_string_listP2)
#
reviews_string_listN2 = dfn['trigram_text'].tolist()
reviews_stringN2 = ' '.join(reviews_string_listN2)
#
reviews_string_listNt2 = dfnt['trigram_text'].tolist()
reviews_stringNt2 = ' '.join(reviews_string_listNt2)

from wordcloud import WordCloud   # for the wordcloud
wordcloudP2 = WordCloud(width = 2000, height =1334 , random_state=1, background_color='white', colormap='PuBu_r', 
                      max_words = 50, collocations=False, normalize_plurals=False).generate(reviews_stringP2)
#                      
wordcloudN2 = WordCloud(width = 2000, height = 1334, random_state=1, background_color='white', colormap='Reds_r', 
                      max_words = 50, collocations=False, normalize_plurals=False).generate(reviews_stringN2)
#                      
wordcloudNt2 = WordCloud(width = 2000, height = 1334, random_state=1, background_color='white', colormap='Spectral_r', 
                      max_words = 50, collocations=False, normalize_plurals=False).generate(reviews_stringNt2)

plot_cloud(wordcloudP2)
#
plot_cloud(wordcloudN2)
#
plot_cloud(wordcloudNt2)

"""...."""