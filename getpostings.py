import urllib
import xml.etree.ElementTree as ET
import re
import time
import sqlite3
import random
import csv


# while testing: measure time it takes to run
#start = time.clock()

# list of cities
with open('cities.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile, delimiter=',')
    citylist = list(reader)
    citylist = list(citylist[0])


def catget(backpageurl):
    "gets the proper category number for the escorts category" 
    #print backpageurl #testing to find source of error
    url = backpageurl + "/online/api/Category.xml?Section=4381"
    
    ns = {'content': 'http://purl.org/rss/1.0/modules/content/',
        'bp': 'http://www.backpage.com/'}

    uh = urllib.urlopen(url)
    data = uh.read()
    tree = ET.fromstring(data)
    lst = tree.findall('channel/item')
    for item in lst:
        if item.find('bp:Name', ns).text == 'escorts':
            categoryNumber = item.find('bp:Id', ns).text
    return categoryNumber;

def postget(backpageurl, cat):
    url = backpageurl + '/online/api/Search.xml?Category=' + cat + '&Max=10'
    #above line limited to 10 items for testing; change to 100 in final program
    ns = {'content': 'http://purl.org/rss/1.0/modules/content/',
        'bp': 'http://www.backpage.com/'}
    uh = urllib.urlopen(url)
    data = uh.read()
    tree = ET.fromstring(data)
    lst = tree.findall('channel/item')
    # postlist = []
    for item in lst:
        post = item.find('bp:Id', ns).text
        # postlist.append(post)
        posttime = item.find('bp:PostingTime', ns).text
        
        # update posts table
        cur.execute('''INSERT OR IGNORE INTO Posts (backpageurl, id, datetime)
                VALUES (?, ?, ?)''', (backpageurl, post, posttime))
    conn.commit()
     
    
 
conn = sqlite3.connect('bpscrape.sqlite')
cur = conn.cursor()
  
    
# cur.execute('''CREATE TABLE IF NOT EXISTS Escorts (id TEXT, title TEXT, body TEXT, 
#            age TEXT, AdUrl TEXT)''')
            
cur.execute('''CREATE TABLE IF NOT EXISTS Posts (backpageurl TEXT, id TEXT, datetime TEXT, 
            PRIMARY KEY (backpageurl, id, datetime))''')
            
#cur.execute('''CREATE TABLE IF NOT EXISTS Cities (city TEXT, lat TEXT, lon TEXT, backpageurl TEXT, PRIMARY KEY (backpageurl))''')
 
print len(citylist), "cities"

for backpageurl in citylist:
    categoryNumber = catget(backpageurl)
    rndnum = random.random()*5
    time.sleep(rndnum)
    print "getting " + backpageurl
    postlist = postget(backpageurl, categoryNumber)
    
    
conn.commit()
cur.close()

# for testing: measure elapsed time
#end = time.clock()
#lapsed = (end - start)
#m, s = divmod(lapsed, 60)
#h, m = divmod(m,60)
#print "%d:%02d:%02d" % (h, m, s)
print 'Finished'

