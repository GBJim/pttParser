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
	postYear = _getYear(pttDict["created_at"])            ## Push data date does not contain year. Year is added in here
	#print(postYear)
	pttDict["push"] = _getPush(pushDivs, postYear)

	return pttDict



def _getYear(created_at):
	if created_at == None:
		return None
	else:
		return str(created_at.year)


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
	if postYear == None:
		pushTime = None
	else:
		pushTime = datetime.strptime(spans[3].text + postYear, " %m/%d %H:%M\n%Y")  
	return {"push_tag": pushTag, "push_user_id": pushUserID, "push_content": pushContent, "pushTime": pushTime}



def _extractReference(referenceSpans):          ## return dict and a set for checking 
	referenceSet = set()
	referenceText = ""
	skipCharacter = 2
	user = None
	replaceString = "《》()"
	citationTag = "※ 引述《"
	for referenceSpan in referenceSpans:
		line = referenceSpan.text
		if citationTag in line:
			authorExtractor = re.compile("《.*》")
			line = authorExtractor.findall(line)[0]
		
			#print(authorExtractor.findall(line)[0].replace("《》()","").split(" "))
			for char in replaceString:
				line = line.replace(char, "")
			#print(line.split(" "))
			pttID,nickname = line.split(" ")[0:2]
			user = {"id": pttID, "nickname": nickname}

		else:
			originalLine = line[skipCharacter:]
			referenceSet.add(line)
			referenceText += (originalLine + "\n") 
	if user == None:
		return ({"body": referenceText}, referenceSet)
	else:
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

	if referenceSpans != []:
		reference, referenceSet = _extractReference(referenceSpans)
		finalDict["reference"] = reference
		checkReference = True
	else:
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
		textOverHead = 4 + len(sign)
	finalDict["body"] = textBody[:-textOverHead]		
	
	return finalDict 


def _getUser(spans):
	userSpan = None
	for span in spans:
		if span.text == "作者":
			userSpan = span.nextSibling
			break
	if userSpan == None:
		user = None
	else:

		pttID = userSpan.text.split()[0]
		nicknameExtractor = re.compile("\((.*)\)")
		nickname = nicknameExtractor.findall(userSpan.text)[0]
		user = {"id": pttID, "nickname": nickname}
	#print(pttID,nickname)
	return user


def _getBorad(spans):
	boardSpan = None
	for span in spans:
		if span.text == "看板":
			boardSpan = span.nextSibling
			break
	
	if boardSpan == None:
		board = None
	else:
		board = boardSpan.text

	
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
	timeSpan = None
	for span in spans:
		if span.text == "時間":
			timeSpan = span.nextSibling
			break
	if timeSpan == None:
		return None
	else:
		created_at = datetime.strptime(timeSpan.text, "%a %b %d %H:%M:%S %Y")
		return created_at


def _getIP(spans):
	ipText = None
	for span in spans:
		if span.text == "◆ From: ":
			ipText = span.text
			
	if ipText == None:
		ip = None
	else:
		ipExtractor = re.compile('[\d]+\.[\d]+\.[\d]+\.[\d]+')
		#print(ipText)
		ip = ipExtractor.findall(ipText)[0]

	return ip


