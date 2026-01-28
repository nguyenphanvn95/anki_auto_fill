# ENVI Auto Fill Fields – Custom Version

## 1. Giới thiệu
**ENVI Auto Fill Fields** là addon mở rộng cho Anki giúp:
- Tra cứu từ vựng tiếng Anh (nguồn ENVI)
- Tự động điền dữ liệu vào các field của note type
- Phù hợp cho học từ vựng, IELTS, active recall, cloze, điền từ

Phiên bản này là **bản custom nâng cấp**, được chỉnh sửa để:
- Lưu config ổn định
- Tương thích Anki 25+ (Python 3.13, Qt6)
- Ghi dữ liệu chính xác, format đẹp (HTML `<br>`)
- Không lỗi mapping field

---

## 2. Yêu cầu hệ thống
- Anki **25.0 trở lên**
- Python: 3.9+ (Anki 25.02+ dùng 3.13)
- Hệ điều hành: Windows / macOS / Linux
- Không yêu cầu AnkiConnect

---

## 3. Cấu trúc dữ liệu ENVI (Raw JSON)

```json
{
  "word": "speech",
  "pron": "spiːtʃ",
  "pos": "danh từ",
  "def": "Speech có nghĩa là khả năng nói hoặc một bài phát biểu.",
  "mean": [
    {
      "m": "bài phát biểu",
      "e": "Her [speech] at the wedding was very touching.",
      "v": "Bài [phát biểu] của cô ấy tại đám cưới rất cảm động."
    },
    {
      "m": "khả năng nói",
      "e": "He has a talent for [speech] and public speaking.",
      "v": "Anh ấy có tài năng về [khả năng nói] và diễn thuyết."
    }
  ]
}
```

---

## 4. Mapping dữ liệu → Anki Fields

| Trường Anki | Dữ liệu |
|------------|--------|
| Vocab | word |
| IPA | pron |
| Part of speech | pos |
| Definition_VI | mean[].m |
| Example | mean[].e + mean[].v |
| Sources | def |

### Format chuẩn
- **Definition_VI**: mỗi nghĩa 1 dòng (`<br>`)
- **Example**:
  - EN
  - `<br>`
  - VI
  - `<br><br>` giữa các ví dụ

---

## 5. Cài đặt addon

### Cách 1: Chép đè thủ công (khuyến nghị)
1. Anki → Tools → Add-ons → chọn addon → **View Files**
2. Chép thư mục `anki_auto_fill_addon/` vào `addons21/`
3. Restart Anki

---

## 6. Thiết lập (Settings)

Vào:
```
Tools → ENVI Auto Fill → Settings
```

### Các tuỳ chọn:
- ☑ Enable Auto Fill
- ☑ Overwrite existing data
- ☑ Show POS tags in meanings (tuỳ chọn)

### Mapping:
- Word Field: `Vocab`
- Pronunciation Field: `IPA`
- Part of Speech Field: `Part of speech`
- Meanings Field: `Definition_VI`
- Examples Field: `Example`
- Sources Field: `Sources`

Bấm **Save** → config được lưu ngay.

---

## 7. Cách sử dụng

### Tự động điền:
1. Mở Browser
2. Chọn các note có field Vocab
3. Menu → ENVI Auto Fill → Process Cards

### Khi review:
- Addon sẽ tự fill các field còn trống
- Không ghi đè nếu bạn bỏ chọn Overwrite

---

## 8. Fix & nâng cấp quan trọng

### ✔ api.py
- Chuẩn hoá meanings, examples
- Xuất nhiều key tương thích:
  - IPA: `pronunciation`, `ipa`, `IPA`
  - POS: `pos`, `part_of_speech`
  - Sources: `def`, `definition`, `sources`

### ✔ processor.py
- Fallback alias khi đọc field
- Không phụ thuộc key cứng
- Không mất dữ liệu khi đổi mapping

---

## 9. Lỗi thường gặp

### ❌ Không thấy IPA / Sources
✔ Đã fix bằng alias key
✔ Kiểm tra mapping trong Settings

### ❌ Báo "Please configure addon"
✔ Đã fix lưu config theo addon ID
✔ Restart Anki sau khi Save

---

## 10. Gợi ý nâng cấp thêm
- Tách Example_EN / Example_VI
- Highlight từ vựng trong ví dụ
- Tuỳ chọn phân cách nghĩa: dòng / dấu phẩy
- Cloze + active recall template

---

## 11. Tác giả & ghi chú
- Custom & debug: theo workflow học thực tế
- Mục tiêu: **đúng dữ liệu – đẹp trình bày – học hiệu quả**
