from datetime import date, datetime, timedelta

import numpy as np

from src.database.repositories import Repository


def seed_demo_data(repo: Repository, force_reset: bool = False) -> None:
    counts = repo.counts()
    if not force_reset and counts["products"] > 0:
        return
    if force_reset:
        repo.reset_all_data()

    rng = np.random.default_rng(42)

    products = [
        ("Saucisson de dinde", "Charcuterie", "kg", 80),
        ("Mortadelle de volaille", "Charcuterie", "kg", 120),
        ("Jambon de poulet", "Charcuterie", "kg", 100),
        ("Nuggets halal", "Surgelé", "kg", 150),
        ("Merguez préparée", "Traiteur", "kg", 70),
    ]
    product_ids = {}
    for p in products:
        pid = repo.create_product(*p)
        product_ids[p[0]] = pid

    today = date.today()
    batch_specs = [
        ("LOT-SIM-001", "Saucisson de dinde", today - timedelta(days=12), today + timedelta(days=2), 240.0, "Terminé"),  # proche péremption
        ("LOT-SIM-002", "Mortadelle de volaille", today - timedelta(days=45), today - timedelta(days=1), 180.0, "Expiré"),  # expiré
        ("LOT-SIM-003", "Jambon de poulet", today - timedelta(days=7), today + timedelta(days=25), 220.0, "Terminé"),
        ("LOT-SIM-004", "Nuggets halal", today - timedelta(days=5), today + timedelta(days=45), 300.0, "En production"),
        ("LOT-SIM-005", "Merguez préparée", today - timedelta(days=3), today + timedelta(days=15), 90.0, "Bloqué"),
    ]

    for code, pname, prod_d, exp_d, qty, status in batch_specs:
        repo.create_batch_atomic(
            batch_code=code,
            product_id=product_ids[pname],
            production_date=prod_d.isoformat(),
            expiration_date=exp_d.isoformat(),
            quantity_produced=qty,
            status=status,
            notes="SIMULATED DATA — Lot académique de démonstration",
        )

    # Sorties pour créer un cas de stock bas
    repo.record_inventory_movement(product_ids["Merguez préparée"], None, "sortie", 50.0, today.isoformat(), "SIMULATED DATA — Vente interne")
    repo.record_inventory_movement(product_ids["Merguez préparée"], None, "sortie", 30.0, today.isoformat(), "SIMULATED DATA — Ajustement")

    # Températures (inclure valeur hors plage)
    base_dt = datetime.now() - timedelta(hours=48)
    locations = ["Chambre froide A", "Chambre froide B", "Zone expédition"]
    for i in range(72):
        loc = locations[i % len(locations)]
        measured_at = (base_dt + timedelta(hours=i)).replace(minute=0, second=0, microsecond=0)
        min_c, max_c = 0.0, 4.0
        temp = float(rng.normal(2.5, 0.8))
        if i == 14:
            temp = 8.5  # hors plage délibéré
        repo.add_temperature_measurement(
            location=loc,
            measured_at=measured_at.isoformat(timespec="seconds"),
            temperature_c=temp,
            minimum_allowed_c=min_c,
            maximum_allowed_c=max_c,
            source="SIMULATED DATA — Capteur virtuel",
        )

    # Ventes journalières simulées déterministes
    start = today - timedelta(days=90)
    product_list = list(product_ids.items())
    for d_idx in range(91):
        d = start + timedelta(days=d_idx)
        season = 1.0 + 0.25 * np.sin(d_idx / 10)
        for pname, pid in product_list:
            base = 12 + (pid % 5) * 3
            q = max(0, float(base * season + rng.normal(0, 2)))
            repo.add_sale(pid, d.isoformat(), round(q, 2))
