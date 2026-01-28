# ENVI Auto Fill Fields - Anki Addon

**Phiên bản:** 1.0.0  
**Tác giả:** Nguyễn Văn Phán

## Mô tả

Addon tự động điền thông tin từ vựng tiếng Anh vào các trường dữ liệu của thẻ Anki. Sử dụng API từ en.jpdictionary.com để tra cứu và lấy thông tin chi tiết về từ vựng.

## Tính năng

### 1. Menu Tools - ENVI Auto Fill
- **Lookup**: Tra cứu từ vựng đơn thuần (giống addon cũ)
- **Settings**: Cấu hình addon
- **About**: Thông tin về addon

### 2. Cấu hình (Settings)
- Chọn Note Type mặc định
- Chọn trường chứa từ vựng cần tra (Word Field)
- Mapping các trường dữ liệu:
  - Definition (Định nghĩa)
  - Pronunciation (Phát âm IPA)
  - Part of Speech (Loại từ)
  - Meanings (Nghĩa tiếng Việt)
  - Examples (Ví dụ)
- Bật/tắt addon
- Cài đặt ghi đè dữ liệu cũ

### 3. Chế độ Review (Học thẻ)
- Tự động kiểm tra và điền dữ liệu khi hiển thị thẻ
- Chỉ xử lý thẻ có Note Type trùng với cấu hình
- Tự động tra cứu từ Word Field và điền vào các trường khác

### 4. Chế độ Browser
- Menu Edit → "ENVI Auto Fill - Process Cards"
- Chọn 1 hoặc nhiều thẻ
- Xử lý hàng loạt với progress bar
- Hiển thị kết quả và lỗi chi tiết

## Cài đặt

1. Tải file addon (.ankiaddon hoặc .zip)
2. Mở Anki → Tools → Add-ons → Install from file
3. Chọn file vừa tải
4. Khởi động lại Anki

## Hướng dẫn sử dụng

### Bước 1: Cấu hình
1. Mở Anki → Tools → ENVI Auto Fill → Settings
2. Chọn Note Type bạn muốn sử dụng
3. Chọn trường chứa từ vựng (Word Field)
4. Mapping các trường khác (Definition, Pronunciation, v.v.)
5. Click Save

### Bước 2: Sử dụng
**Trong Review:**
- Addon tự động hoạt động khi bạn học thẻ
- Không cần làm gì thêm

**Trong Browser:**
1. Chọn các thẻ cần xử lý
2. Edit → "ENVI Auto Fill - Process Cards"
3. Đợi xử lý hoàn tất

## Lưu ý
- Addon chỉ xử lý thẻ có Note Type trùng với cấu hình
- Nếu chưa cấu hình, addon sẽ yêu cầu cài đặt
- Khi tắt addon, các tính năng tự động sẽ không hoạt động
- API có thể giới hạn số lượng request, nên xử lý từng nhóm nhỏ

## Cấu trúc dữ liệu
- **Definition**: Định nghĩa chi tiết của từ
- **Pronunciation**: Phát âm IPA (ví dụ: /wɜːd/)
- **POS**: Loại từ (noun, verb, adjective, v.v.)
- **Meanings**: Nghĩa tiếng Việt, mỗi nghĩa một dòng
- **Examples**: Ví dụ sử dụng, mỗi ví dụ gồm câu tiếng Anh và nghĩa tiếng Việt

## Hỗ trợ
Nếu gặp lỗi, vui lòng kiểm tra:
1. Kết nối internet
2. Cấu hình Note Type và Field Mapping
3. Log lỗi trong Anki (Tools → Add-ons → View Files → debug.log)

## Changelog

### Version 1.0.0 (2026-01-28)
- Phiên bản đầu tiên
- Tự động điền dữ liệu trong review và browser
- Cấu hình linh hoạt
- Progress tracking
- Error logging
