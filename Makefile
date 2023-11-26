.PHONY: install run pdf build clean

install:
	pip install -r requirements.txt

run:
	python analyse_membership_survey.py

md_files := $(wildcard md-files/*.md)
pdf_files := $(patsubst md-files/%.md, pdf-files/%.pdf, $(md_files))

pdf: pdf-files $(pdf_files)

pdf-files:
	mkdir -p pdf-files

pdf-files/%.pdf: md-files/%.md
	pandoc $< --pdf-engine=weasyprint -o $@

clean:
	rm -rf pdf-files/*
	rm -f output/*.md
	rm -f md-files/*
	rm -f figures/*

build: clean run pdf
