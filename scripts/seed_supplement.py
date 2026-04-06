import sys

sys.path.insert(0, "/app")
from datetime import date, datetime, timedelta
from decimal import Decimal
from app.database import engine
from app.models import (
    QualityCheck,
    SaleRecord,
    InventoryItem,
    ProofingTelemetry,
    QualityInspection,
)
from sqlalchemy.orm import Session
import random

products = [
    ("Butter Croissant", 85.0),
    ("Sourdough Loaf (400g)", 120.0),
    ("Almond Danish", 65.0),
    ("Chocolate Eclair", 55.0),
    ("Butter Cookies (box of 12)", 180.0),
    ("Multigrain Bread Loaf", 95.0),
    ("Cinnamon Roll", 45.0),
    ("Pain au Chocolat", 75.0),
    ("Focaccia Slice", 40.0),
    ("Muffin (Chocolate)", 38.0),
]

with Session(engine) as s:
    qc_data = [
        (82.0, "pass", "Croissant batch A - golden, layered"),
        (91.0, "pass", "Butter cookies - perfect golden"),
        (47.0, "fail", "Rye loaf - over-baked"),
        (73.0, "pass", "Sourdough OK, slight pale patch"),
        (88.0, "pass", "Danish pastry - excellent"),
        (65.0, "needs_review", "Muffin batch - uneven top"),
        (95.0, "pass", "Pain au chocolat - best of day"),
        (58.0, "fail", "Focaccia - under-proofed"),
    ]
    for score, status, notes in qc_data:
        s.add(
            QualityCheck(
                score=score,
                status=status,
                notes=notes,
                anomaly_score=max(0, (80 - score) / 100),
                created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
            )
        )

    count = 0
    for day_offset in range(1, 7):
        sales_day = date.today() - timedelta(days=day_offset)
        for _ in range(random.randint(12, 20)):
            product, price = random.choice(products)
            qty = float(random.randint(1, 8))
            total = Decimal(str(price)) * Decimal(str(qty))
            sold_dt = datetime.combine(sales_day, datetime.min.time()) + timedelta(
                hours=random.randint(8, 20), minutes=random.randint(0, 59)
            )
            s.add(
                SaleRecord(
                    product_name=product,
                    quantity_sold=qty,
                    unit_price=Decimal(str(price)),
                    total_amount=total,
                    sold_at=sold_dt,
                )
            )
            count += 1
    s.commit()

    print("=== Final DB Counts ===")
    print("  Inventory items  :", s.query(InventoryItem).count())
    print("  Proofing readings:", s.query(ProofingTelemetry).count())
    print("  Quality checks   :", s.query(QualityCheck).count())
    print("  Quality insp.    :", s.query(QualityInspection).count())
    print("  Sale records     :", s.query(SaleRecord).count())
    today_rev = sum(
        float(r.total_amount)
        for r in s.query(SaleRecord)
        .filter(
            SaleRecord.sold_at >= datetime.combine(date.today(), datetime.min.time())
        )
        .all()
    )
    print("  Today revenue    : Rs.", round(today_rev, 2))
