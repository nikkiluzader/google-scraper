"""
Google URL Scraper

This module is used to scrape data from the internet.

@author: Nikki Luzader
@contributors: John Ryan
"""

from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from urllib.parse import urlparse
import csv


# GLOBAL CONSTANTS #############################################################

ERROR1 = 'invalid search'
ERROR2 = 'HTTP error'
COUNTER = 0

################################################################################


def prep_search_array(sheet_to_read):
    """ take list from csv and plug into array """

    with open(sheet_to_read) as csvFile:
        result = []
        reader = csv.reader(csvFile)
        for each in reader:
            result.append(each)

        return result


def google_search(search_term, cse_id, api_key, **kwargs):
    """
    get results from google search
    kwargs = keyworded arguments
    """

    service = build("customsearch", "v1", developerKey=api_key)
    res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
    try:
        return res['items']
    except KeyError:
        return ERROR1


def get_domain_name(url_to_use):
    """
    get domain name from url
    """

    parsed_uri = urlparse(url_to_use)
    url_to_use = '{uri.scheme}://{uri.netloc}/'.format(uri=parsed_uri)
    # print(urlToUse) #for debugging
    return url_to_use


def write_csv(sheet_to_write, thing_to_write):
    """ append info to csv file """

    with open(sheet_to_write, 'a') as fp:
        wr = csv.writer(fp, dialect='excel', lineterminator='\n')
        wr.writerow([thing_to_write])


def count_and_print(message_to_print):
    """ # count handling """

    print(str(COUNTER) + ' ' + message_to_print)


def execute_search(array_to_use, words_to_ignore, api_key, cse_id):
    """ execute google search and do all the cool stuff """

    for each in array_to_use:
        # Get second to last word and first word of each line
        each = str(each).strip("['']")
        words = each.split()
        second_to_last_word = words[len(words)-2]
        first_word = words[0]

        try:
            results = google_search(each, cse_id, api_key, excludeTerms=words_to_ignore)
            COUNTER += 1
            if (results == error1):
                count_and_print(error1)
                write_csv(outputSheet, error1)
            else:
                if second_to_last_word or first_word in str(results):
                    for eachResult in results:
                        if second_to_last_word or first_word in str(eachResult):
                            link = eachResult.get('link')
                            link = get_domain_name(link)
                            count_and_print(link)
                            write_csv(outputSheet, link)
                            break
                else:
                    try:
                        results = google_search(each, cse_id, api_key, excludeTerms=words_to_ignore, start=10)
                        if (results == error1):
                            count_and_print(error1)
                            write_csv(outputSheet, error1)
                        else:
                            if second_to_last_word or first_word in str(results):
                                for eachResult in results:
                                    if second_to_last_word or first_word in str(eachResult):
                                        link = eachResult.get('link')
                                        link = get_domain_name(link)
                                        count_and_print(link)
                                        write_csv(outputSheet, link)
                                        break
                            else:
                                link = 'no good links'
                                count_and_print(link)
                                write_csv(outputSheet, link)
                    except HttpError:
                        count_and_print(error2)
                        write_csv(outputSheet, error2)
                    except TypeError:
                        count_and_print('type error')
                        write_csv(outputSheet, 'type error')
        except HttpError:
            count_and_print(error2)
            write_csv(outputSheet, error2)
        except TypeError:
            count_and_print('type error')
            write_csv(outputSheet, 'type error')

def main ():
    """ main loop """

    import json

    with open('.env.json') as json_data:
        ENV = json.load(json_data)

    inputSheet = '1to4.csv'
    outputSheet = 'experimentResults.csv'

    ignoredWords = 'walmart news petassure hotel insurance'

    search_info = prep_search_array(inputSheet)
    execute_search(search_info, ignoredWords, ENV["API_KEY"], ENV["CSE_ID"])

if __name__ == '__main__':
    main()
