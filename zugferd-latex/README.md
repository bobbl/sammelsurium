Elektronische ZUGFerd-Rechnung mit Latex erstellen
==================================================

Um ZUGFeRD-Rechnungen mit Latex zu erstellen, wird das Paket `zugfperd`
verwendet, das aber sehr neu ist und zum Beispiel noch nicht in den offiziellen
Paketen von Ubuntu LTS 24.04 (Noble Numbat) enthalten ist.
Außerdem braucht `zugferd` eine relativ neue Version von `pdfmanagement`.

Für die Nutzung der `zugferd` Funktionen mit pdfTeX werden nur folgende
Dateien benötigt:

    zugferd.sty
    pdfmanagement-testphase.sty
    pdfmanagement-testphase.ltx
    3backend-testphase-pdftex.def

die hier von Hand eingefügt wurden. Auch wurden sie leicht angepasst, um auch
mit älteren Latex-Kernels zu funktionieren.

Der Autor von `zugferd` schlägt vor, die immer gleichen Teile einer Rechung in
eine eigenes, persönliches Paket auszulagern. Ich habe hier die mitgelieferte
Beispieldatei `zugerd-invoice.sty` für meine Bedürfnisse angepasst und
`my_rechnung.sty` genannt. Eine Beispielrechnung ist in `bsp_rechnung.tex` zu
finden.

Erst nach dreimaligem Aufruf verschwinden alle Warnungen:

    pdflatex bsp_rechnung.tex
    pdflatex bsp_rechnung.tex
    pdflatex bsp_rechnung.tex

