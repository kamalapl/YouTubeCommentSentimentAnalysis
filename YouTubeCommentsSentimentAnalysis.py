from apiclient.discovery import build
import argparse
import unidecode
import time
import os
import pandas as pd 
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from textblob import TextBlob
import re

def sentiment(polarity):
    if polarity < 0:
        p="Negative"
    elif polarity > 0:
        p="Positive"
    else:
        p="Neutral"
    return p

def scrape_comments(youtube_video_url,Movie_name):

    chrome_path=r"C:\Users\eirpcah\Downloads\chromedriver_win32_84\chromedriver.exe"

    driver = webdriver.Chrome (chrome_path)
    driver.get (youtube_video_url)
    driver.maximize_window()
    driver.implicitly_wait (50)

    #scroll down to load comments

    driver.execute_script('window.scrollTo (0,600);')
    time.sleep (50)
    print("scrolled")

    #sort by top comments
    sort =driver. find_element_by_xpath("""//*[@id="icon-label"]""")

    #(sort=WebDriverMait (driver, 10).until (EC.presence_of_element_located (By XPATH: '//input [@id="icon-label"]')))
    sort.click()
    time.sleep (10) 
    topcomments =driver.find_element_by_xpath("""//*[@id="menu"]/a[1]/paper-item-body/div[1]""")
    topcomments.click() 
    time.sleep (10)

    #Loads 20 comments, scroll two times to load next set of 40 comments.
    for i in range(0,2):
        driver.execute_script ("window.scrollTo (0,Math.max (document.documentElement.scrollHeight, document.body.scrollHeight ,document.documentElement.clientHeight))")
        time.sleep(10)

    #count total number of comments and set index to number of comments if less than 50 otherwise set as 50.
    totalcomments= len (driver.find_eloments_by_xpath("""//*[@id="content-text"]"""))

    if totalcomments < 20:
        index = totalcomments
    else:
        index= 20

    ccount = 0
    comments = []

    while ccount < index:

        try:
            comment = driver.find_elements_by_xpath('//* [@id="content-text"]')[ccount].text
            ccount=ccount+1
            print (comment)
            comments.append (comment)

        except:
            comment = ""

    polarity=[]
    subjectivity=[] 
    sentiment_type=[]

    for elm in comments:
        x=TextBlob(elm)
        print(elm)
        print ("Polarity: "+str(x.sentiment.polarity))
        print ("Subjectivity :"+str (x.sentiment.subjectivity))
        polarity.append (x.sentiment.polarity)
        s=sentiment (x.sentiment.polarity)
        print("Sentiment Type :"+s) 
        sentiment_type.append(s)

    dataframe={"comment":comments, "sentiment_type":sentiment_type, "polarity":polarity, "subjectivity":subjectivity}
    df= pd.DataFrame.from_dict (dataframe, orient='index')
    dfl=df.transpose ()
    dfl.columns = ['comment', 'polarity', 'sentiment_type','subjectivity']
    dfl.to_csv (r"C:\Users\eirpcah\Desktop\python_practice\comment_sentiment_" +Movie_name+".csv", header=True, encoding='utf-8', index=False)

def youtube_video_url(options):
    youtube = build(YOUTUBE_API_SERVICE_NAME,YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    search_response = youtube.search().list(q=options.q, part="id, snippet", maxResults=options.max_results).execute()
    for search_result in search_response.get ("items",[]):
        if search_result["id"]["kind"]=="youtube#video":
            videoId = search_result["id"]["videoId"]
            print ("videoId: " +str(videoId))
            videoId.append (videoId)
            url="https://www.youtube.com/watch?v="+videoId
            print(url)
    return url

if __name__=="__main__":
    print("Enter the Movie Name : ")
    Movie_name = str(input())
    parser = argparse.ArgumentParser(description="youtube search")
    parser.add_argument ("--q", help="Search term", default=Movie_name+ "Movie Trailer 2020") 
    parser.add_argument ("--max-results", help="Max results", default=1) 
    args = parser.parse_args()
    youtube_video_url =  youtube_video_url(args) 
    scrape_comments(youtube_video_url,Movie_name)