#!/usr/bin/env python
# coding: utf-8

# In[0]:


import pandas as pd
import re
import itertools
import sys
import flag

# In[1]:
# read list of stopwords from text file
def readStopWords(fileName='stopwords.txt'):
    fd = open(fileName)
    line = fd.read()
    stopwords = line.splitlines()
    fd.close()
    return stopwords


# In[2]:
# preprocess input text
def removePuncs(text, stopwords):
    # convert to lower case
    text = text.lower()
    
    # convert text to a list of words   
    listWord = text.split()
    
    # remove punctuations and digits
    puncs = r"[!\(\)\-\[\]\{\};'\":\\,<>\./\?@#\$%^&\*_~0-9]"
    listWord = [re.sub(puncs,'',word) for word in listWord]
    listWord = [word for word in listWord if word not in stopwords and len(word)>0]
    
    return listWord


# In[3]:
# generate "n grams" (nC3, nC2, nC1) for given list of terms
def n_grams(terms):
    three_grams = [' '.join(i) for i in itertools.combinations(terms, 3)]
    two_grams = [' '.join(i) for i in itertools.combinations(terms, 2)]
    one_grams = [' '.join(i) for i in itertools.combinations(terms, 1)]
    return three_grams, two_grams, one_grams


# In[4]:
# get a list of locations for each n gram combination, if any
def get_locations(terms, cities='worldcities.csv'):
	# read cities file
    df = pd.read_csv(cities)
    cols = ['city', 'city_ascii','state', 'country', 'iso2', 'iso3']
    
    # convert columns to lowercase
    for c in cols:
        df[c] = df[c].str.lower()
    locations = pd.DataFrame(columns=cols)
    
    # iterate through columns and "n gram" combinations
    for c in cols:
        for t in terms:
            if t in df[c].values and t not in locations[c].values:
                data = df[df[c] == t][cols].iloc[0]
                loc = {}
                # if "n gram" is a city, return city, state, country and iso codes 
                if c == 'city':
                    loc['city'] = data['city']
                    loc['city_ascii'] = data['city_ascii']
                    loc['state'] = data['state']
                    loc['country'] = data['country']
                    loc['iso2'] = data['iso2']
                    loc['iso3'] = data['iso3']
                # if "n gram" is a state, return state, country and iso codes 
                elif c == 'state':
                    loc['state'] = t
                    loc['country'] = data['country']
                    loc['iso2'] = data['iso2']
                    loc['iso3'] = data['iso3']
                # if "n gram" is a country, return country and iso codes 
                elif c == 'country':
                    loc['country'] = t
                    loc['iso2'] = data['iso2']
                    loc['iso3'] = data['iso3']
                # if "n gram" is an ISO code, return country and iso codes 
                elif c == 'iso2' or c == 'iso3':
                    loc['country'] = data['country']
                    loc['iso2'] = data['iso2']
                    loc['iso3'] = data['iso3']
                
                locations = locations.append(loc, ignore_index=True)
    
    # remove duplicates, if any and tidy up results
    locations = locations.drop_duplicates()
    for c in cols:
        if c == 'iso2' or c == 'iso3':
            locations[c] = locations[c].str.upper()
        else:
            locations[c] = locations[c].str.title()
            
    # return list of locations
    return locations.to_dict(orient='records')


# In[5]:
def main():
    text = sys.argv[1]
    
    # handle flag emojis in the text if any
    place = flag.dflagize(text)
    text_size = len(place)
    start_index = place.find(':')
    end_index = -1
    start_prev, end_prev = 0, 0
    rep = {}

    while(start_index > -1):
        start_index += 1
        end_index = start_index + 1 + place[start_index+1:].find(':')
        emoji_loc = place[start_index:end_index] 
        rep[emoji_loc] = (start_index+start_prev-1, end_index+end_prev)
        start_prev, end_prev = start_index, end_index
        place = place[end_index+1:]
        start_index = place.find(':')

    for key in rep.keys():
        text = text.replace(text[rep[key][0]:rep[key][1]], key)
    
    # remove stopwords 
    stopwords = readStopWords(fileName='stopwords.txt')
    
    # generate location terms
    terms = removePuncs(text, stopwords)
    
    # generate n_grams from these terms (combination of terms basically)
    three_grams, two_grams, one_grams = n_grams(terms)
    
    # get unique locations from these n_grams 
    locations = get_locations(three_grams)
    if len(locations) == 0:
        locations = get_locations(two_grams)
        if len(locations) == 0:
            locations = get_locations(one_grams)
            
    # return locations as an array of dictionary
    return locations


print(main())


