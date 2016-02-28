# Innskráning með Íslykli notandi Python og Flask
Dæmi um Flask forrit sem notast við Íslykil frá Þjóðskrá. Sjá https://www.island.is/innskraningarthjonusta.

Innskráning byggir á upplýsingum frá https://www.island.is/media/pdf-skjol-a-island.is-2014/Innskraning-Island-is---leidbeiningar-utg-2-0.pdf.

## Keyrsla

Ég mæli með því að setja upp Virtualenv fyrir Python.

```sh
pip install virtualenv
virtualenv /slóð/á/virtualenv/island
source /slóð/á/virtualenv/island/bin/activate

# SignXML þarf ákveðna hluti setta upp í stýrikerfi. Sjá https://signxml.readthedocs.org/en/latest/.
pip install -r requirements.txt

python server.py
```

## Uppsetning

Í skránni `app/config.py` má sjá fjórar stillingar

**ISLAND_SITE_ID** - Lénið sem þú sóttir um þjónustuna með. T.d. skra.is

**ISLAND_VALIDATE_IP** - Segir til um hvort sannreyna eigi IP tölu milli ísland.is og síðunnar þinnar.

**ISLAND_VALIDATE_UA** - Segir til um hvort sannreyna eigi vafrastreng milli ísland.is og síðunnar þinnar.

**ISLAND_REQUIRED_AUTHENTICATION** - Segir til um hvaða auðkenningarleiðir má nota til að skrá sig inn á síðuna. Nánari upplýsingar í skránni sjálfri.
