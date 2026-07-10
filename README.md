# PageForge — AI Landing Page Generator

Ứng dụng web cho phép nhập một câu **prompt mô tả** và nhận về **một landing
page HTML hoàn chỉnh**, đẹp, responsive, sẵn sàng dùng — nhờ gọi GPT API
(OpenAI).

- **Backend:** Flask (Python) — gọi OpenAI Chat Completions API
- **Frontend:** HTML + Bootstrap 5 (khung UI) + CSS/JS thuần (không build step)
- **Kết quả sinh ra:** 1 file HTML độc lập, dùng Tailwind CDN, Google Fonts,
  responsive, có thể tải về và deploy ngay lên bất kỳ hosting tĩnh nào.

## 1. Cài đặt

```bash
cd landing-generator
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## 2. Cấu hình API key

```bash
cp .env.example .env
```

Mở `.env` và điền API key OpenAI của bạn:

```
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
OPENAI_MODEL=gpt-4o-mini    # hoặc gpt-4o, gpt-4-turbo... tuỳ nhu cầu chất lượng/chi phí
```

> Lấy API key tại: https://platform.openai.com/api-keys

## 3. Chạy ứng dụng

```bash
python app.py
```

Mở trình duyệt tại **http://127.0.0.1:5000**

## 4. Cách dùng

1. Nhập mô tả landing page bạn muốn (càng chi tiết càng tốt: đối tượng khách
   hàng, ngành nghề, tông giọng, phần nội dung cần có...).
2. (Tuỳ chọn) chọn lĩnh vực, ngôn ngữ, phong cách thiết kế, tông màu, CTA chính.
3. Nhấn **"Tạo landing page"** — AI sẽ trả về trang HTML hoàn chỉnh, hiển thị
   ngay trong khung xem trước (có thể chuyển đổi Desktop/Tablet/Mobile).
4. Dùng thanh công cụ để:
   - **Xem trước / Mã HTML** — chuyển giữa preview trực quan và mã nguồn
   - **Sao chép** — copy toàn bộ HTML vào clipboard
   - **Mở tab mới** — xem trang ở tab trình duyệt riêng
   - **Tải xuống** — lưu file `landing-page.html` về máy, dùng/host ngay

## 5. Cấu trúc dự án

```
landing-generator/
├── app.py                  # Flask backend + logic gọi OpenAI + prompt engineering
├── requirements.txt
├── .env.example
├── templates/
│   └── index.html          # Giao diện chính (Bootstrap + custom design)
└── static/
    ├── css/style.css       # Design system riêng cho tool (dark UI)
    └── js/main.js           # Xử lý form, gọi API, preview, tải file
```

## 6. Ghi chú kỹ thuật & tuỳ biến

- **Chất lượng đầu ra** phụ thuộc phần lớn vào `SYSTEM_PROMPT` trong `app.py`.
  Bạn có thể chỉnh sửa prompt này để ép AI tuân theo bộ quy tắc thiết kế/khung
  section riêng của bạn.
- **Model:** mặc định `gpt-4o-mini` (nhanh, rẻ). Nếu cần chất lượng thiết kế/
  copywriting cao hơn, đổi `OPENAI_MODEL=gpt-4o` trong `.env`.
- **Rate limit demo:** có giới hạn 8 giây/lần gọi trên mỗi IP (biến
  `MIN_INTERVAL_SECONDS` trong `app.py`) để tránh spam — chỉnh hoặc thay bằng
  giải pháp rate-limit thực sự (Redis, Flask-Limiter...) khi triển khai
  production.
- **Bảo mật API key:** key chỉ nằm ở server (biến môi trường), không bao giờ
  lộ ra frontend.
- **Triển khai production:** dùng `gunicorn` (đã có trong requirements):
  ```bash
  gunicorn -w 2 -b 0.0.0.0:8000 app:app
  ```
  Nhớ đặt `OPENAI_API_KEY` làm biến môi trường thực (không dùng `debug=True`).
- **Mở rộng thêm:**
  - Lưu lịch sử các trang đã tạo (DB/SQLite) để người dùng xem lại
  - Cho phép "chỉnh sửa tiếp" bằng cách gửi kèm HTML cũ + yêu cầu chỉnh sửa
  - Streaming response để hiển thị code ngay khi AI đang sinh (Server-Sent
    Events / `stream=True` của OpenAI)
  - Xuất thêm định dạng React/Next.js nếu cần tích hợp vào codebase có sẵn

## 7. Giới hạn hiện tại

- Đây là bản demo/MVP: rate limiting là in-memory (mất khi restart server),
  chưa có xác thực người dùng, chưa lưu trữ lịch sử.
- Nội dung do AI sinh ra (testimonial, số liệu, logo khách hàng...) là hư cấu
  minh hoạ — cần thay bằng nội dung thật trước khi dùng cho khách hàng thật.
- Ảnh minh hoạ trong landing page (nếu có) dùng nguồn từ Unsplash — kiểm tra
  lại giấy phép/quyền sử dụng trước khi dùng thương mại.