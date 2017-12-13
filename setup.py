from setuptools import setup, find_packages

setup(	name='stashq',
		version='1.0',
		description='Access Channing datasets',
		url='https://changit.bwh.harvard.edu/renwo/stashq',
		author='Nicholas Wolfe',
		author_email='renwo@channing.harvard.edu',
		install_requires=['AIMS.SAPPHIRE', 'AIMS.Generations', 'stashq_elastic', 'output_format', 'elasticsearch', 're', 'numpy', 'json', 'pyactiveresource']
		include_package_data=True,
		zip_safe=False
	)