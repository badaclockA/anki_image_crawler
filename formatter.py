import csv

# 파일 경로 (수정해서 사용하세요)
answers_file = "답안지.csv"   # 암기고래 답안지
questions_file = "문제지.csv"  # 암기고래 시험지
output_file = "anki_deck.csv"  # Anki용 최종 CSV

# 1. 답안지 로드
answers = {}
with open(answers_file, encoding="utf-8") as f:
    for line in f:
        line = line.strip().strip('"')
        if not line:
            continue
        if "." in line:  # "1. n. 관객, 구경꾼" 같은 형식
            num, text = line.split(".", 1)
            num = num.strip()
            text = text.strip()
            answers[num] = text

# 2. 시험지 로드 + 매칭
with open(questions_file, encoding="utf-8") as f, open(output_file, "w", newline="", encoding="utf-8") as out:
    reader = csv.reader(f)
    writer = csv.writer(out)

    for row in reader:
        word = row[0].strip()
        if word and word[0].isdigit() and "." in word:  
            # "1. spectator," 같은 줄 처리
            num, word_part = word.split(".", 1)
            num = num.strip()
            word_clean = word_part.strip().strip(",")
            meaning = answers.get(num, "")
            if word_clean:
                writer.writerow([word_clean, meaning])

print("✅ anki_deck.csv 파일 생성 완료!")
