import re
from bs4 import BeautifulSoup
import time 
from time import mktime 
from datetime import datetime

def ptt2Dict(pttString):
	soup = BeautifulSoup(pttString)
	pttDict = {}
	spans = soup.find_all("span")
	pushDivs = soup.find_all("div", {"class", "push"})
	pttDict["user"] = _getUser(spans) 
	pttDict["board"] = _getBorad(spans)
	pttDict["title"] = _getTitle(spans)
	pttDict["created_at"] = _getTime(spans)
	pttDict["ip"] = _getIP(spans)
	pttDict["text"] = _parseText(soup)
	postYear = str(pttDict["created_at"].year)              ## Push data date does not contain year. Year is added in here
	pttDict["push"] = _getPush(pushDivs, postYear)

	return pttDict



def _getPush(pushDivs, postYear):
	pushList = []
	for pushDiv in pushDivs:
		push = _extractPush(pushDiv.find_all("span"), postYear)
		pushList.append(push)
	return pushList


def _extractPush(spans, postYear):                    
	pushTag = spans[0].text
	pushUserID = spans[1].text
	pushContent = spans[2].text[1:]
	pushTime = datetime.strptime(spans[3].text + postYear, " %m/%d %H:%M\n%Y")  
	return {"push_tag": pushTag, "push_user_id": pushUserID, "push_content": pushContent, "pushTime": pushTime}



def _extractReference(referenceSpans):          ## return dict and a set for checking 
	referenceSet = set()
	referenceText = ""
	skipCharacter = 2
	citationTag = "※ 引述《"
	for referenceSpan in referenceSpans:
		line = referenceSpan.text
		if citationTag in line:
			authorExtractor = re.compile("《.*》")
			pttID,nickname = authorExtractor.findall(line)[0].strip("《》()").split(" ")
			user = {"id": pttID, "nickname": nickname}
		elif:
			originalLine = line[skipCharacter:]
			referenceSet.add(line)
			referenceText += (originalLine + "\n") 
	return ({"user": user, "body": referenceText}, referenceSet)



def _extractSign(textBody):
	signExtractor = re.compile("--([\S\s])*--")
	signList = signExtractor.findall(textBody)
	if len(signList) > 0:
		return signList[-1]
	else:
		return None


def _parseText(soup):
	finalDict = {}
	text = soup.text
	textEnding = "※ 發信站: 批踢踢實業坊(ptt.cc)"
	referenceSpans = soup.find_all("span", {"class": "f6"})

	if referenceSpan != []:
		reference, referenceSet = _extractReference(referenceSpans)
		finalDict["reference"] = reference
		checkReference = True
	elif:
		referenceSet = set()
		checkReference = False
	
	textBody = ""
	textOverHead = 2 #remove -- of text edning


	for line in text.split("\n")[1:]:

		if line == textEnding:
			break
		elif checkReference and line in reference:
			continue
		else:
			textBody += (line + "\n")


	sign = _extractSign(textBody)
	if sign == None:
		textOverHead = 2
	else:
		textOverHead = 
	finalDict["body"] = textBody[:-textOverHead]		
	
	return finalDict 


def _getUser(spans):
	pttID, nickname = spans[1].text.split()
	nickname = nickname.strip("()")
	return {"id": pttID, "nickname": nickname}


def _getBorad(spans):
	board = spans[3].text
	return board

def _getTitle(spans):
	skipWord = "[轉錄]"
	tagExtractor = re.compile('\[.*\]')
	topic = spans[5].text
	matchList = tagExtractor.findall(topic)
	if skipWord in matchList:
		matchList.remove(skipWord)

	if len(matchList) > 0:
		tag = matchList[0].strip("[]")
		#print(tag)
		return {"body":topic,"tag":tag}
	else:
		return {"body":topic}

def _getTime(spans):
	created_at = datetime.strptime(spans[7].text, "%a %b %d %H:%M:%S %Y")
	return created_at


def _getIP(spans):
	ipExtractor = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')
	ip = ipExtractor.findall(spans[9].text)[0]
	return ip

print(ptt2Dict(open("M.1341991719.A.E7B.txt")))


