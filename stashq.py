import sys
import os
import snp
import datasets
import subject
import argparse

def main(argv):
	parser = argparse.ArgumentParser()
	parser.add_argument('datasets', action = 'store_true', help = 'datasets\nLook for datasets on both Channing\'s Elastic database and chanmine, querying RS id, subject, study, or type')
	parser.add_argument('snp', action = 'store_true', help = 'snp\nLook for information about various SNPs, querying RS id, chromosomal location, or .bim file')
	parser.add_argument('subject', action = 'store_true', help = 'subject\nLook for information about various research subjects, querying subject number, study number, or any of various aliases.')

	parsed, args = parser.parse_known_args()

	if args[0] == 'snp':
		snp.main(args[1:])
	elif args[0] == 'datasets':
		datasets.main(argv[1:])
	elif args[0] == 'subject':
		subject.main(argv[1:])

if __name__ == "__main__":
    main(sys.argv[1:])