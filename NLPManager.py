import os
import warnings

from stemming import porter

import nltk
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
import re

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
nltk.data.path.append(BASE_DIR + '\\Data\\nltk_data')

from Utils.FileFunc import FileFunc

theInstance = None

from datetime import datetime
from datetime import timedelta
import pytz


def getInstance(query = None):
    global theInstance
    
    if theInstance is None:
        theInstance = NLPManager(query)
    elif query is not None:
        theInstance._set_query(query)
    return theInstance

WN_NOUN = 'n'
WN_VERB = 'v'
WN_ADJECTIVE = 'a'
WN_ADJECTIVE_SATELLITE = 's'
WN_ADVERB = 'r'

forms = [WN_NOUN, WN_VERB, WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE, WN_ADVERB]


class NLPManager:
    
    def __init__(self, query=None):
        super(NLPManager, self).__init__()
        wn.synsets('', '') #hack to preload wordnet corpora for speedy response rather than waiting for first use
        self.wnl = WordNetLemmatizer()
        self.query = query
        self.protected_tags = ['N', 'S', '^', 'Z', 'V', 'A', '#', '$']
        path = BASE_DIR + '\\Data\\stopwords_en.txt'
        self.stop_list = FileFunc.read_file_into_list(path)

        if self.stop_list is None:
            raise TypeError("You must specify list of stop words")
    
        if self.protected_tags is None:
            raise TypeError("You must specify list protected tags")
        
        #enable lemmatization of vertices
        self.lemming = True
        
        #enable stemming of vertices
        self.stemming = False
        self.matcher = re.compile("^[@\w-]+$")

    def _set_query(self, query):
        self.query = query
    
    def _stem(self, term):
        return porter.stem(term)
        
    def lemmatize(self, term, pos):
        warnings.filterwarnings("ignore")
        return self.wnl.lemmatize(term, pos)

    def valid_token(self, token, tag):
        #valid ascii text
        try:
            token.encode('ascii')
        except UnicodeEncodeError:
            return None

        token = token.lower().strip()

        if token.startswith('#'):
            token = token[1:]

        if not self.matcher.match(token):
            return None

        if token in self.stop_list:
            # print(token)
            return None
        
        if tag not in self.protected_tags:
            return None
        
        if self.lemming is True:
            if tag is 'N':
                token = self.lemmatize(token, 'n')
            elif tag is 'V':
                token = self.lemmatize(token, 'v')

        if self.stemming is True:
            token = self._stem(token)

        #check if not a matching version of the query
        if self._match_query(token) is True:
            return None
        
        return token

    def _match_query(self, term):
        if self.stemming == False:
            for query in self.query:
                if query == term:
                    return True
        else:
            for query in self.query:
                if self._stem(term) == self._stem(query) or query == term:
                    return True
        
        return False

    #change pos label to wn format
    def posconvert(self, label):
        pos = None

        if label == 'v':
            pos = wn.VERB
        elif label == 'n':
            pos = wn.NOUN

        return pos

    @staticmethod
    def convertPOSForms(word, from_pos, to_pos):

        synsets = wn.synsets(word, pos=from_pos)

        # Word not found
        if not synsets:
            # print(word, "not found")
            return []

        # Get all lemmas of the word (consider 'a'and 's' equivalent)
        lemmas = [l for s in synsets
                    for l in s.lemmas()
                    if s.name().split('.')[1] == from_pos
                        or from_pos in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)
                            and s.name().split('.')[1] in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)]

        # Get related forms
        derivationally_related_forms = [(l, l.derivationally_related_forms()) for l in lemmas]

        # filter only the desired pos (consider 'a' and 's' equivalent)
        related_noun_lemmas = [l for drf in derivationally_related_forms
                                 for l in drf[1]
                                 if l.synset().name().split('.')[1] == to_pos
                                    or to_pos in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)
                                        and l.synset().name().split('.')[1] in (WN_ADJECTIVE, WN_ADJECTIVE_SATELLITE)]

        # Extract the words from the lemmas
        words = [l.name() for l in related_noun_lemmas]
        len_words = len(words)

        # Build the result in the form of a list containing tuples (word, probability)
        result = [(w, float(words.count(w))/len_words) for w in set(words)]
        result.sort(key=lambda w: -w[1])

        # return all the possibilities sorted by probability
        return result

    def gen_forms(self, term, threshold):
        rst = []
        for form1 in forms:
            for form2 in forms:
                if form1 != form2:
                    ret = self.convertPOSForms(term, form1, form2)

                    # remove empties and below threshold
                    ret = [r for r in ret if not [] and r[1] >= threshold]

                    if ret:
                        rst.append({'pos': form2, 'terms': ret})

        return rst

    def similarity(self, chunk1, pos1, chunk2, pos2):
      # pos1 = self.posconvert(pos1)
      #   //pos2 = self.posconvert(pos2)
        set1 = wn.synsets(chunk1)
        print(set1)
        set2 = wn.synsets(chunk2)
        print(set2)
        max = 0.0
        
        for x in set1:
            for y in set2:
                val = x.wup_similarity(y)
                if val is not None and val > max:
                    max = val                
        return max

if __name__ == '__main__':
    starttime = datetime.now(pytz.utc)
    nlp = NLPManager()
    inittime = datetime.now(pytz.utc)
    run = inittime - starttime
    print('init time: ', run)

    print(nlp.similarity("death", 'n', "die", 'v'))

    similaritytime = datetime.now(pytz.utc) - inittime
    print("synset time: ", similaritytime)

    print([ n.lemmas() for n in wn.synsets('agree') ])