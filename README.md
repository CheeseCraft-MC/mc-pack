# mc-pack

Öffentliches Hosting-Repo für Resource-Pack-ZIPs von Emils Minecraft-Plugins - Minecraft-
Clients laden sie direkt über `raw.githubusercontent.com` herunter (eine einzige HTTP-Antwort
ohne Weiterleitungskette, anders als z.B. Dropbox-Freigabelinks). Die ZIP-Dateien liegen dafür
bewusst flach im Repo-Root, da ihre URL fest in den Plugin-`config.yml`s eingetragen ist und
sich bei einer Pfadänderung nicht von selbst mitändert.

| Datei/Ordner | Gehört zu |
|---|---|
| `MurderMystery-ResourcePack.zip` | [`CheeseCraft-plugin/modules/murdermystery`](https://github.com/CheeseCraft-MC/CheeseCraft-plugin/tree/Main/modules/murdermystery) - fest verlinkt in dessen `config.yml` |
| `murdermystery/` | Editierbare Quelldateien (PNGs, Modelle, `pack.mcmeta`) für die ZIP oben - siehe `murdermystery/README.md` |
| `PvPCore-ResourcePack.zip` | [`CheeseCraft-plugin/modules/pvpcore`](https://github.com/CheeseCraft-MC/CheeseCraft-plugin/tree/Main/modules/pvpcore) - fest verlinkt in dessen `config.yml`, siehe dort `docs/RESOURCEPACK.md` |
| `pvpcore/` | Editierbare Quelldateien (PNGs, Font-Icons, `pack.mcmeta`) für die ZIP oben - siehe `pvpcore/README.md` |

Beide Plugin-Module haben **keinen** eigenen `resourcepack/`-Ordner in `CheeseCraft-plugin` -
Quelle und ZIP leben ausschließlich hier.

## Neue ZIP hochladen

Einfach die neue Datei am selben Pfad committen und pushen - `git push` überschreibt die Datei,
die URL bleibt stabil, kein neuer Link nötig (anders als z.B. bei Dropbox-Freigabelinks).
