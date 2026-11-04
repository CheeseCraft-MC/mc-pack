# mc-pack - Hinweis für Claude Code

Dieses Repo ist **nur Hosting + Quelldateien für Resource-Pack-ZIPs**, kein Plugin-Code. Die
eigentlichen Minecraft-Plugins (die diese Packs einbinden) liegen im separaten Repo
[`CheeseCraft-plugin`](https://github.com/CheeseCraft-MC/CheeseCraft-plugin) - dort auch
dessen `CLAUDE.md` lesen, wenn eine Aufgabe beide Repos betrifft (z.B. Pack ändern UND die
`sha1`/URL im Plugin-`config.yml` aktualisieren - beide Schritte gehören zusammen, siehe
[`README.md`](README.md)).

Die ZIP-Dateien im Root liegen bewusst flach, nicht in Unterordnern - ihre URL ist fest in
Plugin-`config.yml`s eingetragen (`raw.githubusercontent.com/CheeseCraft-MC/mc-pack/main/<datei>.zip`)
und darf sich nicht durch eine Umstrukturierung hier ändern, ohne das jeweilige Plugin-Repo
mit anzupassen.

**Historie:** Dieses Repo + `CheeseCraft-plugin` lagen ursprünglich unter dem privaten Account
`emilwernerpfeifer-cmd` (als `mc-pack` bzw. `Mc-server-plugin`) und wurden am 2026-11-04 in die
Organisation `CheeseCraft-MC` transferiert (bei `Mc-server-plugin` zusätzlich umbenannt zu
`CheeseCraft-plugin`, `mc-pack` behielt seinen Namen).
