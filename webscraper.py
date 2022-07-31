from bs4 import BeautifulSoup as soup
import requests
#from newspaper import Article, ArticleException
from textblob import TextBlob
import psycopg2
import metadata_parser
from flatten_json import flatten
import nltk
import json
import spacy
nlp = spacy.load('en_core_web_sm')

TAG_NAME1 = "l-container"
TAG_NAME2 ="Article__body"
TAG_NAME3 = "BasicArticle__main"



# Connection details
connection = psycopg2.connect(user="aaron",
                                  password="A@R0n1!",
                                  host="ec2-52-53-198-177.us-west-1.compute.amazonaws.com",
                                  port="5432",
                                  database="db1")
cursor = connection.cursor()


#url =    "https://edition.cnn.com/2022/07/28/politics/joe-biden-xi-jinping-call/index.html"

def web_scraper(url):

    html = requests.get(url)
    bsobj = soup(html.content, 'lxml')
    if bsobj.find(attrs={'class':TAG_NAME1}):
        content = bsobj.find(attrs={'class':TAG_NAME1})
    elif bsobj.find(attrs={'class':TAG_NAME2}):
        content = bsobj.find(attrs={'class':TAG_NAME2})
    elif bsobj.find(attrs={'class':TAG_NAME3}):
        content = bsobj.find(attrs={'class':TAG_NAME3})


    text= content.get_text()
    if '(CNN)' in text:
        before_keyword, keyword, after_keyword  = text.partition("(CNN)")
        text = after_keyword

    text = text.replace("'s","")
    #after_keyword = after_keyword.replace("'","")
    text = text.replace('"',"")
    text = text.replace('''\'''',"")
    text = text.replace('''\n''',"")

    #metadata
    page = metadata_parser.MetadataParser(url)
    unflat_json = page.metadata
    flat_json = flatten(unflat_json)
    meta_data =json.dumps(flat_json)
    meta_data = meta_data.replace("\'s","")
    meta_data = json.loads(meta_data)
    meta_data['og_title'] = meta_data['og_title'].replace("'","")
    meta_data['meta_keywords'] = meta_data['meta_keywords'].replace("'","")
    meta_data['meta_twitter:title'] = meta_data['meta_twitter:title'].replace("'","")

    
    article_len = len(text)
    sentence=[]
    tokens = nlp(text)
    for sent in tokens.sents:
        sentence.append((sent.text.strip()))
    sentence_len = len(sentence)

    # text sentiment

    text_blob = TextBlob(text)
    text_polarity = text_blob.polarity
    text_subjectivity = text_blob.subjectivity

    title_blob = TextBlob(meta_data['og_title'])
    title_polarity = title_blob.polarity
    title_subjectivity = title_blob.subjectivity


    flag =1
    if text_polarity == 0 and text_subjectivity == 0:
        flag = 0
    
    if not flag:
        return ('Error: Please check Webpage content.')
    else:
        tokenizer = nltk.tokenize.RegexpTokenizer(r'\w+')
        tokens = tokenizer.tokenize(text)
        token_len = len(tokens)
        stopwords = nltk.corpus.stopwords.words('english')
        words =[]
        for word in tokens:
            words.append(word.lower())
        words_new =[]
        for word in words:
            if word not in stopwords:
                if len(word)>1:
                    words_new.append(word)
        token_len = len(words_new)

        freq_dist = nltk.FreqDist(words_new)
        word_freq = dict(freq_dist)

        after_keyword = after_keyword.replace("'s","")
        after_keyword = after_keyword.replace("'","")
        after_keyword = after_keyword.replace('"',"")
        abc = 45
        try:
            print(meta_data,text)
            postgres_insert_query = ''' INSERT INTO d5(publish_date, url, title, description,site_name, article_type, image_url, image_width, image_height, x_ua_compatible, charset, content_type, viewport, article_section, referrer_url, last_modified, author, twitter_title, twitter_description, meta_data_keywords, content_tier, template_top, article_body, body_polarity, body_subjectivity, title_polarity, title_subjectivity, article_count, sentence_count, word_count) VALUES ('{0}','{1}','{2}','{3}','{4}','{5}','{6}',{7},{8},'{9}','{10}','{11}','{12}','{13}','{14}','{15}','{16}', '{17}','{18}','{19}','{20}','{21}','{22}',{23},{24},{25},{26},{27},{28},{29}) '''.format(meta_data.get('meta_pubdate',0),meta_data.get('og_url'), meta_data.get('og_title',0),meta_data.get('og_description',0),meta_data.get('og_site_name',0),meta_data.get('og_type',0),meta_data.get('og_image',0),meta_data.get('og_image:width',0),meta_data.get('og_image:height',0),meta_data.get('meta_x-ua-compatible',0),meta_data.get('meta_charset',0),meta_data.get('meta_content-Type',0),meta_data.get('meta_viewport',0),meta_data.get('meta_section',0),meta_data.get('meta_referrer',0),meta_data.get('meta_lastmod',0),meta_data.get('meta_author',0),meta_data.get('meta_twitter:title',0),meta_data.get('meta_og:description',0),meta_data.get('meta_keywords',0),meta_data.get('meta_article:content-tier',0),meta_data.get('meta_template-top',0),text,text_subjectivity,text_polarity,title_polarity,title_subjectivity,article_len,sentence_len,token_len)
            print(postgres_insert_query)
            cursor.execute(postgres_insert_query)
        #print("headline : {}".format(link.text))
            connection.commit()
            print("HI--------")
            return ('Webpage successfully scraped & uploaded to database')

        except:
            connection.rollback()
            return ("Error: Couldn't connect to database. Please try again.")




'''
    html = requests.get(url)

    bsobj = soup(html.content, 'lxml')
    content = bsobj.find(attrs={'class':CLASS_ATTRIBUTE})
    data = content.get_text()
    before_keyword, keyword, after_keyword  = data.partition("(CNN)")
    #after_keyword
    #print (after_keyword)
    after_keyword = after_keyword.replace("'s","")
    after_keyword = after_keyword.replace("'","")
    after_keyword = after_keyword.replace('"',"")
    postgres_insert_query = ''' '''INSERT INTO ab VALUES ('{}')''' '''.format(after_keyword)
    cursor.execute(postgres_insert_query)
    #print("headline : {}".format(link.text))
    connection.commit()
    count = cursor.rowcount
    return ('Webpage successfully scraped & uploaded to database')

'''