import os
import csv
import sqlite3
import time
import random
from dotenv import load_dotenv
from google import genai
from tqdm import tqdm

# 🔹 .env에서 API Key 로드
load_dotenv()
client = genai.Client()

input_file = "anki_deck_before.csv"
output_file = "anki_deck_after_6.csv"

# 🔹 SQLite 초기화
conn = sqlite3.connect("anki_temp6.db")
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS words (
    idx INTEGER PRIMARY KEY,
    word TEXT,
    enriched TEXT
)
""")
conn.commit()

# 🔹 CSV 읽기
words_list = []
with open(input_file, newline="", encoding="utf-8") as infile:
    reader = csv.reader(infile)
    for idx, row in enumerate(reader):
        word = row[0].strip()
        meaning = row[1].strip() if len(row) > 1 else ""
        words_list.append((idx, word, meaning))

# 🔹 이미 처리된 단어 확인
c.execute("SELECT idx, enriched FROM words")
processed = {row[0]: row[1] for row in c.fetchall()}

# 🔹 처리할 단어만 선택
to_process = [w for w in words_list if w[0] not in processed]

# 🔹 단어 1개씩 API 호출
def enrich_single_word(word_tuple):
    idx, word, meaning = word_tuple
    prompt = f"""(!ONLY respond with CSV-ready OUTPUT. Don't markdown bullet)
You are an English vocabulary learning assistant for Koreans to memorize English words.
Do NOT generate code.
Return ONLY a single line in this exact CSV format:
word,"meaning || 어원/암기팁 || Example sentence | Example sentence translated in Korean"
Do not add any extra text, bullet points, or numbering.
Word: {word}
Meaning: {meaning}"""
    
    for attempt in range(1, 6):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            enriched = response.text.strip()
            return (idx, word, enriched)
        except Exception as e:
            wait_time = 2 ** attempt + random.uniform(0, 1)
            print(f"⚠️ Attempt {attempt} failed for '{word}': {e}. Retrying in {wait_time:.1f}s")
            time.sleep(wait_time)
    
    # 모든 시도 실패 시
    return (idx, word, "Failed")

# 🔹 배치 실행 (단어 1개씩)
def run_words(word_list, label="Processing"):
    progress_bar = tqdm(total=len(word_list), desc=label)
    for word_tuple in word_list:
        idx, word, enriched = enrich_single_word(word_tuple)
        conn.execute(
            "INSERT OR REPLACE INTO words (idx, word, enriched) VALUES (?, ?, ?)",
            (idx, word, enriched)
        )
        conn.commit()
        progress_bar.update(1)
    progress_bar.close()

# 🔹 1차 실행
run_words(to_process, label="First pass")

# 🔹 Failed 항목 재실행 (최대 3회)
for retry_round in range(1, 4):
    c.execute("SELECT idx, word, enriched FROM words ORDER BY idx ASC")
    current_rows = c.fetchall()
    failed_words = [(idx, word, "") for idx, word, enriched in current_rows if enriched == "Failed"]

    if not failed_words:
        print("✅ No failed items left")
        break

    print(f"🔄 Retry round {retry_round}: {len(failed_words)} items to reprocess")
    run_words(failed_words, label=f"Retry {retry_round}")

# 🔹 CSV 최종 저장
c.execute("SELECT word, enriched FROM words ORDER BY idx ASC")
rows = c.fetchall()
with open(output_file, "w", newline="", encoding="utf-8") as outfile:
    writer = csv.writer(outfile)
    writer.writerows(rows)

conn.close()
print("✅ Anki용 CSV 생성 완료 (단어 1개 요청 + Failed 재시도 포함)")
