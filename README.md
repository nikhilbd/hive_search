# Hive search engine

This is a self-contained, functional search engine to search over past [Hive](https://hive.apache.org/) jobs. It consists of 2 distinct parts:
1. An indexer written using the [Whoosh](https://pypi.python.org/pypi/Whoosh/) and the [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/) packages
2. A Django app for searching over the indexed jobs

#### Prerequisites
1. Install [Beautiful Soup](http://www.crummy.com/software/BeautifulSoup/)
2. Install [Whoosh](https://pypi.python.org/pypi/Whoosh)

#### Some things you will need to do to run this

1. Scraping the Hive jobs is dependent on the Hive interface that you use. You will need to modify `hive_job_parser.py` to work your Hive interface
2. There are a couple of paths defined on the top of `views.py` and `hive_job_indexer.py` that you will need to modify to work for you
3. You need to setup a cron job to run the indexing script periodically (say every hour). This will crawl and index the completed Hive jobs
```python <path_to_hive_job_indexer.py> &>> <path_to_a_log_file>
```
4. You need setup the web app using [Django](https://www.djangoproject.com/start/)
