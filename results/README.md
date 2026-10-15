# Kết quả thực nghiệm

Các bảng trong báo cáo dùng 162 lần chạy chính thức: 75 lần SAT ở tập chính, 60 lần đối chứng ở tập chính và 27 lần ở tập mở rộng. Có 117 lần SAT được kiểm tra lại về hình học, 24 lần vượt giới hạn giấy phép, 18 lần hết hạn và 3 trường hợp pairwise bỏ qua theo trần 5.000.000 clause đã định trước.

- `sat_main/raw.jsonl`: 5 mã hóa SAT, N=8,16,32,64,128; 3 lần/cấu hình.
- `comparison_main/raw.jsonl`: CP-SAT, CPLEX MIP, Gurobi, CP Optimizer; cùng kích thước và 3 lần/cấu hình.
- `large/raw.jsonl`: N=256,512,1000; một lần/cấu hình cho cả 9 phương pháp.
- `environment.json`: môi trường chung, phiên bản và tài nguyên đã đọc từ máy.
- `summary.csv`: trung vị, nhỏ nhất, lớn nhất, số lần thành công và trạng thái; mỗi nhóm dùng đúng dữ liệu JSONL.
- `analysis.json`: cấu hình tổng hợp, phạm vi tệp và số dòng đọc, số đếm CNF, nghiệm minh họa cùng các phép tính dùng trong báo cáo.
- `diagnostics/`: lỗi khởi tạo Gurobi do đường dẫn có dấu trước khi sửa đường dẫn giấy phép; không được tính là lần giải chính thức. Nội dung giấy phép không nằm trong bộ dữ liệu.

`elapsed_seconds` đo toàn bộ lời gọi giải sau khi nạp thư viện. `TIMEOUT` không có thời gian giải hoàn thành và không được thay bằng đúng 30 khi tính trung vị. `LICENSE_LIMIT` và `SKIPPED_RESOURCE` không phải kết luận UNSAT.

Các kết quả thuộc một máy và các cấu hình công bố trong báo cáo. Chúng không đại diện cho mọi cấu hình solver, mọi phần cứng hoặc các biến thể N-Queens có hậu đặt sẵn.
