# -*- coding: utf-8 -*-
# Roda uma única vez, manualmente, para popular o histórico já coletado antes do Firestore existir.
# Uso: GOOGLE_APPLICATION_CREDENTIALS=caminho\para\service-account.json python seed_history.py
import json
import os
from datetime import datetime, timezone

import firebase_admin
from firebase_admin import credentials, firestore

HISTORY = {
"2026-06-11": {"José Maurício Finco Mendonça":6,"Alishow":10,"Pedro Henrique":10,"Dinegro":10,"Tião berranteiro":9,"Bruna Veloso":10,"Elza Helena Volpato":14,"Ruthyson":11,"Justyn":10,"Amanda Lemos":7,"Guiby Shelby":5,"Geraldo S2":-1,"Gambiarra Engineering":2,"Não sobra nada para o Betta":6,"Ana Paula Perussolo":10,"Liliuwandowski":10,"Julia Ekermann":2,"Fabrício Cichocki":11,"Alexandre Munaretto":9},
"2026-06-12": {"José Maurício Finco Mendonça":13,"Alishow":12,"Pedro Henrique":11,"Dinegro":14,"Tião berranteiro":10,"Bruna Veloso":10,"Elza Helena Volpato":18,"Ruthyson":13,"Justyn":11,"Amanda Lemos":8,"Guiby Shelby":7,"Geraldo S2":5,"Gambiarra Engineering":3,"Não sobra nada para o Betta":8,"Ana Paula Perussolo":14,"Liliuwandowski":14,"Julia Ekermann":2,"Fabrício Cichocki":16,"Alexandre Munaretto":7},
"2026-06-13": {"José Maurício Finco Mendonça":16,"Alishow":15,"Pedro Henrique":14,"Dinegro":17,"Tião berranteiro":13,"Bruna Veloso":13,"Elza Helena Volpato":20,"Ruthyson":22,"Justyn":19,"Amanda Lemos":11,"Guiby Shelby":10,"Geraldo S2":8,"Gambiarra Engineering":5,"Não sobra nada para o Betta":11,"Ana Paula Perussolo":17,"Liliuwandowski":16,"Julia Ekermann":8,"Fabrício Cichocki":19,"Alexandre Munaretto":4},
"2026-06-14": {"José Maurício Finco Mendonça":24,"Alishow":23,"Pedro Henrique":38,"Dinegro":23,"Tião berranteiro":16,"Bruna Veloso":21,"Elza Helena Volpato":26,"Ruthyson":28,"Justyn":19,"Amanda Lemos":17,"Guiby Shelby":18,"Geraldo S2":9,"Gambiarra Engineering":12,"Não sobra nada para o Betta":17,"Ana Paula Perussolo":23,"Liliuwandowski":20,"Julia Ekermann":7,"Fabrício Cichocki":31,"Alexandre Munaretto":-1},
"2026-06-15": {"José Maurício Finco Mendonça":24,"Alishow":26,"Pedro Henrique":47,"Dinegro":23,"Tião berranteiro":19,"Bruna Veloso":24,"Elza Helena Volpato":26,"Ruthyson":31,"Justyn":19,"Amanda Lemos":20,"Guiby Shelby":21,"Geraldo S2":9,"Gambiarra Engineering":18,"Não sobra nada para o Betta":17,"Ana Paula Perussolo":23,"Liliuwandowski":20,"Julia Ekermann":3,"Fabrício Cichocki":34,"Alexandre Munaretto":-5},
"2026-06-16": {"José Maurício Finco Mendonça":36,"Alishow":33,"Pedro Henrique":66,"Dinegro":40,"Tião berranteiro":47,"Bruna Veloso":44,"Elza Helena Volpato":37,"Ruthyson":41,"Justyn":36,"Amanda Lemos":31,"Guiby Shelby":49,"Geraldo S2":20,"Gambiarra Engineering":27,"Não sobra nada para o Betta":32,"Ana Paula Perussolo":43,"Liliuwandowski":29,"Julia Ekermann":0,"Fabrício Cichocki":40,"Alexandre Munaretto":-8},
"2026-06-17": {"José Maurício Finco Mendonça":50,"Alishow":44,"Pedro Henrique":77,"Dinegro":51,"Tião berranteiro":54,"Bruna Veloso":58,"Elza Helena Volpato":43,"Ruthyson":57,"Justyn":46,"Amanda Lemos":50,"Guiby Shelby":57,"Geraldo S2":28,"Gambiarra Engineering":28,"Não sobra nada para o Betta":39,"Ana Paula Perussolo":55,"Liliuwandowski":36,"Julia Ekermann":5,"Fabrício Cichocki":53,"Alexandre Munaretto":-13},
"2026-06-18": {"José Maurício Finco Mendonça":57,"Alishow":51,"Pedro Henrique":83,"Dinegro":52,"Tião berranteiro":60,"Bruna Veloso":71,"Elza Helena Volpato":49,"Ruthyson":60,"Justyn":51,"Amanda Lemos":56,"Guiby Shelby":66,"Geraldo S2":32,"Gambiarra Engineering":41,"Não sobra nada para o Betta":43,"Ana Paula Perussolo":67,"Liliuwandowski":43,"Julia Ekermann":1,"Fabrício Cichocki":57,"Alexandre Munaretto":-17},
"2026-06-19": {"José Maurício Finco Mendonça":76,"Alishow":78,"Pedro Henrique":92,"Dinegro":72,"Tião berranteiro":69,"Bruna Veloso":75,"Elza Helena Volpato":63,"Ruthyson":74,"Justyn":59,"Amanda Lemos":67,"Guiby Shelby":76,"Geraldo S2":34,"Gambiarra Engineering":53,"Não sobra nada para o Betta":62,"Ana Paula Perussolo":74,"Liliuwandowski":51,"Julia Ekermann":3,"Fabrício Cichocki":64,"Alexandre Munaretto":-21},
"2026-06-20": {"José Maurício Finco Mendonça":84,"Alishow":84,"Pedro Henrique":98,"Dinegro":80,"Tião berranteiro":75,"Bruna Veloso":84,"Elza Helena Volpato":71,"Ruthyson":86,"Justyn":68,"Amanda Lemos":75,"Guiby Shelby":82,"Geraldo S2":40,"Gambiarra Engineering":62,"Não sobra nada para o Betta":70,"Ana Paula Perussolo":82,"Liliuwandowski":49,"Julia Ekermann":8,"Fabrício Cichocki":68,"Alexandre Munaretto":-24},
"2026-06-21": {"José Maurício Finco Mendonça":95,"Alishow":92,"Pedro Henrique":115,"Dinegro":89,"Tião berranteiro":96,"Bruna Veloso":90,"Elza Helena Volpato":77,"Ruthyson":93,"Justyn":79,"Amanda Lemos":84,"Guiby Shelby":90,"Geraldo S2":50,"Gambiarra Engineering":68,"Não sobra nada para o Betta":80,"Ana Paula Perussolo":89,"Liliuwandowski":54,"Julia Ekermann":13,"Fabrício Cichocki":70,"Alexandre Munaretto":-29},
"2026-06-22": {"José Maurício Finco Mendonça":112,"Alishow":121,"Pedro Henrique":125,"Dinegro":118,"Tião berranteiro":113,"Bruna Veloso":126,"Elza Helena Volpato":87,"Ruthyson":103,"Justyn":85,"Amanda Lemos":101,"Guiby Shelby":115,"Geraldo S2":65,"Gambiarra Engineering":79,"Não sobra nada para o Betta":107,"Ana Paula Perussolo":107,"Liliuwandowski":68,"Julia Ekermann":34,"Fabrício Cichocki":79,"Alexandre Munaretto":-33},
"2026-06-23": {"José Maurício Finco Mendonça":121,"Alishow":129,"Pedro Henrique":132,"Dinegro":125,"Tião berranteiro":122,"Bruna Veloso":134,"Elza Helena Volpato":93,"Ruthyson":111,"Justyn":92,"Amanda Lemos":108,"Guiby Shelby":123,"Geraldo S2":73,"Gambiarra Engineering":87,"Não sobra nada para o Betta":113,"Ana Paula Perussolo":115,"Liliuwandowski":75,"Julia Ekermann":44,"Fabrício Cichocki":89,"Alexandre Munaretto":-37},
"2026-06-24": {"José Maurício Finco Mendonça":145,"Alishow":140,"Pedro Henrique":149,"Dinegro":146,"Tião berranteiro":140,"Bruna Veloso":151,"Elza Helena Volpato":108,"Ruthyson":134,"Justyn":123,"Amanda Lemos":138,"Guiby Shelby":138,"Geraldo S2":95,"Gambiarra Engineering":112,"Não sobra nada para o Betta":127,"Ana Paula Perussolo":125,"Liliuwandowski":92,"Julia Ekermann":56,"Fabrício Cichocki":112,"Alexandre Munaretto":-43},
"2026-06-25": {"José Maurício Finco Mendonça":156,"Alishow":151,"Pedro Henrique":163,"Dinegro":161,"Tião berranteiro":152,"Bruna Veloso":171,"Elza Helena Volpato":133,"Ruthyson":152,"Justyn":135,"Amanda Lemos":145,"Guiby Shelby":144,"Geraldo S2":112,"Gambiarra Engineering":121,"Não sobra nada para o Betta":135,"Ana Paula Perussolo":142,"Liliuwandowski":111,"Julia Ekermann":64,"Fabrício Cichocki":106,"Alexandre Munaretto":-49},
"2026-06-26": {"José Maurício Finco Mendonça":177,"Alishow":165,"Pedro Henrique":171,"Dinegro":171,"Tião berranteiro":165,"Bruna Veloso":180,"Elza Helena Volpato":147,"Ruthyson":163,"Justyn":140,"Amanda Lemos":159,"Guiby Shelby":154,"Geraldo S2":132,"Gambiarra Engineering":132,"Não sobra nada para o Betta":149,"Ana Paula Perussolo":146,"Liliuwandowski":121,"Julia Ekermann":78,"Fabrício Cichocki":112,"Alexandre Munaretto":-55},
"2026-06-27": {"José Maurício Finco Mendonça":195,"Alishow":185,"Pedro Henrique":181,"Dinegro":178,"Tião berranteiro":183,"Bruna Veloso":189,"Elza Helena Volpato":163,"Ruthyson":176,"Justyn":148,"Amanda Lemos":172,"Guiby Shelby":161,"Geraldo S2":151,"Gambiarra Engineering":151,"Não sobra nada para o Betta":158,"Ana Paula Perussolo":160,"Liliuwandowski":125,"Julia Ekermann":72,"Fabrício Cichocki":106,"Alexandre Munaretto":-61},
"2026-06-28": {"José Maurício Finco Mendonça":198,"Alishow":187,"Pedro Henrique":183,"Dinegro":187,"Tião berranteiro":185,"Bruna Veloso":191,"Elza Helena Volpato":165,"Ruthyson":178,"Justyn":150,"Amanda Lemos":172,"Guiby Shelby":164,"Geraldo S2":153,"Gambiarra Engineering":153,"Não sobra nada para o Betta":160,"Ana Paula Perussolo":162,"Liliuwandowski":127,"Julia Ekermann":71,"Fabrício Cichocki":105,"Alexandre Munaretto":-62},
"2026-06-29": {"José Maurício Finco Mendonça":208,"Alishow":197,"Pedro Henrique":194,"Dinegro":192,"Tião berranteiro":194,"Bruna Veloso":195,"Elza Helena Volpato":174,"Ruthyson":183,"Justyn":159,"Amanda Lemos":177,"Guiby Shelby":168,"Geraldo S2":157,"Gambiarra Engineering":158,"Não sobra nada para o Betta":165,"Ana Paula Perussolo":161,"Liliuwandowski":137,"Julia Ekermann":80,"Fabrício Cichocki":102,"Alexandre Munaretto":-65},
"2026-06-30": {"José Maurício Finco Mendonça":225,"Alishow":217,"Pedro Henrique":201,"Dinegro":210,"Tião berranteiro":205,"Bruna Veloso":202,"Elza Helena Volpato":193,"Ruthyson":203,"Justyn":176,"Amanda Lemos":189,"Guiby Shelby":183,"Geraldo S2":179,"Gambiarra Engineering":165,"Não sobra nada para o Betta":177,"Ana Paula Perussolo":175,"Liliuwandowski":151,"Julia Ekermann":89,"Fabrício Cichocki":99,"Alexandre Munaretto":-68},
"2026-07-01": {"José Maurício Finco Mendonça":232,"Alishow":226,"Pedro Henrique":207,"Dinegro":218,"Tião berranteiro":219,"Bruna Veloso":212,"Elza Helena Volpato":206,"Ruthyson":211,"Justyn":185,"Amanda Lemos":196,"Guiby Shelby":194,"Geraldo S2":191,"Gambiarra Engineering":175,"Não sobra nada para o Betta":188,"Ana Paula Perussolo":184,"Liliuwandowski":163,"Julia Ekermann":95,"Fabrício Cichocki":96,"Alexandre Munaretto":-71},
"2026-07-02": {"José Maurício Finco Mendonça":255,"Alishow":245,"Pedro Henrique":238,"Dinegro":238,"Tião berranteiro":228,"Bruna Veloso":228,"Elza Helena Volpato":227,"Ruthyson":225,"Justyn":216,"Amanda Lemos":213,"Guiby Shelby":206,"Geraldo S2":205,"Gambiarra Engineering":196,"Não sobra nada para o Betta":192,"Ana Paula Perussolo":189,"Liliuwandowski":171,"Julia Ekermann":104,"Fabrício Cichocki":93,"Alexandre Munaretto":-74},
"2026-07-03": {"José Maurício Finco Mendonça":255,"Alishow":245,"Pedro Henrique":238,"Dinegro":238,"Tião berranteiro":228,"Bruna Veloso":228,"Elza Helena Volpato":227,"Ruthyson":225,"Justyn":216,"Amanda Lemos":213,"Guiby Shelby":206,"Geraldo S2":205,"Gambiarra Engineering":196,"Não sobra nada para o Betta":192,"Ana Paula Perussolo":189,"Liliuwandowski":171,"Julia Ekermann":104,"Fabrício Cichocki":93,"Alexandre Munaretto":-74}
}


def main():
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    if not cred_path:
        raise SystemExit("Defina GOOGLE_APPLICATION_CREDENTIALS apontando para o JSON da service account.")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)
    db = firestore.client()

    batch = db.batch()
    col = db.collection("snapshots")
    for date_str, points in HISTORY.items():
        ts = datetime.strptime(date_str, "%Y-%m-%d").replace(hour=23, minute=59, tzinfo=timezone.utc)
        doc_ref = col.document(date_str)
        batch.set(doc_ref, {"ts": ts, "label": date_str, "points": points})
    batch.commit()
    print(f"Semeados {len(HISTORY)} snapshots históricos.")


if __name__ == "__main__":
    main()
