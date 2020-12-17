#!/usr/bin/env python
# -*- coding: utf-8 -*-
#Scrapes Guardian style guide

import requests
import lxml.html
import simplejson as json
import time
import boto3
from syncData import syncData

# import StringIO

#get date and time

currDate = time.strftime("%d/%m/%Y")
print(currDate)

currTime = time.strftime("%H:%M:%S", time.gmtime())
print(currTime)

urls = ['https://www.theguardian.com/guardian-observer-style-guide-a',
'https://www.theguardian.com/guardian-observer-style-guide-b',
'https://www.theguardian.com/guardian-observer-style-guide-c',
'https://www.theguardian.com/guardian-observer-style-guide-d',
'https://www.theguardian.com/guardian-observer-style-guide-e',
'https://www.theguardian.com/guardian-observer-style-guide-f',
'https://www.theguardian.com/guardian-observer-style-guide-h',
'https://www.theguardian.com/guardian-observer-style-guide-i',
'https://www.theguardian.com/guardian-observer-style-guide-j',
'https://www.theguardian.com/guardian-observer-style-guide-k',
'https://www.theguardian.com/guardian-observer-style-guide-l',
'https://www.theguardian.com/guardian-observer-style-guide-m',
'https://www.theguardian.com/guardian-observer-style-guide-n',
'https://www.theguardian.com/guardian-observer-style-guide-o',
'https://www.theguardian.com/guardian-observer-style-guide-p',
'https://www.theguardian.com/guardian-observer-style-guide-q',
'https://www.theguardian.com/guardian-observer-style-guide-r',
'https://www.theguardian.com/guardian-observer-style-guide-s',
'https://www.theguardian.com/guardian-observer-style-guide-t',
'https://www.theguardian.com/guardian-observer-style-guide-u',
'https://www.theguardian.com/guardian-observer-style-guide-v',
'https://www.theguardian.com/guardian-observer-style-guide-w',
'https://www.theguardian.com/guardian-observer-style-guide-x',
'https://www.theguardian.com/guardian-observer-style-guide-y',
'https://www.theguardian.com/guardian-observer-style-guide-z']

styleData = []

#Scrape style guide content

print("Getting style guide content")

def scrapeEntry(s):
	# print(s)
	if "<br>" in s:
		notes = s.split('<br>')[1].split('</p>')[0]
	else:
		notes = ""
	return notes

for url in urls:
	print(url)
	html = requests.get(url).content
	# print(html)
	parser = lxml.html.HTMLParser(encoding="utf-8")
	dom = lxml.html.fromstring(html, parser=parser)

	#list of p elements in article block
	#r2 - pars = dom.cssselect('#article-body-blocks p')
	#beta - pars = dom.cssselect('.content__article-body p')

	pars = dom.cssselect('.article-body-commercial-selector p')
	#empty list to store position of style entry headers

	headerLocs = []

	for parNo, par in enumerate(pars):
		# print(lxml.html.tostring(par))
		if 'class="css-38z03z"><strong>' in lxml.html.tostring(par).decode("utf-8"):
			print("Actual entry in this paragraph")
			headerLocs.append(parNo)
	
	#print "list of entry locations", headerLocs		 
	#print headerLocs[len(headerLocs)-1], len(pars)

	for i in range(0, len(headerLocs)):
		data = {}
		
		#handle last entry

		if i == len(headerLocs)-1:

			#is the last entry a single paragraph?

			if headerLocs[i] == len(pars)-2:
				entry = pars[(headerLocs[i])].cssselect('strong')[0].text
				notes = scrapeEntry(lxml.html.tostring(pars[(headerLocs[i])]).decode("utf-8"))
				#print entry
				#print notes
				data['entry'] = entry
				data['notes'] = notes

			else:
				entry = pars[(headerLocs[i])].cssselect('strong')[0].text
				notes = str(lxml.html.tostring(pars[(headerLocs[i])]))
				if "<br>" in notes:
					notes = lxml.html.tostring(pars[(headerLocs[i])]).decode("utf-8").split('<br>')[1].split('</p>')[0]
				if '</a>' in notes:
					notes = notes.split('</a>')[1]
				for x in range((headerLocs[i]+1),len(pars)-1):
					notes += lxml.html.tostring(pars[x]).decode("utf-8")
				#print entry
				#print notes
				data['entry'] = entry
				data['notes'] = notes

		#handle other entries
		
		else:

			#handle single par entries

			if headerLocs[i+1] - headerLocs[i] == 1:
				entry = pars[(headerLocs[i])].cssselect('strong')[0].text
				notes = scrapeEntry(lxml.html.tostring(pars[(headerLocs[i])]).decode("utf-8"))
				#print entry
				#print notes
				data['entry'] = entry
				data['notes'] = notes
				
			#or handle multi-par entries
				
			else:
				entry = pars[(headerLocs[i])].cssselect('strong')[0].text
				notes = lxml.html.tostring(pars[(headerLocs[i])]).decode("utf-8")
				if "<br>" in notes:
					notes = lxml.html.tostring(pars[(headerLocs[i])]).decode("utf-8").split('<br>')[1].split('</p>')[0]
				else:
					notes = ""
				if '</a>' in notes:
					notes = notes.split('</a>')[1]

				for x in range((headerLocs[i]+1),(headerLocs[i+1])):
					notes += lxml.html.tostring(pars[x]).decode("utf-8")
				# print(entry)
				# print(notes)
				data['entry'] = entry
				data['notes'] = notes
		
		#handle weird cases
		
		if data['entry'] != "":

			if data['notes'] == "German literary movement":
				data['entry'] = "Sturm und Drang"

			#print data
			styleData.append(data)

final = {"data": styleData, "lastUpdated": currDate + " " + currTime}

with open('style-guide.json', 'w') as f:
	json.dump(final, f, indent=4)

syncData(json.dumps(final, indent=4), "australia/2014/styleguide", "style-guide.json")

# output = StringIO.StringIO()
# output.write('{"data":')
# output.write(json.dumps(styleData))
# output.write(', "lastUpdated":"' + currDate + ' ' + currTime + '"')
# output.write('}')


# print "Connecting to S3"

# bucket = conn.get_bucket('gdn-cdn')

# from boto.s3.key import Key

# k = Key(bucket)
# k.key = "australia/2014/styleguide/style-guide.json"
# k.set_metadata("Cache-Control", "max-age=180")
# k.set_metadata("Content-Type", "application/json")
# k.set_contents_from_string(output.getvalue())
# k.set_acl("public-read")
# print "Done, JSON is updated"


#to write it locally for testing

#with open('../style-guide.json','w') as fileOut:
#		fileOut.write(output.getvalue())


# output.close()


