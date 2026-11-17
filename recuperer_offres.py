"""Récupère les offres Coupon Network et les enregistre dans offres.js, à côté de l'app.

L'app (index.html) charge offres.js à l'ouverture et met son catalogue à jour toute seule.
Les offres changent le mercredi : une récupération par semaine suffit.
Si le dossier est le dépôt git de l'app en ligne, offres.js est aussi envoyé sur GitHub
(la version en ligne, ouverte sur la tablette, est alors à jour).

Usage : double-clic sur « Recuperer les offres.bat », ou  python recuperer_offres.py [--silencieux]
"""
import json
import os
import shutil
import subprocess
import sys
import urllib.request
from datetime import datetime
from pathlib import Path

URL = "https://www.couponnetwork.fr/api/offer/offersList?retailerId=15&skipMember=true"
DOSSIER = Path(__file__).resolve().parent
SORTIE = DOSSIER / "offres.js"
JOURNAL = DOSSIER / "recuperer_offres.log"


def journal(msg):
    ligne = f"{datetime.now():%Y-%m-%d %H:%M}  {msg}"
    print(msg)
    with JOURNAL.open("a", encoding="utf-8") as f:
        f.write(ligne + "\n")


def git(*args):
    exe = shutil.which("git") or r"C:\Program Files\Git\cmd\git.exe"
    return subprocess.run([exe, *args], cwd=DOSSIER, capture_output=True, text=True, timeout=120,
                          creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))


def en_ligne():
    # Pas sur GitHub Actions (la tâche du dépôt publie elle-même) et seulement dans le dépôt de l'app
    return not os.environ.get("GITHUB_ACTIONS") and (DOSSIER / ".git").exists()


def publier():
    """Envoie offres.js sur GitHub, ce qui met à jour l'app en ligne."""
    git("add", "offres.js")
    if git("diff", "--cached", "--quiet", "--", "offres.js").returncode == 0:
        return journal("En ligne : offres déjà à jour")
    c = git("commit", "-m", f"Offres Coupon Network du {datetime.now():%d/%m/%Y}", "--", "offres.js")
    p = git("push")
    if c.returncode or p.returncode:
        raise RuntimeError("envoi sur GitHub impossible : " + (p.stderr or c.stderr).strip()[-300:])
    journal("En ligne : offres envoyées sur GitHub")


def main():
    if en_ligne():
        # Récupère d'abord les éventuelles mises à jour en ligne, pour pouvoir envoyer ensuite sans conflit
        r = git("pull", "--rebase", "--autostash", "-q")
        if r.returncode:
            journal("Attention : mise à jour depuis GitHub impossible : " + r.stderr.strip()[-200:])

    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        data = json.load(r)

    items = data.get("offers", {}).get("items")
    if not isinstance(items, list) or not items:
        raise ValueError("réponse inattendue (pas de liste d'offres)")

    # On ne garde que la liste des offres : c'est tout ce dont l'app a besoin
    contenu = {"fetchedAt": datetime.now().astimezone().isoformat(timespec="seconds"), "offers": {"items": items}}
    tmp = SORTIE.with_suffix(".tmp")
    tmp.write_text("window.CN_OFFERS = " + json.dumps(contenu, ensure_ascii=False) + ";\n", encoding="utf-8")
    tmp.replace(SORTIE)
    journal(f"OK : {len(items)} offres enregistrées dans {SORTIE.name}")
    if en_ligne():
        publier()


if __name__ == "__main__":
    silencieux = "--silencieux" in sys.argv
    try:
        main()
    except Exception as e:
        journal(f"ERREUR : {e}")
        if not silencieux:
            input("Appuie sur Entrée pour fermer…")
        sys.exit(1)
    if not silencieux:
        input("Terminé. Rouvre ou recharge l'app (F5). Appuie sur Entrée pour fermer…")
