#!/usr/bin/python
#
# Classes to aid parsing of jobs from the Hive recent jobs page
#
# Usage: cat saved.html | hive_job_parser.py
#

from bs4 import BeautifulSoup
import re, sys, datetime
from whoosh.fields import SchemaClass, TEXT, KEYWORD, ID, DATETIME
from whoosh.analysis import RegexTokenizer, LowercaseFilter, StopFilter

QUERY_ANALYZER = RegexTokenizer('\w+|\d+') | LowercaseFilter() | StopFilter()

class HiveJobListing(SchemaClass):
  '''Class to store the details associated with each Hive job'''

  job_url = ID(stored=True)
  title = TEXT(stored=True,analyzer=QUERY_ANALYZER)
  owner = KEYWORD(stored=True)
  completion_time = DATETIME(stored=True)
  query = TEXT(stored=True,analyzer=QUERY_ANALYZER)

  def __init__(self):
    self.job_url = None
    self.title = None
    self.owner = None
    self.completion_time = None
    self.query = None

  def __str__(self):
    return 'Url: %s, Title: %s, Owner: %s, Time: %s, Query: %s...' % (
      self.job_url, self.title, self.owner, self.completion_time, self.query[0:10])

class HiveJobScraper:
  def __init__(self):
    self._time_pattern = re.compile('\d{4}-\d\d-\d\d \d\d:\d\d:\d\d')
    self._email_pattern = re.compile('^by (\w+)@')

  def parse_content(self, doc):

    soup = BeautifulSoup(doc)
    jobs = []

    for job_html in soup.find_all(class_='hive_job'):

      status = job_html.find(class_='jobStatus').get_text().lower()
      if status != 'completed': continue

      # Fill in the fields of a HiveJobListing from the parsed job content
      hive_job = HiveJobListing()
      hive_job.job_url = unicode(job_html.find(class_="jobHeader").find('a')
                                 .get('href'))
      hive_job.title = job_html.find(class_="jobHeader").find('a').get_text()

      email_text = job_html.find(class_="emailSpan").get_text()
      match = re.search(self._email_pattern, email_text)
      hive_job.owner = match.group(1) if match else ''

      time_text = job_html.find(class_="time").get_text()
      match = re.search(self._time_pattern, time_text)
      time_string = match.group(0) if match else ''
      hive_job.completion_time = datetime.datetime.strptime(
        time_string, "%Y-%m-%d %H:%M:%S")

      hive_job.query = job_html.find(class_="job_query").get_text()

      if not (hive_job.job_url and hive_job.title and hive_job.owner and
              hive_job.completion_time and hive_job.query):
        print '***** Cannot parse all the details ***** '
        print 'Url: %s\nTitle: %s\nOwner: %s\n\Time: %s\nQuery: %s\n.Html: %s' % (
          hive_job.job_url, hive_job.title, hive_job.owner,
          hive_job.completion_time, hive_job.query, job_html)

      jobs.append(hive_job)
    return jobs

def main():
  ''' For testing'''

  doc = ''.join([line for line in sys.stdin])
  scraper = HiveJobScraper()
  results = scraper.parse_content(doc)

  for result in results:
    print result

if __name__ == "__main__":
  main()
