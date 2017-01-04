import urllib
import xml.etree.ElementTree as ET
import re
import time
import sqlite3
import random
import csv

def getpost(post, backpageurl):
    "Get a specific ad after retrieving posting list"
    url2 = backpageurl + '/online/api/Ad.xml?Id=' + post 
    ns = {'content': 'http://purl.org/rss/1.0/modules/content/',
        'bp': 'http://www.backpage.com/'}
    
    print url2
    uh2 = urllib.urlopen(url2)
    data2 = uh2.read()
    tree2 = ET.fromstring(data2)
    item = tree2.find('channel/item')
    if item is not None:
        ptitle = item.find('bp:Title', ns).text.encode('ascii', 'ignore')
        pad = item.find('bp:Ad', ns).text.encode('ascii', 'ignore')
        AdUrl= item.find('bp:AdUrl', ns).text
        ptime = item.find('bp:PostingTime', ns).text
        age = (item.find('bp:Age', ns).text)
    else:
        ptitle = None
        pad = None
        AdUrl = None 
        ptime = None
        age = None
    return ptitle, pad, AdUrl, ptime, age;

conn = sqlite3.connect('bpscrape.sqlite')
cur = conn.cursor()
 
cur.execute('''CREATE TABLE IF NOT EXISTS Escorts (id TEXT, title TEXT, body TEXT, 
            age TEXT, AdUrl TEXT)''')
 
ids = []
#select ids from posts that are not already in escorts (haven't been downloaded yet)
for row in cur.execute('select distinct t1.id from posts t1 left join escorts t2 on t2.id = t1.id where t2.id is null'):
    ids.append(row)

    
for id in ids:
    item = id[0]
    cur.execute("SELECT * FROM Posts WHERE id= ?", (item, ))
    row = cur.fetchone()
    backpageurl = row[0]
    # random delay to be nice, keep from hammering website
    rndnum = random.random()*5
    time.sleep(rndnum)
    print item, backpageurl
    try:
        posts = getpost(item, backpageurl)
    except:
        continue
    AdUrl = posts[2]
    print AdUrl
    cur.execute('''INSERT INTO Escorts (id, title, body, age, AdUrl)
            VALUES (?, ?, ?, ?, ?)''', 
            (item, posts[0], posts[1], posts[4], posts[2]))
    conn.commit()
cur.close()
print 'Finished'
    
    
conn.close()