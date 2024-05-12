Sakkfeladvány Projekt

Projekt Leírás

A projektünk egy Python nyelven írt interaktív sakkjáték, amely lehetőséget biztosít a felhasználóknak, hogy különböző nehézségi szinteken próbáljanak meg mattot adni egy, kettő vagy három lépésben. A sakk, sakkfeladványok megoldásának általános célja, hogy fejlessze a játékosok stratégiai gondolkodását és sakktudását egy szórakoztató és kihívásokkal teli környezetben.

Technológiai Stack

•	Programozási nyelv: Python 3

•	Könyvtárak: Pygame, Python Chess Library

A Pygame könyvtárat használjuk a grafikus felhasználói felület megvalósítására, míg a Python Chess Library biztosítja a sakk szabályainak érvényesítését.

Főbb Jellemzők

•	Nehézségi szintek választása: A játékosok kiválaszthatják a könnyű, közepes vagy nehéz nehézségi szintet attól függően, hogy milyen kihívást keresnek.

•	Feladványtípusok: A játékosok választhatnak mate-in-1, mate-in-2, vagy mate-in-3 feladványok közül, amelyek különböző komplexitást kínálnak.

•	Interaktív bábuk: A játékosok az egér kattintásokkal mozgathatják a bábukat a sakktáblán, ami intuitív és felhasználóbarát játékélményt biztosít.

Előfeltételek

Győződj meg róla, hogy a Python egyik új verziója telepítve van a számítógépedre. Ezenkívül szükséged lesz a pygame és a chess könyvtárakra, amelyek például a következő parancsokkal telepíthetők:

pip install pygame

pip install chess

Hogyan Játszd

•	Kezdetek: választani kell nehézségi szintet és matt típust is, ennek megfelelően klikkelj a könnyű, közepes vagy nehéz gombok egyikére, majd kattints a mate-in-1, mate-in-2 vagy mate-in-3 gombok egyikére.

•	Oldd meg a feladványt: Mozgasd a bábukat az egérrel. A cél, hogy mattot adj a királynak a megadott lépések számával. Egy lépést úgy tudsz kezelni, hogy kijelölöd kattintással annak a bábunak a mezőjét, amit mozgatni akarsz, majd azt a mezőt is, ahova mozgatni akarod. A program véleményezi minden lépésedet, ennek megfelelően lehet a lépésed jó, rossz vagy érvénytelen is. Vigyázz, mert egymás után 5 rossz lépés vagy 3 érvénytelen lépés után oda a lehetőség. Ha jót léptél, akkor a program instant megjeleníti a program válaszlépését és folytathatod a gondolkodást a következő lépésen.

•	Az elején egy kis idő kell mire betöltődik a pygame, ugyanis a bábuk képeit előbb még le kell töltenie a programnak.

Sok sikert a feladványokhoz!
