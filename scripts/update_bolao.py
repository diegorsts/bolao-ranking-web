# -*- coding: utf-8 -*-
import json
import os
import sys
import traceback
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore
from playwright.sync_api import sync_playwright

URL = "https://www.bolaoesportivo.com.br/PalpiteRanking.aspx?idBolao=MzQwNw==&ydUsua=VFZSQk0wOUVVVDA9"


def log(msg):
    print(f"[{datetime.now(timezone.utc).isoformat(timespec='seconds')}] {msg}")


def init_firestore():
    raw = os.environ["FIREBASE_SERVICE_ACCOUNT"]
    cred = credentials.Certificate(json.loads(raw))
    firebase_admin.initialize_app(cred)
    return firestore.client()


def scrape_current():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_selector('[id*=rptRanking_lkNome]', timeout=15000)
        rows = page.evaluate(
            """() => {
                const names = document.querySelectorAll('[id*=rptRanking_lkNome]');
                const pts = document.querySelectorAll('[id*=rptRanking_lblRkPonto]');
                const out = [];
                for (let i=0;i<names.length;i++) out.push([names[i].innerText.trim(), pts[i]?pts[i].innerText.trim():null]);
                return out;
            }"""
        )
        browser.close()
    return {name: int(pts) for name, pts in rows if pts is not None}


def main():
    db = init_firestore()
    current = scrape_current()
    if not current:
        log("Scrape retornou vazio, abortando.")
        return

    last_q = (
        db.collection("snapshots")
        .order_by("ts", direction=firestore.Query.DESCENDING)
        .limit(1)
        .get()
    )
    last_points = last_q[0].to_dict().get("points") if last_q else None

    if last_points == current:
        log("Sem mudanças desde a última coleta.")
        return

    now = datetime.now(timezone.utc)
    label = now.strftime("%Y-%m-%dT%H:%M")
    db.collection("snapshots").add({
        "ts": now,
        "label": label,
        "points": current,
    })
    log(f"Novo snapshot salvo: {label} ({len(current)} participantes).")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
