""" Implement a REST client for the GoodReads API """

from xml.etree import ElementTree
import urllib.request

def bookInfoISBN(isbn):
  """
  Take a ISBN and query the GoodReads API for the info
  Parse the response and return a dictionary with fields:
    - average_score
    - image_url
    - description
  """
  devKey = '8JWRLazhbfMah62XrCf82A'

  # grab xml data from GoodReads
  xmlString = urllib.request.urlopen("https://www.goodreads.com/book/isbn/?isbn={}&format=xml&key={}".format(isbn, devKey)).read()

  # extract <average_score> and <image_url> from xml
  xmlRoot = ElementTree.fromstring(xmlString)
  xmlAverageScore = xmlRoot.iter('average_rating').__next__().text
  xmlImageUrl = xmlRoot.iter('image_url').__next__().text
  xmlDescription = xmlRoot.iter('description').__next__().text

  return {
    'average_score': xmlAverageScore,
    'image_url': xmlImageUrl,
    'description': xmlDescription
    }