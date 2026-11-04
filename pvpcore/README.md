# PvPCore Resource Pack - Quelldateien

Editierbare Arbeitskopie für `../PvPCore-ResourcePack.zip`. Was die einzelnen Texturen genau
bewirken und wie das Plugin das Pack einbindet, steht in
[`docs/RESOURCEPACK.md`](https://github.com/CheeseCraft-MC/CheeseCraft-plugin/blob/Main/modules/pvpcore/docs/RESOURCEPACK.md)
im Hauptrepo `CheeseCraft-plugin` - diese Datei hier ist nur die Bau-Anleitung.

## Eigene Grafiken ergänzen

PNGs unter `assets/pvpcore/textures/font/` (Logo/Linie) oder `assets/minecraft/textures/gui/`
(Knöpfe, Menü-Hintergründe, Kisten-Menü) ersetzen (gleicher Dateiname, gleiche Maße), dann die
ZIP neu bauen:

```bash
cd pvpcore
zip -r -X ../PvPCore-ResourcePack.zip pack.mcmeta pack.png assets
sha1sum ../PvPCore-ResourcePack.zip
```

Danach beides committen und pushen (die neue ZIP **und** die geänderten Quelldateien hier).
Der neue `sha1`-Wert muss anschließend in
`modules/pvpcore/src/main/resources/config.yml` (im `CheeseCraft-plugin`-Repo, Schlüssel
`ressourcenpaket.sha1`) **und** in `ServerLook.DEFAULT_SHA1` eingetragen werden - sonst lehnen
Minecraft-Clients das Pack als "beschädigt" ab.
