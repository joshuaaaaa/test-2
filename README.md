# ČSFD Novinky - Home Assistant Integration

Custom integrace a karta pro Home Assistant, která zobrazuje aktuální novinky z ČSFD.cz (Československá filmová databáze).

## Funkce

- Automatické načítání 15 nejnovějších zpráv z ČSFD.cz/novinky
- Zobrazení náhledů včetně obrázků, nadpisů, dat a perexů
- Aktualizace každých 30 minut
- Moderní a responzivní karta pro Lovelace UI
- Kliknutím na novinku se otevře celý článek na ČSFD.cz

## Instalace

### HACS instalace (doporučeno):

1. Otevřete HACS v Home Assistantu
2. Přejděte do sekce **"Integrations"**
3. Klikněte na tři tečky v pravém horním rohu
4. Vyberte **"Custom repositories"**
5. Přidejte URL tohoto repozitáře a vyberte kategorii **"Integration"**
6. Klikněte na **"Install"**
7. **DŮLEŽITÉ: Restartujte Home Assistant** (Nastavení → Systém → Restartovat)

### Přidání integrace do Home Assistant:

⚠️ **DŮLEŽITÉ:** Po instalaci přes HACS a restartu počkejte cca 1-2 minuty, než se integrace načte!

1. Přejděte do **Nastavení** → **Zařízení a služby**
2. Klikněte na **"+ Přidat integraci"** v pravém dolním rohu
3. Vyhledejte **"CSFD News"** (pokud ji nevidíte, zkuste obnovit stránku Ctrl+F5)
4. Klikněte na integraci a potvrďte přidání

✅ **Hotovo!** Integrace je nakonfigurována a sensor `sensor.csfd_news` je dostupný. Lovelace karta je automaticky zaregistrována.

### Ruční instalace:

1. Zkopírujte složku `custom_components/csfd_news` do vašeho Home Assistant konfiguračního adresáře:
   ```
   <config>/custom_components/csfd_news/
   ```

2. Restartujte Home Assistant

3. Přejděte do **Nastavení** → **Zařízení a služby** → **"+ Přidat integraci"** a vyhledejte **"CSFD News"**

## Použití

### Přidání karty do Lovelace dashboardu:

Karta se automaticky zaregistruje při startu Home Assistant. Pro její použití:

1. Otevřete váš dashboard v režimu editace
2. Klikněte na "Add Card"
3. Najděte "CSFD News Card" v seznamu karet (nebo vyhledejte "CSFD")
4. Nebo použijte manuální konfiguraci:

```yaml
type: custom:csfd-news-card
entity: sensor.csfd_news
```

**Pokud karta není viditelná v seznamu karet:**
- Zkuste vymazat cache prohlížeče (Ctrl+F5)
- Nebo ručně přidejte zdroj v Lovelace Resources:
  - URL: `/csfd_news/csfd-news-card.js`
  - Resource type: `JavaScript Module`

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
- **NENÍ potřeba** editovat `configuration.yaml` - integrace se přidává přes UI (Nastavení → Zařízení a služby)

## Licence

Tento projekt je poskytován "tak jak je" pro osobní použití.

## Podpora

Pokud narazíte na problém, otevřete issue v repozitáři projektu.
