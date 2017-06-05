import os
import json
import subprocess
from bs4 import BeautifulSoup
import sys


def runProcess(commandString):
    p = subprocess.Popen(commandString, shell=True, stderr=subprocess.PIPE)
    output, err = p.communicate()

def urlFetch(targetFile,targetUrl):
    runProcess("wget --no-check-certificate --output-document \"" + targetFile + "\" \""+targetUrl+"\"")

def downloadApps(targetAppDownloadLinks,targetDir):
    for category in targetAppDownloadLinks.keys():
        targetCategoryDir = targetDir + "/" + category
        if not os.path.exists(targetCategoryDir):
            os.makedirs(targetCategoryDir)
        for app in targetAppDownloadLinks[category].keys():
            targetFile = targetCategoryDir + "/" + app + ".apk"
            if not os.path.exists(targetFile):
                print "Downloading:"+targetAppDownloadLinks[category][app]+" to "+targetFile
                urlFetch(targetFile, targetAppDownloadLinks[category][app])
    

def slideme_getAllAppLinks(targetAppLinkDict,targetFileName,topUrl):
    targetData = None
    with open (targetFileName, "r") as myfile:
        targetData=myfile.read()
    if targetData:
        parsed_html = BeautifulSoup(targetData)
        for childApp in parsed_html.find("ul", { "class" : "category-template" }).find_all("li"):
            urlLink = childApp.find("div",{"class":"category-template-down"}).find("a").get("href")
            targetUrl = topUrl + urlLink
            if not (targetUrl in targetAppLinkDict):
                targetAppLinkDict.append(targetUrl)
        
def slideme_getAppDownloadLinks(targetAppDownloadLinks,targetAppLinkDict,tempWorkingDir):
    targetData = None
    targetFileName = tempWorkingDir + "/dummyAppd.html"
    for tempUrl in targetAppLinkDict:
        urlFetch(targetFileName,tempUrl)
        with open (targetFileName, "r") as myfile:
            targetData=myfile.read()
        if targetData:
            parsed_html = BeautifulSoup(targetData)
            for childApp in parsed_html.find_all("div", { "class" : "fast-download-box" }):
                try:
                    appName = childApp.find("h1").find("span",{"class":"file"}).get_text()
                    for para in childApp.find_all("p"):
                        try:
                            urlLink=para.find("a",{"id":"download_link"}).get("href")
                        except:
                            pass
                    category = "entertainment"
                    targetKey = category.lower()
                    appName = str(appName).strip()
                    if not (targetKey in targetAppDownloadLinks):
                        targetAppDownloadLinks[targetKey] = {}
                    if not (appName in targetAppDownloadLinks[targetKey]):
                        targetAppDownloadLinks[targetKey][appName] = urlLink
                except:
                    pass

if len(sys.argv) != 3:
    print "Usage:"+sys.argv[0] +" <downloadDirectory> <tempWorkingDir>"
    sys.exit(-1)

tempWorkingDir = sys.argv[2]
downloadDir = sys.argv[1]
if not os.path.exists(tempWorkingDir):
    os.makedirs(tempWorkingDir)
if not os.path.exists(downloadDir):
    os.makedirs(downloadDir)
maxPageNumber = 20
urlPrefix = "https://apkpure.com/entertainment?page="
currPageNo = 1
while currPageNo <= maxPageNumber:   
    targetAppLinks = []
    targetAppDownloadLinks = {}
    targetUrl = urlPrefix + str(currPageNo)
    targetFileName = tempWorkingDir + "/dummyd.html"
    currPageNo = currPageNo + 1
    urlFetch(targetFileName, targetUrl)
    slideme_getAllAppLinks(targetAppLinks, targetFileName,"http://apkpure.com")
    slideme_getAppDownloadLinks(targetAppDownloadLinks,targetAppLinks,tempWorkingDir)
    downloadApps(targetAppDownloadLinks,downloadDir)
    
