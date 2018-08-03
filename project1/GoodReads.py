""" Implement a REST client for the GoodReads API """

"""
Take a ISBN and query the GoodReads API for the info
parse the response and return a dictionary with fields:
  - average_score
  - image_url
"""
def bookInfoISBN(isbn):
  return {
    # TODO: replace these test values
    'average_score': 0,
    'image_url': 'https://images.gr-assets.com/books/1388321463m/41804.jpg'
    }