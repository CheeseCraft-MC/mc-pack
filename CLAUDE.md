# mc-pack - Hinweis für Claude Code

Dieses Repo ist **nur Hosting + Quelldateien für Resource-Pack-ZIPs**, kein Plugin-Code. Die
eigentlichen Minecraft-Plugins (die diese Packs einbinden) liegen im separaten Repo
[`Mc-server-plugin`](https://github.com/emilwernerpfeifer-cmd/Mc-server-plugin) - dort auch
dessen `CLAUDE.md` lesen, wenn eine Aufgabe beide Repos betrifft (z.B. Pack ändern UND die
`sha1`/URL im Plugin-`config.yml` aktualisieren - beide Schritte gehören zusammen, siehe
[`README.md`](README.md)).

Die ZIP-Dateien im Root liegen bewusst flach, nicht in Unterordnern - ihre URL ist fest in
Plugin-`config.yml`s eingetragen (`raw.githubusercontent.com/emilwernerpfeifer-cmd/mc-pack/main/<datei>.zip`)
und darf sich nicht durch eine Umstrukturierung hier ändern, ohne das jeweilige Plugin-Repo
mit anzupassen.
