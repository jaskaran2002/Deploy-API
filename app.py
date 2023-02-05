from flask import Flask,jsonify,Response
from flask_cors import CORS, cross_origin


from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.options import Options
import json


import requests, webbrowser
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse
import sys
import os

import subprocess
sys.path.append(os.path.abspath("/opt/render/project/src/sherlock/sherlock"))
# sys.path.append(os.path.abspath("/Users/jaskaran/Documents/Projects/Deploy-API/sherlock/sherlock"))
from sherlock import customfunc


app=Flask(__name__)
CORS(app)

@app.route('/')
def hello_world():
    return 'Hello, World!'

@app.route('/d')
def debuggincode():
    currdir = os.getcwd()
    allfiles = os.listdir()
    chrometemp = os.environ.get("GOOGLE_CHROME_BIN")
    return {'nothing' : f"{currdir}", 'directories': f"{allfiles}", 'chrome': f"{chrometemp}"}

@app.route('/runredditPython/<string:query>')
def searchReddit(query):
    PATH = "./geckodriver"

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    # options = Options()
    # options.headless = True
    # driver = webdriver.Firefox(executable_path=PATH, options=options)
    query.replace(' ', "%20")
    url = f"https://www.reddit.com/search/?q={query}"
    driver.get(url)
    # driver.implicitly_wait(5)
    # data = []

    try:
        temp = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, '_2i5O0KNpb9tDq0bsNOZB_Q')))
#         tem2 = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.CLASS_NAME, '_3ryJoIoycVkA88fy40qNJc')))
    except:
        print("NOT found")
        
        cards = driver.find_elements(By.CLASS_NAME, '_1poyrkZ7g36PawDueRza-J')
        driver.quit()
        return {"noting" : f"{cards}"}
    data = []

    cards = driver.find_elements(By.CLASS_NAME, '_1poyrkZ7g36PawDueRza-J')
    for card in cards:
        info = {}

        currData = card.text.split('\n')

#         info['subreddit'] = card.find_element(By.CLASS_NAME, '_3ryJoIoycVkA88fy40qNJc').text
#         info['user'] = card.find_element(By.CLASS_NAME, '_2tbHP6ZydRpjI44J3syuqC').text

        linktest = card.find_element(By.CLASS_NAME, 'nbO8VWsMIB-Mv-tIa37NF')
        linktag = linktest.find_element(By.CSS_SELECTOR, 'a')
        info['link'] = linktag.get_attribute('href')

        subreddittemp = info['link'].replace('https://www.reddit.com/r/', '')
        info['subreddit'] = "r/"
        for c in subreddittemp:
            if (c == '/'):
                break
            info['subreddit'] += c
        temp = card.find_element(By.CLASS_NAME, '_eYtD2XCVieq6emjKBH3m')
        info['title'] = temp.text
        smallData = card.find_elements(By.CLASS_NAME, '_vaFo96phV6L5Hltvwcox')

        if (smallData):
            info['upvotes'] = smallData[0].text.replace('upvotes', ' ').strip()
            info['comments'] = smallData[1].text.replace('comments', ' ').strip()
            info['awards'] = smallData[2].text.replace('awards', ' ').strip()
        data.append(info)

    driver.quit()
    # return data

    return Response(json.dumps(data),mimetype='application/json')


# query = 'usa'
# data = searchReddit(query)
# with open('./test.json', 'w') as f:
#     json.dump(data,f,indent=4)


@app.route('/runDuckPython/<string:query>')
def searchNews(query):
    PATH = "./geckodriver"
    data = []

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(options=chrome_options)

    # options = Options()
    # PATH_TO_DEV_NULL = '/dev/null'
    # options.headless = True
    # driver = webdriver.Firefox(executable_path=PATH, options=options, service_log_path=PATH_TO_DEV_NULL)
    # driver = webdriver.Firefox(executable_path=PATH)
    url = f"https://duckduckgo.com/{query}"
    driver.get(url)
    # search = driver.find_element(By.ID, 'searchbox_input')
    # search.send_keys(query)
    # search.send_keys(Keys.RETURN)
    try:
        news = WebDriverWait(driver,10).until(EC.presence_of_element_located((By.LINK_TEXT, 'News')))
    except:
        print("Not Found")
        driver.quit()
        exit()
    news.click()
    try:
        cards = WebDriverWait(driver,10).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'result__body')))
    except:
        print("Cards not found")
        driver.quit()
        exit()
    for card in cards:
        info = {}
        info['title'] = card.find_element(By.CLASS_NAME, 'result__a').text
        info['text'] = card.find_element(By.CLASS_NAME, 'result__snippet').text
        website = card.find_element(By.CLASS_NAME, 'result__url')
        info['website'] = website.text
        info['news-link'] = website.get_attribute('href')
        try:
            img = card.find_element(By.CLASS_NAME, 'result__image__img')
            info['image'] = img.get_attribute('src')
        except:
            print("not Found")
        data.append(info)
    driver.quit()
    return data


@app.route('/googlesearch/<string:user_inp>')
def ongaBunga(user_inp):
    user_input=''
    for i in range(len(user_inp)):
        if user_inp[i] == ' ':
            user_input = user_input + '+'
        else:
            user_input = user_input + user_inp[i]

    print("Bringing top results.")
    res = requests.get('https://www.google.com/search?q=' + user_input)
    soup = BeautifulSoup(res.text, 'html.parser')

    results = soup.find_all('div', class_='egMi0 kCrYT')
    title=soup.find_all('div',class_='BNeawe vvjwJb AP7Wnd')

    imres='https://www.google.com/search?tbm=isch&q='+ user_input
    vidres='https://www.google.com/search?tbm=vid&q='+user_input


    l = len(results)

    li = []
    lit=[]

    c ='googleSearch.json'

    def findDomain(URL):
        domain = urlparse(URL).netloc
        return domain
    def find(URL):
        url = re.findall('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\), ]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',URL)
        return url
    for i in results:

        j = str(i)
        li.append(find(j))
    for i in title:
        j=str(i.text)
        lit.append(j)




    l2=[]
    for i in range(len(li)):
        x=findDomain(li[i][0])
        z=li[i][0]
        w=z.index('&')
        di1 = {'User Input': user_inp, 'Google Images': imres, 'Videos': vidres}
        di1['Title'] = lit[i]
        di1['Link'] = z[:w]
        di1['Website'] = x
        l2.append(di1)
    print(l2)
    return Response(json.dumps(l2),mimetype='application/json')


@app.route('/sherlock/<string:query>')
def searchUsername(query):
    
    tempdata = customfunc(query)
    return tempdata

    timeout = 1
    # Taking Data
    # p = subprocess.Popen([f'cd sherlock && python3 sherlock {query} --timeout {timeout} > ../{query}.txt'], shell=True)
    p = subprocess.Popen([f'workon deployingapi && cd /home/asgardian/Deploy-API/sherlock && python sherlock {query} --timeout {timeout} > ../{query}.txt'], shell=True)
    p.wait()

    # Removing Default File
    # p1 = subprocess.Popen([f'rm -f /home/asgardian/Deploy-API/sherlock/{query}.txt'], shell=True)
    # p1.wait()

    # file = open(f'/home/asgardian/Deploy-API/{query}.txt','r')
    file = open(f'/home/asgardian/Deploy-API/sherlock/{query}.txt','r')
    data = file.read().strip().split('\n')
    data.pop()
    final = {}
    for i in range(2,len(data)-3):
        temp = data[i]
        temp = temp.replace('[+]', ' ')
        indx = temp.find(':')
        final[temp[0:indx].strip()] = temp[indx+1:].strip()

    file.close()
    # p1 = subprocess.Popen([f'rm -f /home/asgardian/Deploy-API/{query}.txt'], shell=True)
    p1 = subprocess.Popen([f'rm -f /home/asgardian/Deploy-API/sherlock/{query}.txt'], shell=True)
    p1.wait()
    return final



if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
