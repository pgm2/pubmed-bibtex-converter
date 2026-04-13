Install pymed and biopython, with pip install pymed and pip install biopython. If pip is not available, install that as well.
Then change input and output file paths to match your files in pubmed2.py. You can use pwd in Linux to check current path.
The pubmed2.py takes a single commandline argument as inputfile, if none is given it uses default names and paths (for Android).

For Raspberry Pi 5 you can do the following:

python -m venv my_project

source my_project/bin/activate

pip install biopython

pip install pymed

pip install pylatexenc
