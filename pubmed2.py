#author: pmajorin 
#makes bibtex entries from a list of pubmed article pmids, uses pmc article link, if available
#fixed the problem with sometimes wrong publication date, uses now biopython instead of pymed to get publication date
#same with title, uses now biopython for titles
#added unicode to latex translation of author names
#uses now regex special rules for title conversion to latex format
#todo: add changable author numbers instead of just first author

#input list file format is
#%comment
#12345678
#23415251
#....

from pymed import PubMed
pubmed = PubMed()
from Bio import Entrez
from Bio import Medline
from pylatexenc.latexencode import unicode_to_latex
from pylatexenc.latexencode import UnicodeToLatexEncoder, UnicodeToLatexConversionRule, RULE_REGEX
import re
import os
import sys

Entrez.email = "your_email2@example.com"  # Required by NCBI

def test():
    if (len(sys.argv) == 2):
    	input_file = os.getcwd()+'/'+sys.argv[1]
    	output_file = open(os.getcwd()+'/bibtex.txt', "w")
    elif (len(sys.argv) == 1):
    	input_file = '/storage/emulated/0/Download/python/pmids'
    	output_file = open('/storage/emulated/0/Download/python/bibtex.txt',"w")
    else:
    	sys.exit("Give only a single argument as inputfilename.")
    pmids = []
    with open(input_file, 'r') as file:
        for line in file:
            line = line.lstrip()
            if line.startswith("%"):
            	continue
            # Split the line into columns (split by whitespace)
            columns = line.strip().split()
            # Extend the data list with the columns of the current line
            pmids.extend(columns)
    
    for pmid in pmids:
    	if pmid.startswith("%"):
    		continue
    	pmid = pmid.strip()
    	results = pubmed.query(f"{pmid}[PMID]", max_results=1)
    	article = next(results, None)
    	if article:
    	   print(f"PMID: {pmid}")
    	   title = fetch_title(pmid)
    	   title = special_convert(title)
    	   print(f"Title: {title}")
    	   raw_id = str(article.pubmed_id)
    	   clean_pmid = raw_id.split()[0]  # Takes first entry if multiple exist
    	   
    	   first_author = article.authors[0]  # Get first author dict
    	   first_author_name = f"{first_author.get('firstname', '')} {first_author.get('lastname', '')}".strip()
    	   #translate to latex syntax
    	   first_author_name = unicode_to_latex(first_author_name)
    	   print(f"First Author: {first_author_name}")
    	   
    	   url = get_pmc_from_pubmed_xml(clean_pmid)
    	   print(f"URL: {url}")
    	   # Extract year 
    	   handle = Entrez.esummary(db="pubmed", id=clean_pmid)
    	   record = Entrez.read(handle)
    	   handle.close()
    	   year=record[0]["PubDate"].split()[0]
    	   print(f"Publication year: {year}")
    
    	   # get ISO abbreviation for journal name
    	   abbrev = get_journal_abbreviation(clean_pmid)  # Replace with your PMID
    	   print(f"ISO Abbreviation: {abbrev}")  # e.g., "Nat. Biotechnol."
    	   #make a bibtex entry
    	   bibtex_entry(output_file,first_author_name, url, title, abbrev, year)
    	   print("")
    	else:
    		print(f"\nError: PMID {pmid} not found.\n")
    		
def get_pmc_from_pubmed_xml(pmid):
    try:
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        record = Entrez.read(handle)
        
        if "PubmedArticle" in record:
            article = record["PubmedArticle"][0]
            if "ArticleIdList" in article["PubmedData"]:
                for id_type in article["PubmedData"]["ArticleIdList"]:
                    if id_type.attributes["IdType"] == "pmc":
                        return f"https://www.ncbi.nlm.nih.gov/pmc/articles/{str(id_type)}/"
    except Exception as e:
        print(f"Error fetching PMCID for PMID {pmid}: {e}")
    return f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"
    
# Example:
def get_pmc(pmid):
        try:
        	handle = Entrez.elink(dbfrom="pubmed", db="pmc", id=pmid)
        	record = Entrez.read(handle)
        	if record and "LinkSetDb" in record[0] and record[0]["LinkSetDb"]:
        	   	pmcid = record[0]["LinkSetDb"][0]["Link"][0]["Id"]
        	   	return f"https://www.ncbi.nlm.nih.gov/pmc/articles/PMC{pmcid}/"
        except Exception as e:
        	print(f"Error fetching PMCID for PMID {pmid}: {str(e)}")
        return  f"https://pubmed.ncbi.nlm.nih.gov/{pmid}"
    

def get_journal_abbreviation(pmid):
    
    try:
        # Step 1: Fetch record in Medline format (more reliable than XML)
        handle = Entrez.efetch(db="pubmed", id=pmid, rettype="medline", retmode="text")
        record = Medline.read(handle)
        
        # Step 2: Check all possible journal name fields
        journal_fields = ['TA', 'JT', 'SO']
        for field in journal_fields:
            if field in record:
                return record[field]
        
        # Step 3: Ultimate fallback
        return record.get('SO', 'Journal name unavailable')
    
    except Exception as e:
        print(f"Error processing PMID {pmid}: {str(e)}")
        return "Journal name unavailable"

def fetch_title(pmid):
    """Fetch article title for a given PMID."""
    try:
        # Fetch XML data for the PMID
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        record = Entrez.read(handle)
        
        # Extract title from the nested XML structure
        if "PubmedArticle" in record:
            article = record["PubmedArticle"][0]
            title = article["MedlineCitation"]["Article"]["ArticleTitle"]
            return title
    except Exception as e:
        print(f"Error fetching title for PMID {pmid}: {e}")
    return None
 
 #this converts strings to LaTex format, there might be special rules which are needed e.g. <i>text</i> -> \textit{text}
def special_convert(string):
	u = UnicodeToLatexEncoder(
	conversion_rules=[
	UnicodeToLatexConversionRule(rule_type=RULE_REGEX, rule=[
	(re.compile(r'<i>'), r'\\textit{'),
	(re.compile(r'</i>'), r'}'),
	]),
	'defaults'
	])
	return u.unicode_to_latex(string)
	
#@Article{hallmarks_aging,
# Author         = "Carlos Lopez-Otin and others",
# Title          = "\href{https://pubmed.ncbi.nlm.nih.gov/36599349/}{Hallmarks of aging: An expanding universe}",
# Journal        = "Cell Metabolism",
# Year           = 2023,
#}
def bibtex_entry(text_file, author, url, title, journal, year):
		print(f"@Article {{key,",file=text_file)
		print(f"Author = \"{author} and others\",",file=text_file)
		print(f"Title = \"\\href{{{url}}}{{{title}}}\",",file=text_file)
		print(f"Journal = \"{journal}.\",",file=text_file)
		print(f"Year = {year},\n}}\n",file=text_file)
		return

test()
