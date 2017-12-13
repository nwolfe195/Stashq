from elasticsearch import Elasticsearch

def connect():
	try:
		es = Elasticsearch(
			'lagrange.bwh.harvard.edu:9200'
		)
		return es
	except Exception as ex:
		print "Error:", ex
