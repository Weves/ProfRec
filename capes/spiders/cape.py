# -*- coding: utf-8 -*-
import scrapy
import re
from ucsdProf.prof import Prof
import os
import pandas as pd

cnames = []


def reformat_num(string):

	valid = re.compile('[0-9.]+')
	number = re.compile('[0-9]')
	
	start = 0
	while (number.match(string[start]) == None):
		start += 1
		if (start >= len(string)):
			return 0

	num = valid.match(string[start:len(string)])
	return float(num.group())


def reformat_url(string):	

	i = len(string) - 1
	ret = ""

	while (i >= 0):
		if (string[i] == '+'):
			ret = ' ' + ret
		elif(string[i] == '='):
			return ret
		else:
			ret = string[i] + ret
		i -= 1

def reformat_cname(string):

	scount = 0

	for i in range(len(string)):
		if (string[i] == ' ' and scount > 0):
			return string[0:i]
		elif(string[i] == ' '):
			scount += 1

def GetOverall(r):
	avge = sum(r['Avg Expected GPA']) / len(r)
	avgr = sum(r['Avg Recieved GPA']) / len(r)
	rclass = sum(r['Rec Class']) / len(r)
	rprof = sum(r['Rec Instructor']) / len(r)
	shours = sum(r['Study Hours']) / len(r)
	enroll = sum(r['Enroll'])
	evals = sum(r['Evals'])
	return pd.Series([enroll, evals, rclass, rprof, shours, avge, avgr], index = ['Enroll', 'Evals', 'Rec Class', \
				'Rec Instructor', 'Study Hours', 'Avg Expected GPA', 'Avg Recieved GPA'])

def make_prof(row):
	prof = Prof(row[0], row[3], row[4], row[5], row[6], row[7], row[8])
	return prof

def data_into_dict(cname, bCells, mCells, cCells):
	
	numBCol = 3
	numMCol = 6
	rows = [[]]
	index = 0
	count = 0
	valid = re.compile('\w')

	# go through the basic info and divide it into rows
	for i in range(len(bCells)):
		match = valid.match(bCells[i][0])
		if (match != None):
			count += 1
			if (count > numBCol):
				index += 1
				count = 1
				rows.append([])
			
			if (count > 2):
				ins = reformat_num(bCells[i].strip())
			else:
				ins = bCells[i].strip()
			rows[index].append(ins)
	
	index = 0
	count = 0
	# go into the more involved info and put it in the appropriate row
	for i in range(len(mCells)):
		if (mCells[i] == 'CAPE Results'):
			continue
		match = valid.match(mCells[i][0])
		if (match != None):
			count += 1
			if (count > numMCol):
				index += 1
				count = 1
				rows.append([])
			
			
			ins = reformat_num(mCells[i])
			rows[index].append(ins)

	# go through and format the class names correctly
	for i in range(len(cCells)):
		cCells[i] = reformat_cname(cCells[i])
	
	
	tdict = {}
	pdd = {}
	profs = []
	pdd['Professor'] = []
	pdd['Class'] = []
	pdd['Enroll'] = []
	pdd['Evals'] = []
	pdd['Rec Class'] = []
	pdd['Rec Instructor'] = []
	pdd['Study Hours'] = []
	pdd['Avg Expected GPA'] = []
	pdd['Avg Recieved GPA'] = []

	#i = 2
	for val in rows:
		#if (len(val) > 0 and cCells[i] == cname):
		if (len(val) > 0):
			if val[0] not in tdict:
				prof = make_prof(val)
				tdict[val[0]] = prof
				#tdict[val[0]] = val
				
				
			else:
				prof = tdict[val[0]]
				prof.evals += val[3]
				prof.rcmndc = ((prof.rcmndc * prof.taught) + val[4]) / (prof.taught + 1)
				prof.rcmndp = ((prof.rcmndp * prof.taught) + val[5]) / (prof.taught + 1)
				prof.study = ((prof.study * prof.taught) + val[6]) / (prof.taught + 1)
				prof.avge = ((prof.avge * prof.taught) + val[7]) / (prof.taught + 1)
				prof.avgr = ((prof.avgr * prof.taught) + val[8]) / (prof.taught + 1)
				prof.taught += 1
			
			profs.append(val[0])
			pdd['Professor'].append(val[0])	
			pdd['Class'].append(cname)	
			pdd['Enroll'].append(val[2])	
			pdd['Evals'].append(val[3])	
			pdd['Rec Class'].append(val[4])	
			pdd['Rec Instructor'].append(val[5])	
			pdd['Study Hours'].append(val[6])	
			pdd['Avg Expected GPA'].append(val[7])	
			pdd['Avg Recieved GPA'].append(val[8])	
		
		#i += 1

	
	df = pd.DataFrame(pdd, index=profs)
	dfp = df.groupby(['Professor', 'Class'])
	dfo = dfp.apply(GetOverall).sort_values(by='Rec Instructor', ascending=False)

	#print (df)
	print (dfo)

	#for prf in tdict:
	#	print(cname)
	#	print(tdict[prf].pname + " " + str(tdict[prf].rcmndp) + "%" + '\n')

class CapeSpider(scrapy.Spider):
	name = 'cape'
	allowed_domains = ['www.cape.ucsd.edu/', 'www.ratemyprofessors.com/']
	start_urls = ['http://www.cape.ucsd.edu/', 'http://www.ratemyprofessors.com/']

	def start_requests(self):
		urls = []

		# get the names of the classes we want to look at
		f = open('cnames.txt', 'r')
		for line in f:
			cname = line.strip('\n')
			cnames.append(cname)
			u = 'http://www.cape.ucsd.edu/responses/Results.aspx?Name=&CourseNumber=' + cname
			urls.append(u)

		f.close()

		# go through each class
		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse)

	def parse(self, response):
		
		# get relevent info from website
		baseCells = response.selector.xpath('//td/text()').extract()
		moreCells = response.selector.xpath('//span/text()').extract()
		classCells = response.selector.xpath('//a/text()').extract()

		# reformat class name to be more readable
		cname = reformat_url(response.url)

		data_into_dict(cname, baseCells, moreCells, classCells)
	

