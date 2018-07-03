from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse
import csv

inputSheet = '1to4.csv'
outputSheet = 'experimentResults.csv'

cseId = "custom search engine ID"
devKey = "API key"

searchTerm = ""
counter = 0
error1 = 'invalid search'
error2 = 'HTTP error'
searchInfo = []
ignoredWords = 'walmart news petassure hotel insurance'


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
        #print(each)
        each = str(each).strip("['']")
        #print(each)
        words = each.split()
        words = words[len(words)-2]
        words2 = words[0]
        #print(words)
        try:
            results = google_search(each, cseId, excludeTerms=wordsToIgnore)
            counterToUse += 1
            if (results == error1):
                countAndPrint(counterToUse, error1)
                writeCsv(outputSheet, error1)
            else:
                if words or words2 in str(results):
                    for eachResult in results:
                        if words or words2 in str(eachResult):
                            link = eachResult.get('link')
                            link = getDomainName(link)
                            countAndPrint(counterToUse, link)
                            writeCsv(outputSheet, link)
                            break
                else:
                    try:
                        results = google_search(each, cseId, excludeTerms=wordsToIgnore, start=10)
                        #counterToUse += 1
                        if (results == error1):
                            countAndPrint(counterToUse, error1)
                            writeCsv(outputSheet, error1)
                        else:
                            if words or words2 in str(results):
                                for eachResult in results:
                                    if words or words2 in str(eachResult):
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
                    except TypeError:
                        countAndPrint(counterToUse, 'type error')
                        writeCsv(outputSheet, 'type error')
        except HttpError:
            countAndPrint(counterToUse, error2)
            writeCsv(outputSheet, error2)
        except TypeError:
            countAndPrint(counterToUse, 'type error')
            writeCsv(outputSheet, 'type error')



###################################main loop

prepSearchArray(inputSheet, searchInfo)

executeSearch(searchInfo, counter, ignoredWords)





########testingbelow


# word = 'westbrook'
#
# test = google_search('Westbrook Animal Hospital Westbrook ME', cseId, excludeTerms=ignoredWords)
#
# print(str(test))
#
# if word in str(test):
#     for each in test:
#         if word in str(each):
#             link = each.get('link')
#             link = getDomainName(link)
#             print(link)
#             break
#         else:
#             print('checking next result...')
# else:
#     test = google_search('Bowen Animal Hospital Abbeville SC', cseId, excludeTerms=ignoredWords, start=10)
#     if word in str(test):
#         for each in test:
#             if word in str(each):
#                 link = each.get('link')
#                 link = getDomainName(link)
#                 print(link)
#                 break
#             else:
#                 print('checking next result...')
#     else:
#         print('nothing')
