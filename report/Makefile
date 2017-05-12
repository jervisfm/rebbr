DOC=main

all:
	make clean
	pdflatex $(DOC).tex
	bibtex $(DOC)
	pdflatex $(DOC).tex
	pdflatex $(DOC).tex

clean:
	rm -f $(DOC).blg $(DOC).bbl $(DOC).aux $(DOC).log $(DOC).pdf $(DOC).fdb_latexmk $(DOC).fls $(DOC).lof $(DOC).lot $(DOC).toc $(DOC).out *~ tex/*~

check:
	pdflatex $(DOC).tex | grep -e "undefined" -e "multiply"

osx:
	pdflatex $(DOC).tex
	open $(DOC).pdf
