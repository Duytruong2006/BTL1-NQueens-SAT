# N Queens bằng SAT

Bài tập lớn số 1 môn Các vấn đề hiện đại trong KHMT, học kỳ I năm học 2026–2027.

**Sinh viên:** Nguyễn Duy Trường — 24021650 — CS5.

Repository: https://github.com/Duytruong2006/BTL1-NQueens-SAT

Repository lưu trực tiếp mã nguồn, kết quả thực nghiệm và [báo cáo PDF](report/BTL1_NguyenDuyTruong_24021650.pdf). Bạn có thể tải hoặc clone repository để có đầy đủ cấu trúc thư mục bên dưới. Gói `BTL1_NguyenDuyTruong_24021650.zip` được cung cấp riêng để tiện gửi và nộp, không cần giải nén thêm nếu đã dùng thư mục dự án. Khi nộp qua GitHub, cấp quyền đọc repository cho giảng viên.

## Nội dung

- `src/nqueens_sat.py`: năm mã hóa AMO tự cài đặt, gọi Glucose3 thật qua PySAT, kiểm tra nghiệm và xuất DIMACS CNF.
- `src/comparisons.py`: mô hình CP cho IBM CP Optimizer và OR-Tools CP-SAT; mô hình nhị phân cho CPLEX MIP và Gurobi.
- `tests/`: kiểm thử tính đúng của AMO bằng mọi phép gán nhỏ, kiểm tra SAT/UNSAT và đếm nghiệm N≤8.
- `scripts/benchmark.py`: chạy tuần tự trong tiến trình riêng, giới hạn 30 giây từ khi bắt đầu tạo mô hình đến khi kiểm tra nghiệm.
- `scripts/analyze.py`: tổng hợp dữ liệu thật, tạo bảng và hình dùng trong báo cáo.
- `results/`: nhật ký JSONL có nghiệm, thời gian và trạng thái; CSV, cấu hình và môi trường chạy.
- `report/`: nguồn LaTeX Elsevier CAS, biểu đồ, bảng và báo cáo PDF.
- `notes/source_review.md`: đối chiếu tài liệu và phạm vi trang đã đọc.

## Cài đặt và chạy

Dùng Python 3.12 64 bit. Tạo môi trường riêng, cài các phiên bản trong `requirements.txt`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python src/nqueens_sat.py 8 --encoding product
python src/nqueens_sat.py 8 --encoding binary --cnf examples/n8_binary.cnf
python -m unittest discover -s tests -v
```

Kết quả nghiệm là danh sách cột theo thứ tự hàng, chỉ số bắt đầu từ 0. `verified=true` nghĩa là nghiệm đã được kiểm tra độc lập về hàng, cột và hai đường chéo. `UNSAT` chỉ dùng khi bộ giải kết luận không có nghiệm; hết thời gian không phải UNSAT.

## Tái lập thực nghiệm

```powershell
python scripts/benchmark.py --suite main --limit 30
python scripts/benchmark.py --suite large --limit 30
python scripts/analyze.py
python scripts/build_report.py
```

Trên Windows với đường dẫn dự án có dấu tiếng Việt, nên chạy `powershell -File scripts/run_all.ps1` sau khi kích hoạt môi trường. Script đặt bản giấy phép hạn chế đi kèm gurobipy tại đường dẫn tạm không dấu, giúp thư viện Gurobi đọc được; không thay đổi hay tạo giấy phép. Biến `GRB_LICENSE_FILE` đã có của người dùng được giữ ưu tiên. Không chỉnh sửa nội dung giấy phép.

Nhật ký được chia thành `sat_main`, `comparison_main` và `large` trong bộ kết quả được giao. Những lỗi Gurobi ban đầu do đường dẫn Unicode được giữ trong `results/diagnostics`; bảng báo cáo dùng các lần chạy lại thành công với cùng mô hình và giấy phép. Tập chính có 135 lần chạy, tập mở rộng 27 lần. Để đo mới, dùng `--output` trỏ tới thư mục kết quả mới; nếu giữ thư mục cũ, script sẽ tiếp tục các tác vụ còn thiếu.

Tập chính dùng N=8,16,32,64,128, mỗi phương pháp chạy ba lần. Tập mở rộng dùng N=256,512,1000, mỗi phương pháp một lần. Tất cả chạy tuần tự; thứ tự được trộn với seed 24021650. Bộ giải đối chứng đặt một luồng và seed 42. Mọi solver giải cùng nhiệm vụ tìm một nghiệm trên bàn cờ trống, không thêm ràng buộc phá đối xứng thủ công.

Thời gian `elapsed_seconds` bao gồm tạo mô hình, nạp solver, tìm nghiệm, giải mã và kiểm tra, loại thời gian nạp thư viện. `build_seconds` và `solve_seconds` là các pha bên trong; riêng SAT có `solver_setup_seconds`. Giới hạn ngoài áp dụng cho tổng quá trình. Các timeout là quan sát bị kiểm duyệt (censored observations), không phải số đo bằng đúng 30 giây.

Đặt trần 5.000.000 clause cho pairwise trước khi chạy để tránh sử dụng bộ nhớ quá lớn; các trường hợp vượt trần có trạng thái `SKIPPED_RESOURCE`, không được tính là timeout. Lỗi thư viện, thiếu runtime và giới hạn giấy phép được giữ riêng.

Các bản CPLEX/Gurobi cài qua pip có thể bị giới hạn kích thước mô hình. CP Optimizer được dò tự động từ bản cplex pip mới hoặc thư mục IBM; nếu cần đặt `CPO_EXECUTABLE` tới đúng chương trình. Để mở rộng so sánh ngoài giới hạn bản đi kèm, cần giấy phép phù hợp và chạy lại bằng cùng script. Không thay công cụ bị thiếu bằng công cụ khác.

## Báo cáo và nguồn

Báo cáo dùng `\documentclass[a4paper,fleqn]{cas-sc}`. Các tệp CAS gốc và giấy phép được giữ trong `report/vendor`. Mã hóa và thực nghiệm là cài đặt mới của bộ bài làm; nguồn lý thuyết được dẫn trong báo cáo. Các PDF môn học và báo cáo tham khảo không được đưa lại vào repository.

Để biên dịch, chạy `tectonic main.tex` trong thư mục `report`, hoặc mở project trong Overleaf và chọn XeLaTeX. Bản đã kiểm tra dùng Tectonic 0.17.0. Nhánh XeLaTeX dùng phông TeX Gyre và unicode-math để giữ đúng dấu tiếng Việt và ký hiệu toán, đồng thời tránh nạp bộ phông STIX cũ của CAS; các tệp lớp CAS gốc không bị sửa.

Phạm vi tài liệu đã đọc: `Assignment 1 - requirements.pdf` trang 1/1; `An optimized SAT approach solving N-Queens problem.pdf` trang PDF 1–41; `Mau xay dung bao cao BTL so 1 và BTL so 2.pdf` trang PDF 1–32; Module3 trang 1–17; Module2 trang 1–27. Số liệu của báo cáo tham khảo không được dùng như kết quả thực nghiệm của bộ bài làm này.

Repository được tạo riêng tư. Khi nộp, chủ repository cần cấp quyền đọc cho giảng viên để truy cập đường dẫn trong Data Availability.
