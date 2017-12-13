def output(text, output, append):
	if output and append:
		f = open(output, 'a')
		f.write('%s\n' % text)
		f.close()
	elif output:
		f = open(output, 'w+')
		f.write('%s\n' % text)
		f.close()
	else:
		print text