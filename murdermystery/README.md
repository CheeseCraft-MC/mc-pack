# MurderMystery Resource Pack - Quelldateien

Editierbare Arbeitskopie für `../MurderMystery-ResourcePack.zip`. Was die einzelnen Texturen
genau bewirken und wie das Plugin das Pack einbindet, steht in
[`docs/RESOURCEPACK.md`](https://github.com/CheeseCraft-MC/CheeseCraft-plugin/blob/Main/modules/murdermystery/docs/RESOURCEPACK.md)
im Hauptrepo `CheeseCraft-plugin` - diese Datei hier ist nur die Bau-Anleitung.

## Eigene Texturen ergänzen

PNG-Dateien unter `assets/minecraft/textures/item/` ersetzen (64×64 Pixel, exakt gleicher
Dateiname), dann die ZIP neu bauen:

```bash
cd murdermystery
zip -r -X ../MurderMystery-ResourcePack.zip pack.mcmeta assets
sha1sum ../MurderMystery-ResourcePack.zip
```

Danach beides committen und pushen (die neue ZIP **und** die geänderten Quelldateien hier).
Der neue `sha1`-Wert muss anschließend in `modules/murdermystery/src/main/resources/config.yml`
(im `CheeseCraft-plugin`-Repo, Schlüssel `resourcepack.sha1`) eingetragen werden - sonst lehnen
Minecraft-Clients das Pack als "beschädigt" ab.

Für weitere Skins: neues PNG unter `textures/item/`, neues Modell unter `models/item/` (siehe
bestehende `mm_knife_*.json`/`mm_bow_*.json` als Vorlage), neuer `entries`-Eintrag in der
jeweiligen `items/*.json` - Details dazu ebenfalls in `docs/RESOURCEPACK.md` im Hauptrepo.
