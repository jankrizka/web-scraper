import requests
import re
import csv
import sys

"""
scraper.py: Volby-2017 scraper
author: Jan Křižka
email: JanKri610@seznam.cz discord: #jon.void
"""

# Definice regex vzorů pro extrakci dat z HTML
HTML_PATTERNS = {
    "obec_nazev": r'<td class="overflow_name".*?>(.*?)</td>',
    "obec_cislo": r'<a href="ps311\?.*?xobec=(\d+?)&amp;.*?">\d+?</a>',
    "volici_celkem": r'<td class="cislo" headers="sa2"[^>]*>([^<]+)</td>',
    "vydane_obalky": r'<td class="cislo" headers="sa3"[^>]*>([^<]+)</td>',
    "platne_hlasy": r'<td class="cislo" headers="sa6"[^>]*>([^<]+)</td>',
    "strana_vysledek": re.compile(
        r'<td class="cislo" headers="t1sa1 t1sb1">\s*(\d+)\s*</td>\s*'
        r'<td class="overflow_name" headers="t1sa1 t1sb2">([^<]*)</td>\s*'
        r'<td class="cislo" headers="t1sa2 t1sb3">([^<]*)</td>'
    )
}

def stahni_html(url: str) -> str | None:
    """Stáhne HTML obsah z dané URL a vrátí jej jako řetězec."""
    try:
        response = requests.get(url)
        response.raise_for_status()  # Vyvolá chybu pro špatné HTTP odpovědi (4xx nebo 5xx)
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Chyba při stahování URL '{url}': {e}")
        return None

def ziskej_seznam_obci(hlavni_url: str) -> list[dict] | None:
    """
    Získá základní informace o obcích (název, kód, URL detailu) z hlavní stránky.
    Vrátí seznam slovníků, kde každý slovník reprezentuje jednu obec.
    """
    html_obsah = stahni_html(hlavni_url)
    if not html_obsah:
        return None

    nazvy_obci = re.findall(HTML_PATTERNS["obec_nazev"], html_obsah)
    kody_obci = re.findall(HTML_PATTERNS["obec_cislo"], html_obsah)

    if len(nazvy_obci) != len(kody_obci):
        print("Upozornění: Počet názvů a kódů obcí se neshoduje.")
        return None

    # Extrahujeme parametry xkraj a xvyber z hlavní URL pro sestavení detailních URL
    match_kraj = re.search(r"xkraj=(\d+)", hlavni_url)
    match_vyber = re.search(r"xnumnuts=(\d+)", hlavni_url)

    if not match_kraj or not match_vyber:
        print("Chyba: Nelze extrahovat 'xkraj' nebo 'xnumnuts' z hlavní URL.")
        return None

    kraj_param = match_kraj.group(1)
    vyber_param = match_vyber.group(1)

    obce_data = []
    for nazev, kod in zip(nazvy_obci, kody_obci):
        detail_url = (
            f"https://www.volby.cz/pls/ps2017nss/ps311?xjazyk=CZ&xkraj={kraj_param}"
            f"&xobec={kod}&xvyber={vyber_param}"
        )
        obce_data.append({
            "kod": kod,
            "nazev": nazev,
            "url": detail_url,
            "volici_v_seznamu": None,
            "vydane_obalky": None,
            "platne_hlasy": None,
            "hlasy_stran": {}
        })
    return obce_data

def parsuj_obecni_statistiky(html: str) -> dict:
    """
    Parsování souhrnných volebních statistik z HTML stránky obce.
    Vrátí slovník s klíči 'volici_v_seznamu', 'vydane_obalky', 'platne_hlasy'.
    """
    statistiky = {
        'volici_v_seznamu': 0,
        'vydane_obalky': 0,
        'platne_hlasy': 0
    }

    # Pomocná funkce pro bezpečné parsování čísla
    def safe_int_parse(match_obj, key_name):
        if match_obj:
            hodnota_str = match_obj.group(1).replace('&nbsp;', '').strip()
            try:
                return int(hodnota_str)
            except ValueError:
                print(f"Upozornění: Nelze převést '{hodnota_str}' na číslo pro '{key_name}'.")
        return 0

    statistiky['volici_v_seznamu'] = safe_int_parse(
        re.search(HTML_PATTERNS["volici_celkem"], html), 'volici_v_seznamu'
    )
    statistiky['vydane_obalky'] = safe_int_parse(
        re.search(HTML_PATTERNS["vydane_obalky"], html), 'vydane_obalky'
    )
    statistiky['platne_hlasy'] = safe_int_parse(
        re.search(HTML_PATTERNS["platne_hlasy"], html), 'platne_hlasy'
    )

    return statistiky

def parsuj_hlasy_stran(html: str, obec_nazev: str) -> dict:
    """
    Parsování výsledků politických stran z HTML stránky obce.
    Vrátí slovník, kde klíčem je název strany a hodnotou počet hlasů.
    """
    hlasy_stran = {}
    for match in HTML_PATTERNS["strana_vysledek"].finditer(html):
        cislo_strany = match.group(1).strip() # Nepoužito, ale dostupné
        nazev_strany = match.group(2).strip()
        pocet_hlasu_str = match.group(3).replace('&nbsp;', '').strip()
        try:
            hlasy_stran[nazev_strany] = int(pocet_hlasu_str)
        except ValueError:
            print(f"Upozornění: Nelze převést hlasy '{pocet_hlasu_str}' pro stranu '{nazev_strany}' v obci '{obec_nazev}'.")
    return hlasy_stran

def zpracuj_vsechny_obce(seznam_obci: list[dict]) -> list[dict]:
    """
    Projde každou obec, stáhne její detailní data a obohatí slovníky obcí
    o souhrnné statistiky a hlasy pro jednotlivé strany.
    """
    if not seznam_obci:
        print("Žádné obce k zpracování.")
        return []

    processed_obce = []
    for i, obec in enumerate(seznam_obci):
        print(f"Zpracovávám obec {i + 1}/{len(seznam_obci)}: {obec['nazev']} ({obec['kod']})")
        
        html_obsah_detailu = stahni_html(obec['url'])
        if not html_obsah_detailu:
            continue # Pokračujeme další obcí v případě chyby

        # Aktualizace obecních statistik
        statistiky = parsuj_obecni_statistiky(html_obsah_detailu)
        obec.update(statistiky)

        # Aktualizace hlasů stran
        hlasy_stran = parsuj_hlasy_stran(html_obsah_detailu, obec['nazev'])
        obec['hlasy_stran'] = hlasy_stran

        processed_obce.append(obec)
    return processed_obce

def exportuj_do_csv(data_obci: list[dict], nazev_souboru: str):
    """
    Exportuje obohacená data obcí do CSV souboru.
    """
    if not data_obci:
        print("Žádná data k exportu do CSV.")
        return

    # Sběr všech unikátních názvů stran napříč všemi obcemi pro dynamickou hlavičku
    vsechny_nazvy_stran = set()
    for obec in data_obci:
        vsechny_nazvy_stran.update(obec.get('hlasy_stran', {}).keys())
    serazene_nazvy_stran = sorted(list(vsechny_nazvy_stran))

    hlavicka = [
        'Kód obce', 'Název obce', 'Voliči v seznamu', 'Vydané obálky', 'Platné hlasy'
    ] + serazene_nazvy_stran

    try:
        with open(nazev_souboru, mode='w', newline='', encoding='utf-8') as soubor_csv:
            writer = csv.writer(soubor_csv)
            writer.writerow(hlavicka)

            for obec in data_obci:
                radek = [
                    obec.get('kod', ''),
                    obec.get('nazev', ''),
                    obec.get('volici_v_seznamu', 0),
                    obec.get('vydane_obalky', 0),
                    obec.get('platne_hlasy', 0)
                ]
                # Přidáme hlasy pro každou stranu, 0 pokud strana v obci neměla hlasy
                for strana_nazev in serazene_nazvy_stran:
                    radek.append(obec['hlasy_stran'].get(strana_nazev, 0))
                writer.writerow(radek)
        print(f"Data byla úspěšně uložena do '{nazev_souboru}'.")
    except IOError as e:
        print(f"Chyba při zápisu do souboru '{nazev_souboru}': {e}")

def main():
    if len(sys.argv) != 3:
        print("Použití: python skript.py <URL_HLAVNI_STRANKY> <NAZEV_CSV_SOUBORU>")
        print("Příklad: python scraper.py \"https://www.volby.cz/pls/ps2017nss/ps32?xjazyk=CZ&xkraj=12&xnumnuts=7103\" vysledky_prostejov.csv")
        sys.exit(1)

    url_vstup = sys.argv[1]
    csv_vystup = sys.argv[2]

    print(f"Spouštím zpracování pro URL: {url_vstup}")
    print(f"Výsledky budou uloženy do: {csv_vystup}")

    # Krok 1: Získání základních informací o obcích
    seznam_obci = ziskej_seznam_obci(url_vstup)

    if seznam_obci:
        # Krok 2: Zpracování detailů pro každou obec
        kompletni_data_obci = zpracuj_vsechny_obce(seznam_obci)

        # Krok 3: Export dat do CSV
        exportuj_do_csv(kompletni_data_obci, csv_vystup)
    else:
        print("Nepodařilo se získat základní informace o obcích.")

if __name__ == '__main__':
    main()
