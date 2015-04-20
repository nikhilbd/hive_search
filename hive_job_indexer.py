#!/usr/bin/python
#
# Gets jobs from a Hive recent jobs page and indexes them on
# disk-based indexes
#

import urllib2, datetime, os
from hive_job_parser import HiveJobListing, HiveJobScraper
from whoosh import index


JOB_BASE_DIR = 'http://hive.example.com'


class HiveJobIndexer():

  def __init__(self):

    # Change this dir to where you want to save the search index
    self._data_dir = os.path.expanduser('~') + '/data/hive_search/'
    self._index_dirname = 'index/'
    self._index_dir = os.path.join(self._data_dir, self._index_dirname)

    self._job_url = JOB_BASE_DIR + '/hive_jobs/recent'

    # We save the last time we did a crawl in _last_job_filename
    self._last_job_filename = 'last_job_time'
    self._last_job_file = os.path.join(self._data_dir, self._last_job_filename)

    self._dt_format = "%Y-%m-%d %H:%M:%S"

  def get_last_job_time(self):
    ''' Read the _last_job_file to get the datetime for the last indexed job'''

    with open(self._last_job_file, 'r') as f:
      try:
        dt = datetime.datetime.strptime(f.read(), self._dt_format)
      except ValueError:
        dt = datetime.datetime(2001,01,01)
      return dt

  def set_last_job_time(self, last_job_time):
    with open(self._last_job_file, 'w') as f:
      f.write(str(last_job_time))

  def get_new_jobs(self):
    content = urllib2.urlopen(self._job_url).read()
    scraper = HiveJobScraper()
    jobs = scraper.parse_content(content)
    return jobs

  def create_index(self):
    return index.create_in(self._index_dir, HiveJobListing)

  def get_index_writer(self, clear=False):
    if clear:
      ix = self.create_index()
    else:
      if index.exists_in(self._index_dir):
        ix = index.open_dir(self._index_dir)
      else:
        ix = self.create_index()
    return ix.writer()

  def index(self):
    '''
    The indexing script does the following steps:
    1. Crawl the recent jobs page and get all the jobs listed there
    2. Read the time of the last indexed job
    3. Index all the jobs from Step 1 which were run after the time in Step 2
    4. Save the time of the latest job as the new last indexed job
    '''

    print '%s: Starting run. Scraping job site...' % datetime.datetime.now()

    jobs = self.get_new_jobs()
    last_job_time = self.get_last_job_time()

    print '%s: Indexing new jobs...' % datetime.datetime.now()
    writer = self.get_index_writer()

    latest_job_time = last_job_time
    new_jobs = 0
    for job in jobs:
      job_time = job.completion_time
      if (job_time > last_job_time):
        writer.add_document(job_url=job.job_url, title=job.title, owner=job.owner,
                            completion_time=job.completion_time, query=job.query)
        new_jobs += 1
      if (job_time > latest_job_time):
        latest_job_time = job_time

    writer.commit()
    self.set_last_job_time(latest_job_time)

    print '%s: Done! Added %d (out of %d) new jobs to the index' % (
      datetime.datetime.now(), new_jobs, len(jobs))

def main():
  indexer = HiveJobIndexer()
  indexer.index()

if __name__ == "__main__":
  main()
