# Volební Scraper – Volby.cz

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






