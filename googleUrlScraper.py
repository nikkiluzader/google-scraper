from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse
import csv

inputSheet = '1to4.csv'
outputSheet = 'experimentResults.csv'

cseId = "custom search engine id"
devKey = "API key"

searchTerm = ""
counter = 0
error1 = 'invalid search'
error2 = 'HTTP error'
searchInfo = []
ignoredWords = 'test 1 2 3'


# take list from csv and plug into array
def prepSearchArray(sheetToRead, arrayToUse):
    with open(sheetToRead) as csvFile:
        reader = csv.reader(csvFile)
        for each in reader:
            arrayToUse.append(each)


# get results from google search
def google_search(searchTerm, cseId, **kwargs):  # kwargs = keyworded arguments
    service = build("customsearch", "v1", developerKey=devKey)
    res = service.cse().list(q=searchTerm, cx=cseId, **kwargs).execute()
    # print (res)
    try:
        return res['items']
    except KeyError:
        res = error1
        return res


# get domain name from url
def getDomainName(urlToUse):
    parsed_uri = urlparse(urlToUse)
    urlToUse = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    # print(urlToUse) #for debugging
    return urlToUse


# append info to csv file
def writeCsv(sheetToWrite, thingToWrite):
    with open(sheetToWrite, 'a') as fp:
        wr = csv.writer(fp, dialect='excel', lineterminator='\n')
        wr.writerow([thingToWrite])


# count handling
def countAndPrint(counterToUse, messageToPrint):
    print(str(counterToUse) + ' ' + messageToPrint)


# execute google search and do all the cool stuff
def executeSearch(arrayToUse, counterToUse, wordsToIgnore):
    for each in arrayToUse:
        print(each)
        each = str(each).strip("['']")
        print(each)
        twoWords = each.split()
        twoWords = twoWords[0] + ' ' + twoWords[1]
        print(twoWords)
        try:
            results = google_search(each, cseId, num=1, excludeTerms=wordsToIgnore)
            counterToUse += 1
            if (results == error1):
                countAndPrint(counterToUse, error1)
                writeCsv(outputSheet, error1)
            else:
                for eachResult in results:
                    if twoWords in str(eachResult):
                        link = eachResult.get('link')
                        link = getDomainName(link)
                        countAndPrint(counterToUse, link)
                        writeCsv(outputSheet, link)
                        break
                    else:
                        link = 'no good links'
                        countAndPrint(counterToUse, link)
                        writeCsv(outputSheet, link)
        except HttpError:
            countAndPrint(counterToUse, error2)
            writeCsv(outputSheet, error2)


###################################main loop

prepSearchArray(inputSheet, searchInfo)

executeSearch(searchInfo, counter, ignoredWords)
