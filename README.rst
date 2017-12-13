======
stashq
======
Description of functions:
-------------------------

*snp*
-----
This allows the retrieval of snps by various criteria.  Snps can be searched by either their direct rs numbers, rs numbers from a .bim file, or by querying a specific chromosome and  position.  The package will return a table of rs numbers, chromosome and position, primary allele, and alternative allele(s), and the index they were found in, either in the command line, or in a specified output file.

By default, the most recent vcf index will be searched, but there are options for searching a specific index, or any index.

To see all available vcf file indices, give 'indices' as a parameter.  To specify an index, list the desired .vcf file

*datasets*
----------
This allows the querying of the many Channing datasets. They can be searched by subject ID's, rs numbers, or by dataset keywords, like study name or type of study.  Query output defaults to the command line, but can be written to a .txt file instead.  Keyword queries will search both datasets contained within the Elastic database, as well as datasets in Redmine.

*subject*
---------
This function allows querying of the Sapphire database, by subject, sample or alias.Subject searches return a list of details about the subject.  Sample searches return a table of subjects, studies, and aliases associated with that sample.  Alias searches return a table of samples, subjects, and studies associated with that alias.

If parameters are given without being specified, the program will make automatically assume whether the parameters were intended as subjects, samples, or aliases.
