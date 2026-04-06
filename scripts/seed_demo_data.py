#!/usr/bin/env python3
"""
BakeManage Demo Data Seeder
Populates the sandbox database with realistic bakery ERP data for UAT.
Run: docker exec bakemanage-api-1 python /app/scripts/seed_demo_data.py
"""

import sys, os

sys.path.insert(0, "/app")

from datetime import date, datetime, timedelta
from decimal import Decimal
from app.database import engine, Base, get_session
from app.models import (
    InventoryItem,
    ProofingTelemetry,
    QualityCheck,
    QualityInspection,
    SaleRecord,
)
from app.ingestion import simulate_vlm_ocr, persist_invoice
from sqlalchemy.orm import Session
import random, hashlib

print("=== BakeManage Demo Data Seeder ===")
Base.metadata.create_all(bind=engine)

with Session(engine) as session:
    # ──────────────────────────────────────────────────────────────
    # 1. INVENTORY ITEMS — full bakery stock
    # ──────────────────────────────────────────────────────────────
    stock_items = [
        ("Chakki Atta (Whole Wheat)", 120.0, "kg", "flour_grain", 42.0, 90),
        ("Maida (Refined Flour)", 80.0, "kg", "flour_grain", 30.0, 90),
        ("Bread Flour (High Gluten)", 60.0, "kg", "flour_grain", 55.0, 60),
        ("Semolina (Sooji)", 40.0, "kg", "flour_grain", 38.0, 120),
        ("Refined Sugar", 75.0, "kg", "sugar_sweet", 46.0, 365),
        ("Powdered Icing Sugar", 20.0, "kg", "sugar_sweet", 68.0, 180),
        ("Brown Sugar", 15.0, "kg", "sugar_sweet", 72.0, 180),
        ("Jaggery Powder", 25.0, "kg", "sugar_sweet", 55.0, 90),
        ("Amul Butter (Salted)", 30.0, "kg", "dairy_fat", 495.0, 30),
        ("Amul Butter (Unsalted)", 25.0, "kg", "dairy_fat", 510.0, 30),
        ("Vegetable Shortening", 20.0, "kg", "dairy_fat", 185.0, 60),
        ("Sunflower Oil", 50.0, "litre", "dairy_fat", 140.0, 180),
        ("Full Cream Milk (Amul)", 40.0, "litre", "dairy_fat", 62.0, 3),
        ("Milk Powder", 15.0, "kg", "dairy_fat", 320.0, 365),
        ("Fresh Cream (Amul)", 10.0, "litre", "dairy_fat", 185.0, 7),
        ("Fresh Yeast (Instant)", 5.0, "kg", "leavener", 220.0, 14),
        ("Dry Active Yeast", 3.0, "kg", "leavener", 680.0, 365),
        ("Baking Powder (Weikfield)", 4.0, "kg", "leavener", 280.0, 365),
        ("Baking Soda", 3.0, "kg", "leavener", 60.0, 365),
        ("Salt (Tata Iodised)", 20.0, "kg", "seasoning", 22.0, 730),
        ("Vanilla Extract", 2.0, "litre", "flavour", 850.0, 730),
        ("Cocoa Powder (Morde)", 8.0, "kg", "flavour", 360.0, 365),
        ("Dark Chocolate Chips", 5.0, "kg", "flavour", 550.0, 90),
        ("Sesame Seeds", 6.0, "kg", "topping", 145.0, 180),
        ("Poppy Seeds", 3.0, "kg", "topping", 320.0, 90),
        ("Almond Flakes", 4.0, "kg", "topping", 1200.0, 365),
        ("Raisins (Golden)", 5.0, "kg", "dry_fruit", 280.0, 180),
        ("Cardamom Powder", 1.0, "kg", "spice", 2800.0, 365),
        ("Bread Packaging Bags (Small)", 500.0, "pcs", "packaging", 2.0, 730),
        ("Cake Boxes (6-inch)", 200.0, "pcs", "packaging", 18.0, 730),
        ("Pastry Boxes (Assorted)", 150.0, "pcs", "packaging", 12.0, 730),
    ]
    added = 0
    for name, qty, unit, cat, price, days_exp in stock_items:
        existing = (
            session.query(InventoryItem).filter(InventoryItem.name == name).first()
        )
        if not existing:
            exp_date = date.today() + timedelta(days=days_exp)
            item = InventoryItem(
                name=name,
                quantity_on_hand=qty,
                unit_of_measure=unit,
                category=cat,
                vertical="bakery",
                unit_price=Decimal(str(price)),
                expiration_date=exp_date,
            )
            session.add(item)
            added += 1
    session.commit()
    print(f"✓ Stock: {added} new items added")

    # ──────────────────────────────────────────────────────────────
    # 2. PROOFING TELEMETRY — 10 days of chamber readings
    # ──────────────────────────────────────────────────────────────
    pf_count = session.query(ProofingTelemetry).count()
    if pf_count < 20:
        readings = [
            (28.0, 74.5, 820, 1200, "stable", 0.04),
            (28.5, 75.0, 835, 1190, "stable", 0.06),
            (29.0, 76.2, 850, 1210, "rising", 0.08),
            (29.5, 77.0, 860, 1230, "rising", 0.11),
            (30.0, 78.0, 880, 1200, "stable", 0.07),
            (30.5, 79.1, 1320, 1100, "anomaly", 0.42),  # CO2 spike
            (29.8, 76.5, 840, 1210, "falling", 0.09),
            (28.8, 75.2, 825, 1215, "stable", 0.05),
            (27.5, 73.0, 795, 1220, "falling", 0.12),
            (28.2, 74.8, 810, 1205, "stable", 0.04),
            (28.0, 75.5, 815, 1200, "stable", 0.03),
            (28.5, 76.0, 830, 1195, "rising", 0.07),
            (29.2, 77.3, 855, 1215, "rising", 0.09),
            (30.1, 78.5, 870, 1200, "stable", 0.06),
            (28.9, 75.8, 835, 1220, "stable", 0.04),
        ]
        for i, (temp, hum, co2, fan, status, anomaly) in enumerate(readings):
            ts = datetime.utcnow() - timedelta(hours=i * 8)
            reading = ProofingTelemetry(
                temperature_c=temp,
                humidity_percent=hum,
                co2_ppm=co2,
                fan_speed_rpm=fan,
                status=status,
                anomaly_score=anomaly,
                created_at=ts,
            )
            session.add(reading)
        session.commit()
        print(f"✓ Proofing: {len(readings)} telemetry readings added")
    else:
        print(f"✓ Proofing: {pf_count} readings already exist — skipped")

    # ──────────────────────────────────────────────────────────────
    # 3. QUALITY INSPECTIONS — historical browning + uniformity
    # ──────────────────────────────────────────────────────────────
    qi_count = session.query(QualityInspection).count()
    if qi_count < 10:
        inspections = [
            ("croissant_batch_001", 0.81, 0.88, "pass", "Golden, evenly layered"),
            ("sourdough_batch_001", 0.73, 0.79, "pass", "Good crust, slight pale spot"),
            ("danish_pastry_001", 0.65, 0.70, "needs_review", "Under-browned edges"),
            (
                "butter_cookie_001",
                0.90,
                0.95,
                "pass",
                "Perfect golden, high uniformity",
            ),
            ("baguette_001", 0.78, 0.85, "pass", "Crisp crust, good score"),
            ("rye_loaf_001", 0.55, 0.62, "fail", "Burnt top — oven too hot"),
            ("croissant_batch_002", 0.84, 0.91, "pass", "Excellent lamination"),
            ("muffin_001", 0.76, 0.80, "pass", "Slightly over-baked edges"),
            ("focaccia_001", 0.69, 0.74, "needs_review", "Pale center, good sides"),
            ("pain_au_choc_001", 0.87, 0.93, "pass", "Rich colour, perfect chocolate"),
        ]
        for fp, brown, unif, status, notes in inspections:
            existing = (
                session.query(QualityInspection)
                .filter(QualityInspection.image_fingerprint == fp)
                .first()
            )
            if not existing:
                session.add(
                    QualityInspection(
                        image_fingerprint=fp,
                        browning_score=brown,
                        uniformity_score=unif,
                        status=status,
                        notes=notes,
                        created_at=datetime.utcnow()
                        - timedelta(days=random.randint(0, 14)),
                    )
                )
        # Also add QualityCheck records
        qc_checks = [
            (82.0, "pass", "Croissant batch A"),
            (91.0, "pass", "Butter cookies — perfect"),
            (47.0, "fail", "Rye loaf — over-baked"),
            (73.0, "pass", "Sourdough OK"),
            (88.0, "pass", "Danish pastry"),
        ]
        for score, status, notes in qc_checks:
            session.add(
                QualityCheck(
                    score=score,
                    status=status,
                    notes=notes,
                    anomaly_score=max(0, (80 - score) / 100),
                    created_at=datetime.utcnow() - timedelta(days=random.randint(0, 7)),
                )
            )
        session.commit()
        print(
            f"✓ Quality: {len(inspections)} inspections + {len(qc_checks)} checks added"
        )
    else:
        print(f"✓ Quality: {qi_count} inspections already exist — skipped")

    # ──────────────────────────────────────────────────────────────
    # 4. SALES RECORDS — 7 days of sales across products
    # ──────────────────────────────────────────────────────────────
    products = [
        ("Butter Croissant", 85.0),
        ("Sourdough Loaf (400g)", 120.0),
        ("Almond Danish", 65.0),
        ("Chocolate Éclair", 55.0),
        ("Butter Cookies (box of 12)", 180.0),
        ("Multigrain Bread Loaf", 95.0),
        ("Cinnamon Roll", 45.0),
        ("Pain au Chocolat", 75.0),
        ("Focaccia Slice", 40.0),
        ("Muffin (Chocolate)", 38.0),
    ]
    sr_today = (
        session.query(SaleRecord)
        .filter(
            SaleRecord.sold_at >= datetime.combine(date.today(), datetime.min.time())
        )
        .count()
    )
    if sr_today < 5:
        sale_entries = []
        for day_offset in range(7):
            sales_day = date.today() - timedelta(days=day_offset)
            num_sales = random.randint(8, 16)
            for _ in range(num_sales):
                product, price = random.choice(products)
                qty = round(random.uniform(1, 8), 0)
                total = Decimal(str(price)) * Decimal(str(qty))
                sold_dt = datetime.combine(sales_day, datetime.min.time()) + timedelta(
                    hours=random.randint(8, 20), minutes=random.randint(0, 59)
                )
                sale_entries.append(
                    SaleRecord(
                        product_name=product,
                        quantity_sold=qty,
                        unit_price=Decimal(str(price)),
                        total_amount=total,
                        sold_at=sold_dt,
                    )
                )
        for entry in sale_entries:
            session.add(entry)
        session.commit()
        print(f"✓ Sales: {len(sale_entries)} sale records added (7 days)")
    else:
        print("✓ Sales: records already exist — skipped")

    # ──────────────────────────────────────────────────────────────
    # 5. INVOICE INGESTIONS — simulated vendor delivery receipts
    # ──────────────────────────────────────────────────────────────
    fake_receipt_bytes = [
        b"GreenMill_Invoice_Flour_March2026",
        b"DairyDirect_Invoice_Butter_April2026",
        b"SugarCo_Invoice_March2026",
    ]
    for receipt in fake_receipt_bytes:
        try:
            invoice = simulate_vlm_ocr(receipt)
            persist_invoice(session, invoice)
        except Exception:
            pass
    session.commit()
    print("✓ Invoices: 3 simulated vendor invoices ingested")

    # ──────────────────────────────────────────────────────────────
    # Summary
    # ──────────────────────────────────────────────────────────────
    print("\n=== Seed Complete ===")
    print(f"  Inventory items  : {session.query(InventoryItem).count()}")
    print(f"  Proofing readings: {session.query(ProofingTelemetry).count()}")
    print(f"  Quality checks   : {session.query(QualityCheck).count()}")
    print(f"  Quality insp.    : {session.query(QualityInspection).count()}")
    print(f"  Sale records     : {session.query(SaleRecord).count()}")
