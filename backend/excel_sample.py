import pandas as pd
from database import SessionLocal, engine
import models

models.Base.metadata.create_all(bind=engine)

file_path = "../assets/001908994.xlsx"  # 相対パスを調整
# df = pd.read_excel(file_path) #,sheet_name=None

# df.columns = df.iloc[1]  # 2行目を列名に設定
# df = df[3:]  # 3行目までを削除して本データのみ残す
# df = df.reset_index(drop=True)

sheets_dict = pd.read_excel(file_path, sheet_name=None)
columns = ['都道府県名', '市区名', '基準地数', '平均価格', '最上位の価格', '最下位の価格']
df_list = []
for sheet_name, sheet_df in sheets_dict.items():
    temp_df = pd.DataFrame(sheet_df.values, columns=columns)
    df_list.append(temp_df)
df = pd.concat(df_list, ignore_index=True)

# 「都道府県名」列を直近の値で置換 / 平均価格Nanは削除
df["平均価格"] = pd.to_numeric(df["平均価格"], errors="coerce")
df = df.dropna(subset=['平均価格']).reset_index(drop=True)
df["平均価格"] = df["平均価格"].astype(int)
df['都道府県名'] = df['都道府県名'].replace('〃', pd.NA)  # まず〃をNaに
df['都道府県名'] = df['都道府県名'].fillna(method='ffill')  # 上の値で埋める

db = SessionLocal()
properties = []
for _, row in df.iterrows():
    name = row['市区名']  # 物件名に使う場合
    address = f"{row['都道府県名']}"  # 住所として都道府県名+市区名
    price = int(row['平均価格'])  # 数値型でない場合、カンマ除去してintに
    properties.append(models.Property(name=name, address=address, price=price))

db.add_all(properties)
db.commit()
db.close()
print("✅ 初期データを追加しました。")

# xls = pd.ExcelFile(file_path)
# print("シート名一覧:", xls.sheet_names)

# sheets_data = {}
# for sheet_name in xls.sheet_names:
#     df = pd.read_excel(file_path, sheet_name=sheet_name)
#     sheets_data[sheet_name] = df

# # データ確認
# for name, df in sheets_data.items():
#     print(f"\n=== {name} ===")
#     print(df[:10]) 

# print("Columns:", df.columns.tolist())
# print("len:", len(df))
# print(df.head())