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

DETAIL_FIELDS = {
    "LT": "lblRkPlacar",
    "PE": "lblbolao_placar_certo",
    "RCGZ": "lblbolao_placar_errado_result_certo_gol_acerto_time",
    "RCG": "lblbolao_placar_errado_result_certo_gol_acerto_exclui_zero",
    "RC": "lblbolao_placar_errado_result_certo",
    "IP": "lblbolao_participacao_incluiu_palpite",
    "SP": "lbbolao_sem_participacao_sem_palpite",
    "OP": "lblbolao_palpite_oposto_somar",
    "OU": "lblbolao_placar_ousado_somar",
    "EE": "lblbolao_empate_placar_errado_somar",
    "GA": "lblbolao_gol_acerto_times_somar",
    "GV": "lblbolao_gol_acerto_vencedor_somar",
    "GP": "lblbolao_gol_acerto_perdedor_somar",
    "GE": "lblbolao_gol_acerto_resultado_errado_somar",
    "PU": "lbluser_bolao_ponto",
    "PX": "lblPontosExtras",
}


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
            """(detailFields) => {
                function getExact(suffix) {
                    const re = new RegExp(`rptRanking_${suffix}_\\\\d+$`);
                    return [...document.querySelectorAll('[id*=rptRanking_]')].filter(el => re.test(el.id));
                }
                const names = document.querySelectorAll('[id*=rptRanking_lkNome]');
                const pts = getExact('lblRkPonto');
                const fieldEls = {};
                for (const key in detailFields) fieldEls[key] = getExact(detailFields[key]);

                const out = [];
                for (let i = 0; i < names.length; i++) {
                    const details = {};
                    for (const key in detailFields) {
                        const v = fieldEls[key][i] ? fieldEls[key][i].innerText.trim() : null;
                        details[key] = v;
                    }
                    out.push({
                        name: names[i].innerText.trim(),
                        pts: pts[i] ? pts[i].innerText.trim() : null,
                        details,
                    });
                }
                return out;
            }""",
            DETAIL_FIELDS,
        )
        browser.close()

    points = {}
    details = {}
    for row in rows:
        if row["pts"] is None:
            continue
        points[row["name"]] = int(row["pts"])
        details[row["name"]] = {
            k: (int(v) if v not in (None, "") else None) for k, v in row["details"].items()
        }
    return points, details


def main():
    db = init_firestore()
    points, details = scrape_current()
    if not points:
        log("Scrape retornou vazio, abortando.")
        return

    last_q = (
        db.collection("snapshots")
        .order_by("ts", direction=firestore.Query.DESCENDING)
        .limit(1)
        .get()
    )
    last_points = last_q[0].to_dict().get("points") if last_q else None

    if last_points == points:
        log("Sem mudanças desde a última coleta.")
        return

    now = datetime.now(timezone.utc)
    label = now.strftime("%Y-%m-%dT%H:%M")
    db.collection("snapshots").add({
        "ts": now,
        "label": label,
        "points": points,
        "details": details,
    })
    log(f"Novo snapshot salvo: {label} ({len(points)} participantes).")


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        sys.exit(1)
