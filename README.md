# ČSFD Novinky - Home Assistant Integration

Custom integrace a karta pro Home Assistant, která zobrazuje aktuální novinky z ČSFD.cz (Československá filmová databáze).

## Funkce

- Automatické načítání 15 nejnovějších zpráv z ČSFD.cz/novinky
- Zobrazení náhledů včetně obrázků, nadpisů, dat a perexů
- Aktualizace každých 30 minut
- Moderní a responzivní karta pro Lovelace UI
- Kliknutím na novinku se otevře celý článek na ČSFD.cz

## Instalace

### 1. Instalace Custom Integration

#### Ruční instalace:

1. Zkopírujte složku `custom_components/csfd_news` do vašeho Home Assistant konfiguračního adresáře:
   ```
   <config>/custom_components/csfd_news/
   ```

2. Restartujte Home Assistant

3. Přidejte do souboru `configuration.yaml`:
   ```yaml
   csfd_news:
   ```

4. Znovu restartujte Home Assistant

#### HACS instalace (pokud máte HACS):

1. Otevřete HACS v Home Assistantu
2. Přejděte do "Integrations"
3. Klikněte na tři tečky v pravém horním rohu
4. Vyberte "Custom repositories"
5. Přidejte URL tohoto repozitáře a vyberte kategorii "Integration"
6. Klikněte na "Install"
7. Restartujte Home Assistant

### 2. Instalace Lovelace Karty

#### Ruční instalace:

1. Zkopírujte složku `www/csfd-news-card` do vašeho Home Assistant konfiguračního adresáře:
   ```
   <config>/www/csfd-news-card/
   ```

2. Přidejte kartu jako zdroj v Lovelace:
   - Přejděte do nastavení Lovelace
   - Klikněte na tři tečky v pravém horním rohu
   - Vyberte "Resources"
   - Klikněte "Add Resource"
   - URL: `/local/csfd-news-card/csfd-news-card.js`
   - Resource type: `JavaScript Module`

3. Restartujte Home Assistant (nebo jen obnovte cache prohlížeče)

#### HACS instalace:

1. Otevřete HACS v Home Assistantu
2. Přejděte do "Frontend"
3. Klikněte na tři tečky v pravém horním rohu
4. Vyberte "Custom repositories"
5. Přidejte URL tohoto repozitáře a vyberte kategorii "Lovelace"
6. Klikněte na "Install"
7. Restartujte Home Assistant

## Použití

### Přidání karty do Lovelace dashboardu:

1. Otevřete váš dashboard v režimu editace
2. Klikněte na "Add Card"
3. Najděte "CSFD News Card" v seznamu karet
4. Nebo použijte manuální konfiguraci:

```yaml
type: custom:csfd-news-card
entity: sensor.csfd_news
```

### Příklad automatizace:

```yaml
automation:
  - alias: "Upozornění na novou ČSFD novinku"
    trigger:
      - platform: state
        entity_id: sensor.csfd_news
    condition:
      - condition: template
        value_template: "{{ trigger.to_state.state | int > trigger.from_state.state | int }}"
    action:
      - service: notify.mobile_app
        data:
          title: "Nová novinka na ČSFD!"
          message: "{{ state_attr('sensor.csfd_news', 'news')[0].title }}"
```

## Konfigurace

### Sensor

Po instalaci je dostupný sensor `sensor.csfd_news` s následujícími atributy:

- `count`: Počet načtených novinek
- `news`: Seznam novinek, každá obsahuje:
  - `title`: Název novinky
  - `link`: Odkaz na celý článek
  - `image`: URL náhledového obrázku
  - `date`: Datum publikace
  - `perex`: Krátký perex článku

### Přizpůsobení

V souboru `custom_components/csfd_news/const.py` můžete upravit:

- `SCAN_INTERVAL_MINUTES`: Interval aktualizace (výchozí 30 minut)
- `MAX_NEWS_ITEMS`: Maximální počet novinek (výchozí 15)

## Poznámky

- Integrace vyžaduje internetové připojení
- Data jsou načítána z veřejně dostupné stránky ČSFD.cz
- Pokud se struktura ČSFD stránky změní, může být potřeba aktualizovat parsing logiku

## Licence

Tento projekt je poskytován "tak jak je" pro osobní použití.

## Podpora

Pokud narazíte na problém, otevřete issue v repozitáři projektu.
