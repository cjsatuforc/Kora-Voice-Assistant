TARGET=main
TEX=latex
default: pdf

clean: clean-doc
# Documentation

pdf: ps
	ps2pdf $(TARGET).ps

ps: dvi
	dvips $(TARGET).dvi

dvi: $(TARGET).tex
	$(TEX) $(TARGET).tex
	#Comment out if bibliography is included: bibtex $(TARGET)
	$(TEX) $(TARGET).tex
	$(TEX) $(TARGET).tex

clean-doc:
	rm -f $(TARGET).aux
	rm -f $(TARGET).dvi
	rm -f $(TARGET).log
	rm -f $(TARGET).out
	rm -f $(TARGET).ps
	rm -f $(TARGET).toc
	rm -f $(TARGET).bbl
	rm -f $(TARGET).blg
	rm -f pygments.tex.aux
	rm -f $(TARGET).pdf

all: pdf prog

.PHONY: all
