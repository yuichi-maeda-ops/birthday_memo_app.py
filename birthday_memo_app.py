import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path

st.set_page_config(page_title="Birthday Memo", layout="centered")
st.title("🎂 Birthday Memo")

# 🔐 ユーザー名を入力
st.sidebar.header("👤 ユーザー選択")
username = st.sidebar.text_input("あなたの名前（例：maedayuichi）", value="guest")

if not username:
    st.warning("ユーザー名を入力してください。")
    st.stop()

# ✅ データ保存先（Streamlit Cloud でも動作するように）
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)
DATA_FILE = DATA_DIR / f"{username}.json"
MAX_GRANDCHILDREN = 10

# データ初期化
if not DATA_FILE.exists():
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f)

# データ読み込み
with open(DATA_FILE, "r", encoding="utf-8") as f:
    birthday_data = json.load(f)

year = st.number_input("年を選択（修正・新規入力用）", min_value=1900, max_value=2100, value=datetime.now().year)

def get_existing(role):
    entries = birthday_data.get(role, [])
    for entry in entries:
        if entry["年"] == year:
            return entry["名前"], entry["したこと"]
    return "", ""

def input_section(label, key_prefix, existing_name, existing_memo, emoji=""):
    st.subheader(f"{emoji} {label}")
    name = st.text_input(f"{label}の名前", value=existing_name, key=f"{key_prefix}_name")
    memo = st.text_area(f"{label}の{year}年の誕生日にしたこと", value=existing_memo, key=f"{key_prefix}_memo")
    return name, memo

# 既存データ取得
roles = ["自分", "配偶者", "子供1", "子供2", "子供3"]
icons = ["🎈", "💐", "👶", "👦", "👧"]
inputs = {}

for role, icon in zip(roles, icons):
    name0, memo0 = get_existing(role)
    name, memo = input_section("妻 or 夫" if role == "配偶者" else role, role, name0, memo0, icon)
    inputs[role] = {"名前": name, "年": year, "したこと": memo}

# 孫の動的セクション
st.markdown("---")
st.subheader("🐱 孫の記録")

if "num_grandchildren" not in st.session_state:
    st.session_state.num_grandchildren = 3

if st.button("➕ 孫を追加"):
    if st.session_state.num_grandchildren < MAX_GRANDCHILDREN:
        st.session_state.num_grandchildren += 1
    else:
        st.warning("これ以上追加できません（最大10人まで）")

grandchildren = []
for i in range(1, st.session_state.num_grandchildren + 1):
    key = f"孫{i}"
    name0, memo0 = get_existing(key)
    name, memo = input_section(f"孫{i}", f"grand{i}", name0, memo0, "🐱")
    grandchildren.append((key, name, memo))

# 保存処理
if st.button("💾 この年の記録を保存・修正"):
    new_data = inputs.copy()
    for idx, (role, name, memo) in enumerate(grandchildren, 1):
        if name and memo:
            new_data[role] = {"名前": name, "年": year, "したこと": memo}

    for role, entry in new_data.items():
        if entry["名前"] and entry["したこと"]:
            existing = birthday_data.get(role, [])
            updated = [e for e in existing if e["年"] != year]
            updated.append(entry)
            birthday_data[role] = updated

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(birthday_data, f, ensure_ascii=False, indent=2)

    st.success(f"{year}年の記録を保存・更新しました！")

# 一覧表示
st.markdown("---")
st.header(f"📜 {username} さんの記録一覧")

if not birthday_data:
    st.info("保存された記録はまだありません。")
else:
    for role, records in birthday_data.items():
        icon = "🐱" if "孫" in role else "👤"
        st.subheader(f"{icon} {role}")
        for r in sorted(records, key=lambda x: x["年"], reverse=True):
            st.markdown(f"- {r['年']}年：**{r['名前']}** → {r['したこと']}")
