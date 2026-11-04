# UltimateRPG Resource Pack - Quelldateien

Editierbare Arbeitskopie für `../UltimateRPG-ResourcePack.zip`. Anders als bei MurderMystery/
PvPCore ist hier praktisch nichts von Hand gemalt: `assets/` ist die **generierte Ausgabe** von
`tools/` (Python + Pillow) - Icons, Waffen-/Schild-3D-Modelle, Mob-Texturen, Menü-Hintergründe
usw. werden aus Code erzeugt, nicht als fertige PNGs gepflegt.

Was die einzelnen Assets genau bewirken und wie das Plugin das Pack einbindet, steht in
[`docs/RESOURCEPACK.md`](https://github.com/CheeseCraft-MC/CheeseCraft-plugin/blob/Main/modules/ultimaterpg/docs/RESOURCEPACK.md)
im Hauptrepo `CheeseCraft-plugin` - diese Datei hier ist nur die Bau-Anleitung.

## Wichtig: der Generator braucht das Plugin-Repo

`tools/generate.py` liest beim Bauen auch `items.yml`, `skills.yml`, `regions.yml` und
`config.yml` aus `CheeseCraft-plugin/modules/ultimaterpg/src/main/resources/` - welche Items/
Skills es gibt, kommt aus dem Plugin selbst, nicht nur aus diesem Repo. Zum Neubauen also
**beide Repos** nebeneinander ausgecheckt haben:

```
CheeseCraft-plugin/modules/ultimaterpg/   <- Plugin-Quellcode, liefert die YAMLs
mc-pack/ultimaterpg/                       <- dieses Verzeichnis
```

## Pack neu bauen

```bash
cd mc-pack/ultimaterpg/tools
python3 generate.py --plugin-resources ../../../CheeseCraft-plugin/modules/ultimaterpg/src/main/resources --out ..
cd ..
python3 tools/validate.py
zip -r -X ../UltimateRPG-ResourcePack.zip pack.mcmeta assets
sha1sum ../UltimateRPG-ResourcePack.zip
```

(Die genauen Flags von `generate.py`/`validate.py` siehe deren eigene `--help` bzw.
Kommentare am Dateianfang - das Skript wurde aus dem Plugin-Repo hierher verschoben, die
Pfad-Konstanten am Dateianfang ggf. prüfen/anpassen.)

Danach beides committen und pushen (die neue ZIP **und** die geänderten Quelldateien hier).
Der neue `sha1`-Wert muss anschließend in
`modules/ultimaterpg/src/main/resources/config.yml` (im `CheeseCraft-plugin`-Repo, Schlüssel
`resource_pack.hosting.sha1`) eingetragen werden - sonst lehnen Minecraft-Clients das Pack als
"beschädigt" ab.
