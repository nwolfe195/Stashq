from AIMS.SAPPHIRE import SDIAlias, Sample, SampleFamily, Subject, Cohort
from AIMS.Generations import util as db
import sys
import argparse
import re
import output_formatter

output = None
lv = db.connect('sapphire_r@labvprd')

def main(args):
	global output

	subjects = []
	samples = []
	aliases = []

	parser = argparse.ArgumentParser()
	parser.add_argument('unspecified', type = str, nargs = '*')
	parser.add_argument('-o', '--output', nargs = '?', default = None, help = 'File to write output to')
	parser.add_argument('-su', '--subject', nargs = '*', default = None, help = 'Subjects of interest, ie ST-12345')
	parser.add_argument('-sa', '--sample', nargs = '*', default = None, help = 'Samples of interest, ie S-12345')
	parser.add_argument('-a', '--alias', nargs = '*', default = None, help = 'Aliases of interest.  Given the range of possible aliases, unspecified arguments that don\'t fit the otehr parameters will be assumed to be aliases')
	
	a = parser.parse_args()
	a.unspecified.pop(0)

	if a.subject:
		subjects.extend(a.subject)
	if a.sample:
		samples.extend(a.sample)
	if a.alias:
		aliases.extend(a.alias)

	for arg in a.unspecified:
		# Set output file
		if arg.endswith('.txt'):
			output = arg
		# Get subjects
		elif re.match('^ST-\d+', arg):
			subjects.append(arg)
		# Set samples
		elif re.match('^S-\d+', arg):
			samples.append(arg)
		# Get Alias
		else:
			aliases.append(arg)

	if subjects:
		subject_query(subjects)
	if samples:
		sample_query(samples)	
	if len(aliases) > 0:
		alias_query(aliases)

def help():
	print 'Search for information about a particular subject, or search for treasure'
	print 'subject_query(): get information about a specific subject'
	print 'alias_query(): get subjects related to various alias words'
	print 'sample_query(): query various samples for subject information'

def subject_query(*argv):
	if type(argv[0]) == list:
		subjects = argv[0]
	else:
		subjects = argv

	output_formatter.output('Query: %s' % ' '.join(subjects), output, False)
	for sub in subjects:
		try:	
			subject = Subject()
			subject.select(lv, S_SUBJECTID=sub)

			cohort = Cohort()
			cohort.select(lv, SUBJECTID=sub)

			output_formatter.output(sub, output, True)
			for (k,v) in subject.__dict__.items():
				output_formatter.output('%s\t%s' % (k,v), output, True)
			for (k,v) in cohort.__dict__.items():
				output_formatter.output('%s\t%s' % (k, v), output, True)
		except Exception as e:
			output_formatter.output(e, output, True)

def alias_query(*argv):	
	if type(argv[0]) == list:
		aliases = argv[0]
	else:
		aliases = argv

	output_formatter.output('Query: %s' % ' '.join(aliases), output, False)
	for alias in aliases:
		output_formatter.output(alias, output, True)
		output_formatter.output('S_SAMPLEID\tS_SUBJECTID\tS_STUDYID', output, True)

		alias_list = SDIAlias().selectAll(lv, ALIASID=alias)
		n = len(alias_list)

		for a in alias_list:
			sid = a['KEYID1'].strip()
			study = a['KEYID2']

			if sid.startswith('S-'):
				s = Sample()
				s.select(lv, S_SAMPLEID=sid)
				sf = SampleFamily()
				sf.select(lv, S_SAMPLEFAMILYID=s.SAMPLEFAMILYID)
				subj = sf.SUBJECTID
			elif sid.startswith('ST-'):
				subj = sid
			else:
				raise ValueError(sid)
			if not study or study == '(null)':
				try:
					coh = Cohort()
					coh.select(lv, SUBJECTID=subj)
					study = coh.STUDYID
				except:
					study = 'N/A'
			output_formatter.output('%s\t%s\t%s' % (sid, subj, study), output, True)

def sample_query(*argv):
	if type(argv[0]) == list:
		samples = argv[0]
	else:
		samples = argv

	output_formatter.output('Query: %s' % ' '.join(samples), output, False)
	try:
		for samp in samples:
			output_formatter.output(samp, output, True)
			output_formatter.output('S_SAMPLEID\tS_SUBJECTID\tS_STUDYID\tALIASTYPE\tALIASID', output, True)
			sample = Sample()
			sample.select(lv, S_SAMPLEID=samp)

			sf = SampleFamily()
			sf.select(lv, S_SAMPLEFAMILYID=sample.SAMPLEFAMILYID)

			subject = Subject()
			subject.select(lv, S_SUBJECTID=sf.SUBJECTID)

			cohort = Cohort()
			cohort.select(lv, SUBJECTID=subject.S_SUBJECTID)

			aliases = SDIAlias.selectAll(lv, KEYID1=subject.S_SUBJECTID)
			for alias in aliases:
				output_formatter.output('%s\t%s\t%s\t%s' % (subject.S_SUBJECTID, cohort.STUDYID, alias['ALIASTYPE'], alias['ALIASID']), output, True)
	except Exception as e: print e

if __name__ == "__main__":
    main(sys.argv[1:])