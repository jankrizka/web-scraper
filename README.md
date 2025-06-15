# 📊 Volební Scraper – Volby.cz

Tento skript slouží ke **stažení a zpracování výsledků voleb** v jednotlivých obcích z webu [volby.cz](https://www.volby.cz/) a k jejich exportu do CSV souboru.

## Co skript dělá

1. **Stáhne HTML stránku** s výpisem obcí pro zadaný region.
2. **Získá kódy a názvy obcí** a zkonstruuje odkazy na detailní stránky jednotlivých obcí.
3. **Stáhne každou detailní stránku** obce a z ní získá:
   - Počet voličů v seznamu
   - Počet vydaných obálek
   - Počet platných hlasů
   - Počty hlasů pro jednotlivé politické strany
4. **Výsledná data exportuje do CSV**, kde každý řádek představuje jednu obec.

---

## Spuštění

### Požadavky
- Python 3.10+
- Knihovny: `requests`

```bash
pip install requests
```

### Použití

```bash
python scraper.py <URL_HLAVNÍ_STRÁNKY> <NÁZEV_CSV_SOUBORU>
```

#### Příklad:

```bash
python scraper.py "https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103" vysledky_prostejov.csv
```

---

## Výstup

CSV soubor obsahuje:

- Kód obce
- Název obce
- Počet voličů v seznamu
- Počet vydaných obálek
- Počet platných hlasů
- Hlasové zisky jednotlivých stran (každá strana ve vlastním sloupci)

---

## Struktura kódu

- `stahni_html(url)` – stáhne HTML obsah z URL
- `ziskej_seznam_obci(url)` – získá seznam obcí a jejich URL na detaily
- `parsuj_obecni_statistiky(html)` – extrahuje souhrnné statistiky obce
- `parsuj_hlasy_stran(html, nazev_obce)` – extrahuje výsledky stran pro danou obec
- `zpracuj_vsechny_obce(obce)` – stáhne a zpracuje všechny detailní stránky
- `exportuj_do_csv(data, nazev_souboru)` – uloží výsledky do CSV

---

## Poznámky

- HTML stránky jsou parsovány pomocí **regulárních výrazů**, což je náchylné na změny v HTML struktuře.
- Pokud se změní formát stránek volby.cz, bude potřeba upravit regex vzory v `HTML_PATTERNS`.
- Pro robustnější řešení doporučujeme knihovny jako `BeautifulSoup`.

---

## Kontakt

Máte-li dotazy nebo nahlásíte chybu, neváhejte mě kontaktovat nebo vytvořit issue.
