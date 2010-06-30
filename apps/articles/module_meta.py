from django.utils.html import strip_tags
from django.utils.text import unescape_entities
from meta.utils import generate_meta_keywords

class ArticleMeta():
    """
    SEO specific tags carefully constructed follow.  These must *NOT* be perfect
    but rather should be strong. - ES
    
    create a search engine friendly html TITLE tag for the page
    - we want similar phrases but NOT the exact same between TITLE and META tags
    - It MUST produce the exact same result if the spider returns but must also differ
    by site for sites that feed from the same central data
    """ 
    def get_title(self):
        return self.object.headline

    def get_description(self):
        if self.object.summary:
            return_value = self.object.summary
        elif self.object.body:
            return_value = self.object.body

        return_value = strip_tags(return_value)
        return_value = unescape_entities(return_value)
        return_value = return_value.replace("\n","")
        return_value = return_value.replace("\r","")

        return return_value

    def get_keywords(self):
        return generate_meta_keywords(self.object.body)

    def get_meta(self, object, name):

        self.object = object
        self.name = name
        
        if self.name == 'title':
            return self.get_title()
        elif self.name == 'description':
            return self.get_description()
        elif self.name =='keywords':
            return self.get_keywords()

        return ''
    


#Use page title from seo table
#If page title is blank, use headline “–“ release_dt
#If site primary keywords are not blank, add “:” & site primary keywords & “article”
#Else, add “:” & category “ “ subcategory & “article”
#If contact name is not blank, add “:contact : & firstname & “ “ & lastname 
#Else (headline is blank) use category “:” & subcategory
#' note that I don't like category showing up with sitePrimaryKeywords because
#' if you pick a relevant category you get redundant text that looks spammy - ES
#    If category is not blank, add category
#    If subcategory is not blank, add & ": " & subcategory
#    Add " articles for "
#    Else (category is blank), add Site Primary Keywords
#    Add ": Articles for "
    
#If Site Geographic Location is not blank, add Site Display Name  “in” Site Geographic Location
#Else add Site Display Name



"""
create a search engine friendly html META DESCRIPTION tag for the page
"""
#function html_description()
#Use metadescription
#    If metadescription is blank, use headline “by” firstname & “ “ & lastname &”:”& body(250)
#    Else If site primary keywords is not blank, use site primary keywords
#        Else, “:” category & “ “ & subcategory & “article”
#    Add "Articles and White Papers for & stie disdplay name & “ “ & site geographic location


"""
create a search engine friendly html META KEYWORDS tag for the page
"""
#function html_keywords()
#Use metakeywords
#    If metakeywords are blank, use site primary keywords & “ “ 
#    If headline is not blank, add “Articles, “ & site geographic location & “,” & site display name
#        Add “, white paper, “ & firstname & “ “ & lastname & “, “ and body(250)
#    Else add “Articles, “ & site geographic location & “,” & site display name & “, white papers”
#    If site secondary keywords is not blank, add site secondary keywords

    