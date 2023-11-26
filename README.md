# Analyse af NKKs medlemsundersøgelse (2023)

> Magnus Berg Sletfjerding 2023

## Installation

Dette script kører igennem `make`. For at installere, brug kommandoen

```bash
$ make install
```

Vi antager også at man har `pandoc` installeret for at generere PDFer.

## Opsætning

For at køre scriptet, skal man have fat i datafilerne fra medlemsundersøgelsen.
Disse findes i nkk-forms projektet, hostet af fly.io. Log ind her, hvis det er aktivt, eller aktiver det igennem fly.io
https://nkk-forms.fly.dev/login
Hent dem i admin-panelet, ved at eksportere resultaterne fra undersøgelsen.
Læg dem derefter i mappen `./data`

## At køre scriptet

Scriptet består af flere bestanddele, som kan ses i koden, eller i filen `Makefile`. For at køre hele scriptet, kan man blot bruge kommandoen

```bash
$ make build
```
