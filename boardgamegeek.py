#!/usr/bin/python
import simplescrape, pprint
"""
Sample use of simplescrape.py

Script to parse board game geek play records, found here:
    https://boardgamegeek.com/plays/bydate/user/<user>/subtype/boardgame
"""

# some super common UA:
user_agent = "<useragent>"
# URL to start at:
url = "https://boardgamegeek.com/plays/bydate/user/<user>/subtype/boardgame"
# This is how we will parse each page:
xpath = {
    'tr': {
        'each': "//table[@class='forum_table']//tr",
        'date': "th/a/text()",
        'game': "td/div[1]/a/text()",
        'description': "td/div[3]/text()"
    }
}

results = []
for page in simplescrape.autoUnpage(url, "//a[@title='next page']/@href", lambda url: simplescrape.dl2(url, ua=user_agent)):
    parsed = simplescrape.docExtract(xpath,page)
    # cleanup date mess
    currentDate = None
    for item in parsed['tr']:
        if 'date' in item:
            currentDate = item['date']
        if 'description' in item:
            item['date'] = currentDate
            if isinstance(item['description'],list): item['description'] = "".join(item['description'])
            item['description'] = item['description'].strip()
            results.append(item)

# output a CSV
print("date,game,description")
for result in results:
    print('"%s","%s","%s"' % (result['date'],result['game'],result['description']))



