from re import compile
from operator import itemgetter

from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from django.utils.translation import ugettext_lazy as _

STOP_WORDS = ['able','about','across','after','all','almost','also','am',
              'among','an','and','any','are','as','at','be','because',
              'been','but','by','can','cannot','could','dear','did','do',
              'does','either','else','ever','every','for','from','get',
              'got','had','has','have','he','her','hers','him','his','how',
              'however','i','if','in','into','is','it','its','just','least',
              'let','like','likely','may','me','might','most','must','my',
              'neither','no','nor','not','of','off','often','on','only','or',
              'other','our','own','rather','said','say','says','she','should',
              'since','so','some','than','that','the','their','them','then',
              'there','these','they','this','tis','to','too','twas','us','wants',
              'was','we','were','what','when','where','which','while','who',
              'whom','why','will','with','would','yet','you','your',
              'find','very','still','non','here', 'many', 'a','s','t','ve',
              'use', 'don\'t', 'can\'t', 'wont', 'come','you\'ll', 'want']

def generate_meta_keywords(value):
    """
        Take any string and removes the html and html entities
        and then runs a keyword density analyizer on the text
        to decided the 20 best one word and two word
        key phrases
    """
    try:
        # translate the stop words
        TR_STOP_WORDS = _(' '.join(STOP_WORDS))
        TR_STOP_WORDS = TR_STOP_WORDS.split()

        # get rid of the html tags
        value = strip_tags(value)

        # get rid of the html entities
        value = unescape_entities(value)

        # lower case the value
        value = value.lower()

        # get the one word, two word, and three word patterns
        one_word_pattern = compile(r'\s*(\w+[a-zA-Z0-9:\-]*\w*(\'\w{1,2})?)')
        two_word_pattern = compile(r'\s*(\w+[a-zA-Z0-9:\-]*\w*(\'\w{1,2})?)(\s+|_)(\w+[a-zA-Z0-9:\-]*\w*(\'\w{1,2})?)')

        # get the length of the value
        value_length = len(value)

        # make a list of one words
        search_end = 0
        one_words = []
        while search_end < value_length:
            s = one_word_pattern.search(value, search_end)
            if s:
                one_word = s.group(1)
                # remove the : from the word
                if one_word[-1] == ':':
                    one_word = one_word[:-1]

                one_words.append(one_word)
                search_end = s.end()
            else: break

        # remove the stop words
        one_words = [word for word in one_words if word not in TR_STOP_WORDS]

        # get the density, and word into a tuple
        one_words_length = len(one_words)
        unique_words = set(word for word in one_words)
        one_words = [(word, round((one_words.count(word)*100.00/one_words_length),2)) for word in unique_words]

        # sort the tuple by the density
        one_words = sorted(one_words, key=itemgetter(1), reverse=True)

        # get the 10 best keywords
        one_words = [word[0] for word in one_words[:10]]

        # make a list of two words phrases without stop phrases
        search_end = 0
        two_words = []
        while search_end < value_length:
            s = two_word_pattern.search(value, search_end)
            if s:
                word1 = s.group(1)
                word2 = s.group(4)
                # remove the : from the words
                if word1[-1] == ':':
                    word1 = word1[:-1]
                if word2[-1] == ':':
                    word2 = word2[:-1]

                if word1 not in TR_STOP_WORDS:
                    if word2 not in TR_STOP_WORDS:
                        two_word = word1 + ' ' + word2
                        two_words.append(two_word)

                search_start = s.start()
                next_search = one_word_pattern.search(value, search_start)
                search_end = next_search.end()
            else:
                # if no match, advance a word
                s = one_word_pattern.search(value, search_end)
                if s:
                    search_end = s.end()
                else: search_end = value_length

        # get the density, and word into a tuple
        two_words_length = len(two_words)
        unique_words = set(words for words in two_words)
        two_words = [(words, round((two_words.count(words)*100.00/two_words_length),2)) for words in unique_words]

        # sort the tuple by the density
        two_words = sorted(two_words, key=itemgetter(1), reverse=True)

        # get the best 2 word keywords
        two_words = [word[0] for word in two_words[:10]]

        # add the two lists together
        keywords = two_words + one_words

        return ', '.join(keywords)
    except AttributeError:
        return ''
