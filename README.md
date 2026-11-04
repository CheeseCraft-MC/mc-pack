# mc-pack

Öffentliches Hosting-Repo für Resource-Pack-ZIPs von Emils Minecraft-Plugins - Minecraft-
Clients laden sie direkt über `raw.githubusercontent.com` herunter (eine einzige HTTP-Antwort
ohne Weiterleitungskette, anders als z.B. Dropbox-Freigabelinks). Die ZIP-Dateien liegen dafür
bewusst flach im Repo-Root, da ihre URL fest in den Plugin-`config.yml`s eingetragen ist und
sich bei einer Pfadänderung nicht von selbst mitändert.

| Datei/Ordner | Gehört zu |
|---|---|
| `MurderMystery-ResourcePack.zip` | [`Mc-server-plugin/modules/murdermystery`](https://github.com/emilwernerpfeifer-cmd/Mc-server-plugin/tree/Main/modules/murdermystery) - fest verlinkt in dessen `config.yml` |
| `murdermystery/` | Editierbare Quelldateien (PNGs, Modelle, `pack.mcmeta`) für die ZIP oben - siehe `murdermystery/README.md` |
| `PvPCore-ResourcePack.zip` | Gehört zu keinem Plugin in `Mc-server-plugin` - nicht anfassen, ohne den Kontext zu kennen |

## Neue ZIP hochladen

Einfach die neue Datei am selben Pfad committen und pushen - `git push` überschreibt die Datei,
die URL bleibt stabil, kein neuer Link nötig (anders als z.B. bei Dropbox-Freigabelinks).
