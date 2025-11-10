# -*- coding: utf-8 -*-

from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

db = SessionLocal()
properties = [
    models.Property(name="新宿ハイツ", address="東京都新宿区西新宿1-1-1", price=85000),
    models.Property(name="渋谷レジデンス", address="東京都渋谷区渋谷2-2-2", price=125000),
    models.Property(name="池袋マンション", address="東京都豊島区池袋3-3-3", price=99000),
]
db.add_all(properties)
db.commit()
db.close()
print("✅ 初期データを追加しました。")
