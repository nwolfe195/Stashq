import re
import numpy 
import argparse
import output_formatter
import stashq_elastic

output = False
es = stashq_elastic.connect()

def main(args):
	global output
	version = False
	output = None
	rs_search_terms = []
	location = []
	bims = []

	parser = argparse.ArgumentParser()
	parser.add_argument('unspecified', type = str, nargs = '*')
	parser.add_argument('-o', '--output', nargs = '?', default = None, help = 'File to write output to')
	parser.add_argument('-l', '--location', nargs = '*', default = None, help = 'Location of snp of interest.  Format chromosome number:chromosome location, ie 7:12345')
	parser.add_argument('-m', '--marker', nargs = '*', default = None, help = 'Rs id marker of interest, ie rs12345')
	parser.add_argument('-b', '--bim', nargs = '*', default = None, help = 'bim file to read rs ids from')
	parser.add_argument('-i', '--index', nargs = '?', default = None, help = 'Specific .vcf file to look through.  Defaults to most recent')
	parser.add_argument('-v', '--version', action = 'store_true', help = 'Get information about which indices are available')

	a = parser.parse_args()
	a.unspecified.pop(0)

	if a.location:
		location.extend(a.location)
	if a.marker:
		rs_search_terms.extend(a.marker)
	if a.bim:
		bims.extend(a.bim)
	if a.index:
		index = a.index
	if a.version:
		version = True

	for arg in a.unspecified:
		# Set output file
		if arg.endswith('.txt'):
			output = arg
		# Get marker
		elif re.match('^rs\d+', arg):
			rs_search_terms.append(arg)
		# Get location
		elif re.match('^\d:\d+', arg):
			location.append(arg)
		# Get bim
		elif arg.endswith('.bim'):
			rs_search_terms.extend(numpy.genfromtxt(arg, dtype='str')[:,1].tolist())
		# Get version
		elif arg.endswith('.vcf'):
			index = arg
	
	if version:
		getIndicesList()
		exit()

	if rs_search_terms:
		marker_query(', '.join(rs_search_terms))

	if location:
		chrom_query(', '.join(location))

def help():
	print 'Each function takes a list of queries.  If an index besides the most recent is required, enter its name as the first parameter.'
	print 'chrom_query(): chromosomal locations'
	print 'marker_query(): rs number'
	print 'bim_query(): all rs numbers contained in selected .bim files'

def bim_query(*argv):
	if argv[0].endswith('.bim'):
		index = getCurrentIndex()
		bims = argv
	else:
		index = argv[0]
		bims = argv[1:]

	output_formatter.output('Query: %s' % ' '.join(argv), output, False)
	for bim in bims:
		rsids = numpy.genfromtxt(bim, dtype='str')[:,1].tolist()
		output_formatter.output('%s' % bim, output, True)
		output_formatter.output('rs number\tlocation\treference allele\talternative allele\tindex', output, True)

		for rsid in rsids:
			q = {
				'query': {
					'bool': {
						'must': [{'match': {'id': rsid}}]
					}
				}
			}
			res = es.search(index=index, size=10000, body=q)
			results(res)

def chrom_query(*argv):
	if re.match('^\d:\d+', argv[0]):
		index = getCurrentIndex()
		locs = argv
	else:
		index = argv[0]
		locs = argv[1:]

	output_formatter.output('Query: %s' % ' '.join(argv), output, False)
	output_formatter.output('rs number\tlocation\treference allele\talternative allele\tindex', output, True)

	for loc in locs:
		(chrom, position) = loc.split(':')
		q = {
			'query': {
				'bool': {
					'minimum_should_match': '1',
					'must': [{'match': {'chrom': chrom}}],
					'should': [{'match': {'start_pos': position}}]
				}
			}
		}
		res = es.search(index=index, size=10000, body=q)
		return results(res)

def marker_query(*argv):
	if re.match('^rs\d+', argv[0]):
		index = getCurrentIndex()
		rsids = argv
	else:
		index = argv[0]
		rsids = argv[1:]

	output_formatter.output('Query: %s' % ' '.join(argv), output, False)
	output_formatter.output('rs number\tlocation\treference allele\talternative allele\tindex', output, True)

	for rsid in rsids:
		q = {
			'query': {
				'bool': {
					'must': [{'match': {'id': rsid}}]
				}
			}
		}
		res = es.search(index=index, size=10000, body=q)
		results(res)

def results(res):
	data = []
	for doc in res['hits']['hits']:
		rsid = doc['_source']['id']
		chrom = doc['_source']['chrom']
		start = doc['_source']['start_pos']
		alleles = doc['_source']['alleles']
		ref = None
		alts_list = []
		for i in range(0,len(alleles)):
			if len(alleles[i]) == 2:
				ref = alleles[i].get('allele')
			else:
				alts_list.append(alleles[i].get('allele'))
		alts = ''.join(alts_list)
		ind = doc['_index']		
		output_formatter.output('%s\t%s:%s\t%s\t%s\t%s' % (rsid, chrom, start, ref, alts, ind), output, True)

def getCurrentIndex():
	indices = getIndices()
	indices.sort(key=natural_keys)
	return indices[0]

def getIndices():
	indices = []
	for index in es.indices.get_alias("*"):
		dotSplit = index.split('.')
		if dotSplit[-1] == 'vcf':
			indices.append(index)
	return indices	

def getIndicesList():
	indices = getIndices()
	print 'Index\tVersion'
	for index in indices:
		res = es.indices.get(index=index)
		version = res[index]['settings']['index']['version']['created']
		print '%s\t%s' % (index, version)

def natural_keys(text):
	return [ atoi(c) for c in re.split('(\d+)', text)]

def atoi(text):
	return int(text) if text.isdigit() else text

if __name__ == "__main__":
    main(sys.argv[1:])