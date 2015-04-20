#!/usr/bin/python
#
# Expose the Hive search engine via a simple web form
#

from django.template import Context, loader
from datetime import datetime, date, time
from django import forms
from django.http import HttpResponse

from hive_job_parser import HiveJobListing
import os

from whoosh import index as wh_index
from whoosh.qparser import MultifieldParser
from whoosh.query import DateRange


INDEX_PATH = os.path.expanduser('~') + '/data/hive_search/index/'
JOB_BASE_DIR = 'http://hive.example.com'

DT_FORMAT = '%Y-%m-%d'
DEFAULT_START_DATE = '2014-04-28'


class QueryForm(forms.Form):
  q = forms.CharField(widget=forms.TextInput(attrs={'size':'30'}))
  fromDate = forms.DateField(widget=forms.TextInput(
      attrs={'size':'20', 'class':'datePicker'}))
  toDate = forms.DateField(widget=forms.TextInput(
      attrs={'size':'20', 'class':'datePicker'}))

def index(request):
  template = loader.get_template('hive_search/index.html')

  # Setup the search form
  query = request.GET.get('q', 'example')
  fromDate = request.GET.get('fromDate', DEFAULT_START_DATE)
  fromDate = datetime.strptime(fromDate, DT_FORMAT).date()
  toDate = request.GET.get('toDate', date.today().strftime(DT_FORMAT))
  toDate = datetime.strptime(toDate, DT_FORMAT).date()

  form = QueryForm(initial = {'q': query, 'fromDate':fromDate, 'toDate':toDate})

  # Perform the actual query
  ix = wh_index.open_dir(INDEX_PATH)
  query_parser = MultifieldParser(["owner", "query", "title"],
                                  schema=HiveJobListing())
  parsed_query = query_parser.parse(unicode(query))

  time_filter = DateRange("completion_time",
                          datetime.combine(fromDate, time(0,0,0)),
                          datetime.combine(toDate, time(23,59,59)))

  with ix.searcher() as searcher:
    results = []
    results_object = searcher.search(parsed_query, limit=50, filter=time_filter)
    results_object.fragmenter.surround = 60

    for result in results_object:
      result_fields = result.fields()

      snippet = result.highlights('query', top=3)
      result_fields['snippet'] = snippet if snippet else result['query'][:120]
      title = result.highlights('title')
      if title: result_fields['title'] = title
      result_fields['job_url'] = JOB_BASE_DIR + result['job_url']

      results.append(result_fields)

  context = Context({
    'form':form,
    'fromDate':fromDate,
    'toDate':toDate,
    'firstDate': datetime.strptime(DEFAULT_START_DATE, DT_FORMAT).date(),
    'results':results
    })

  return HttpResponse(template.render(context))
