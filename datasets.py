import json
import re
from pyactiveresource.activeresource import ActiveResource
import argparse
import output_formatter
import stashq_elastic

API_KEY = '5dc85114b236db737339136e05d000cb1f291044'
index = '_all'
strict = True
output = False
es = stashq_elastic.connect()

def main(args):
	global strict
	global output

	output = None
	markers = []
	subjects = []
	study_or_type = []
	redmine = []

	parser = argparse.ArgumentParser()
	parser.add_argument('-o', '--output', nargs = '?', default = None, help = 'File to write output to')
	parser.add_argument('-m', '--marker', nargs = '*', default = None, help = 'Rs id marker of interest, ie rs12345')
	parser.add_argument('-s', '--subject', nargs = '*', default = None, help = 'Subjects of interest, ie ST-12345')
	parser.add_argument('-st', '--study_or_type', nargs = '*', default = None, help = 'Studies, or type of studies, ie CAMP or gwas')
	parser.add_argument('-u', '--unstrict', action = 'store_true', help = '')
	parser.add_argument('-r', '--redmine', nargs = '*', default = None, help = 'Search chanmine for datasets')
	parser.add_argument('unspecified', type = str, nargs = '*')

	a = parser.parse_args()
	a.unspecified.pop(0)

	if a.marker:
		markers.extend(a.marker)
	if a.subject:
		subjects.extend(a.subject)
	if a.study_or_type:
		study_or_type.extend(a.study_or_type)
	if a.unstrict:
		strict = False
	if a.redmine:
		redmine.extend(a.redmine)

	for arg in a.unspecified:
		# Check for output file
		if arg.endswith('.txt'):
			output = arg
			f = open(output, 'w')
		# Set rs number markers 
		elif re.match('^rs\d+', arg):
			markers.append(arg)
		# Set subject
		elif re.match('^ST-\d+', arg):
			subjects.append(arg)
		# Set strict or unstrict
		elif arg == 'unstrict':
			strict = False
		# Assume anything else is a study or type
		else:
			study_or_type.append(arg)

	if markers:
		marker_query(markers)

	if subjects:
		subject_query(subjects)

	if study_or_type:
		keyword_query(study_or_type)

	if redmine:
		redmine_query(redmine)

def help():
	print 'Each function takes a list of queries, and returns a list of databases and locations if available.'
	print 'marker_query(): rs number based search'
	print 'subject_query(): subject number based search'
	print 'keyword_query(): study or type keyword based search'
	print 'redmine_query(): search redmine specifically for study or type keyword'

def marker_query(*argv):
	if type(argv[0]) == list:
		markers = argv[0]
	else:
		markers = argv

	output_formatter.output('Query: %s' % ' '.join(markers), output, False)
	output_formatter.output('Marker\tIndex ID\tIndex', output, True)

	for marker in markers:
		docs = ['vcf_record']
		q = {
			'query': {
				'bool': {
					'must': [{'match': {'id': marker}}]
				}
			}
		}
		res = es.search(index=index, doc_type=docs, body=q)
		res_filtered = strictCheck(res, 'id', marker)
		results(res_filtered, 'id', 'marker')

def subject_query(*argv):
	if type(argv[0]) == list:
		subjects = argv[0]
	else:
		subjects = argv

	output_formatter.output('Query: %s' % ' '.join(subjects), output, False)
	output_formatter.output('Subject\tIndex ID\tIndex', output, False)

	for subject in subjects:
		docs = ['plink_fam_record']
		q = {
			'query': {
				'bool': {
					'must': [{'match': {'subject_id': subject}}]
				}
			}
		}
		res = es.search(index=index, doc_type=docs, body=q)
		if strict:
			res = strictCheck(res, 'subject_id', subject)
		else:
			res = res['hits']['hits']
		results(res, 'subject_id', 'subjectID')

def keyword_query(*argv):
	if type(argv[0]) == list:
		keywords = argv[0]
	else:
		keywords = argv

	output_formatter.output('Query: %s\n' % ' '.join(keywords), output, False)
	output_formatter.output('ID\tType\tIndex\tPath', output, True)

	for keyword in keywords:
		indices = []
		search_ind = []
		for index in es.indices.get_alias("*"):
			if keyword.lower() in index.lower():
				res = es.search(index=index)
				search_ind.append(res)
		for result in search_ind:
			for ind in result['hits']['hits']:
				path = 'N/A'
				if 'path' in ind:
					path = ind['path']
				output_formatter.output('%s\t%s\t"%s"\t(%s)' % (ind['_id'], ind['_type'], ind['_index'], path), output, True)

def redmine_query(*argv):
	if type(argv[0]) == list:
		keywords = argv[0]
	else:
		keywords = argv

	output_formatter.output('Query: %s\n' % ' '.join(keywords), output, False)
	output_formatter.output('ID\tCategory\tSubject\tPath', output, True)

	for keyword in keywords:
		try:
			datasets = Issue.find(None, None, tracker = 'Dataset', project_id = keyword)
			datasets = json.loads(datasets[0].to_json())
		
			for ds in datasets['issue']['issues']:
				path = 'N/A'
				for cf in ds.get('custom_fields', []):
					if cf['name'] == 'URL':
						path = cf['value']
			
				category = 'N/A'
				if 'category' in ds:
					category = ds['category']['name']
				
				output_formatter.output('%s\t%s\t"%s"\t(%s)' % (ds['id'], category, ds['subject'], path), output, True)
		except:
			output_formatter.output('No results found for %s' % arg, output, True)

def results(res, field, mark):
	for doc in res:
		index_id = doc['_id']
		query = doc['_source'][field]
		index = doc['_index']
		output_formatter.output('%s\t%s\t%s' % (query, index_id, index), output, True)

def strictCheck(res, field, mark):
	keep = []
	for i in range(0,len(res['hits']['hits'])):
		if res['hits']['hits'][i]['_source'][field] == mark:
			keep.append(i)
	res = [res['hits']['hits'][ind] for ind in keep]
	return res

class Issue(ActiveResource):
	_site = 'https://%s@chanmine.bwh.harvard.edu/' % (API_KEY)

if __name__ == "__main__":
    main(sys.argv[1:])