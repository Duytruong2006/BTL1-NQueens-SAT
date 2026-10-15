# Rà soát nguồn và cơ sở phương pháp cho Bài tập lớn số 1

## 1. Phạm vi đã đọc

Đã đọc toàn bộ **phần văn bản trích xuất theo trang PDF** của năm tài liệu sau. Số trang dưới đây là số trang vật lý trong PDF, tính trang bìa là trang 1; chúng có thể lệch một trang so với số in ở chân trang. Các hình được đọc qua nhãn và chú thích có trong bản trích; ghi chú này không tái dựng số liệu từ đường cong trong hình và không thay thế việc kiểm tra trực quan bản PDF báo cáo cuối cùng.

| Tệp gốc | Phạm vi đọc | Mục đích sử dụng |
|---|---|---|
| `Assignment 1 - requirements.pdf` | Trang 1/1, toàn bộ yêu cầu | Tiêu chí phải đáp ứng, cách nộp báo cáo và dữ liệu |
| `An optimized SAT approach solving N-Queens problem.pdf` | Trang 1–41/41, toàn bộ văn bản, bảng và tài liệu tham khảo | Bài tham khảo về N-Queens, năm mã hóa AMO và thiết kế thực nghiệm; cần sửa các lỗi công thức được liệt kê bên dưới |
| `Mau xay dung bao cao BTL so 1 và BTL so 2.pdf` | Trang 1–32/32, toàn bộ văn bản, bảng và tài liệu tham khảo | Tham khảo cấu trúc một bài báo khoa học, cách phân biệt kết quả tự chạy và kết quả công bố |
| `Module3_AMO ALO Encoding.pdf` | Trang 1–17/17, toàn bộ slide | Định nghĩa AMO/ALO và pairwise, binary, sequential, commander, product |
| `Module2_SAT Encoding.pdf` | Trang 1–27/27, toàn bộ slide | Kiến thức CNF, biến phụ, tính đồng khả thỏa và quy trình SAT encoding |

Các nhận xét dưới đây là đối chiếu và suy luận toán học từ nguồn được cung cấp. Chưa kiểm chứng các tài liệu được những nguồn này dẫn tới nếu bản gốc của chúng không nằm trong phạm vi đọc trên.

## 2. Yêu cầu bắt buộc và nội dung được khuyến khích

**Phạm vi nguồn cho mục này:** `Assignment 1 - requirements.pdf`, trang 1/1.

1. Sinh viên làm **cá nhân** và chọn một trong hai đề tài: Sudoku hoặc N-Queens. Với yêu cầu hiện tại, chọn N-Queens là phù hợp.
2. Phải **lập trình solver**, không chỉ viết khảo sát lý thuyết. Hướng chính là SAT solving; đề bài cho phép PySAT hoặc gọi SAT solver trực tiếp. CaDiCaL, Glucose, Kissat và CryptoMiniSAT là các ví dụ được nêu, không phải yêu cầu phải dùng toàn bộ.
3. Phải triển khai **thực nghiệm đánh giá**, trong đó so sánh SAT với các phương pháp chính xác khác như ILP và CP. Câu yêu cầu nêu cụ thể **CPLEX CP, CPLEX MIP, Gurobi, CP-SAT**. Vì vậy, chỉ chạy CP-SAT hoặc một ILP thay thế thì chưa thể tuyên bố đã đáp ứng trọn vẹn dòng yêu cầu này. Nếu môi trường thiếu thư viện, bộ thực thi hoặc giấy phép, phải ghi đúng trạng thái, giao bộ chuyển tiếp có thể chạy lại, và chỉ rõ phần so sánh còn thiếu.
4. Báo cáo có dạng **bài báo khoa học**, tham khảo tệp mẫu và lớp LaTeX Elsevier `\documentclass[a4paper,fleqn]{cas-sc}`. Không nên chỉ giao báo cáo dạng luận văn 5 chương giống bài tham khảo cũ nếu chưa đáp ứng định dạng mới.
5. Kết quả thực nghiệm cần có **ma trận kích thước lớn**. Đề không ấn định mốc N cụ thể; nên xác định bộ kích thước và giới hạn tài nguyên trước khi chạy, ghi minh bạch cỡ lớn nhất đã chạy được và các trường hợp timeout.
6. Phải ghi **đường dẫn repository chứa mã nguồn và kết quả thực nghiệm** trong mục **Data Availability**. Một đường dẫn giả hoặc placeholder không đáp ứng yêu cầu. Có thể chuẩn bị gói nộp và repository cục bộ, nhưng chỉ ghi URL công khai sau khi có URL thực và được phép xuất bản.
7. **Khuyến khích**, không bắt buộc từng phương án riêng lẻ: các mã hóa binary, commander, product, sequential counter; bố cục do sinh viên tự thiết kế để thể hiện kết quả.

Nên có bảng đối chiếu yêu cầu trong README hoặc phụ lục. Trạng thái `NOT_AVAILABLE`, `LICENSE_LIMIT`, `TIMEOUT`, `SAT`, `UNSAT` phải tách biệt; không quy tất cả vào timeout và không điền số liệu mượn để lấp chỗ trống.

## 3. Bố cục phù hợp với mẫu

**Phạm vi nguồn cho mục này:** tệp mẫu trang 1–32/32; đặc biệt trang 2–5 về mở đầu/nền tảng, trang 5–10 về phương pháp, trang 10–19 về thực nghiệm, trang 19–20 về kết luận và công bố dữ liệu, trang 20–30 về phụ lục, trang 31 về tài liệu tham khảo.

Tệp “mẫu” là một bản thảo bài báo về **Two-Dimensional Bandwidth Minimization Problem (2DBMP)**, không phải một bộ yêu cầu N-Queens và không phải mẫu trống để điền số. Không chuyển mô hình 2DBMP, các bảng benchmark hoặc kết quả tối ưu của nó sang bài N-Queens.

Cấu trúc đề xuất cho báo cáo N-Queens:

1. Tiêu đề; tác giả/sinh viên; đơn vị; mã sinh viên và lớp chỉ điền từ thông tin thật.
2. **Tóm tắt (Abstract)**: bài toán, phương pháp, phạm vi thực nghiệm, kết quả định lượng được tự chạy và giới hạn.
3. Từ khóa (Keywords).
4. Giới thiệu (Introduction): động cơ, phạm vi “tìm một nghiệm”, các câu hỏi thực nghiệm và đóng góp ở mức BTL.
5. Cơ sở và công trình liên quan (Background and Related Work): N-Queens, SAT/CNF/AMO/ALO, mô hình CP và ILP, phạm vi kế thừa bài tham khảo.
6. Phương pháp (Methodology): biến, ràng buộc, năm mã hóa, chứng minh tính đúng, cách giải mã, kiểm tra nghiệm và các mô hình đối chứng.
7. Thực nghiệm (Experiments): máy chạy, phiên bản, dữ liệu, timeout, số lần lặp, chỉ số, kết quả và thảo luận.
8. Kết luận (Conclusion): trả lời câu hỏi thực nghiệm trong phạm vi dữ liệu, hạn chế và hướng mở rộng.
9. Data Availability: repository thực chứa mã và dữ liệu thô; mô tả cách tái lập.
10. Phụ lục: công thức đếm, mã giả, kiểm chứng, kết quả chi tiết và trạng thái công cụ.
11. Tài liệu tham khảo.

Trong mẫu có CRediT, tuyên bố xung đột lợi ích và tuyên bố dùng AI. Không sao chép tên tác giả hay tuyên bố trách nhiệm của người khác. Nếu dùng mục AI, phải phản ánh đúng việc AI tham gia tạo mã, rà soát và hỗ trợ soạn báo cáo; không chỉ viết “sửa ngôn ngữ” nếu thực tế dùng rộng hơn.

## 4. Những điểm trong bài N-Queens phải sửa trước khi dùng

**Phạm vi nguồn cho mục này:** `An optimized SAT approach solving N-Queens problem.pdf`, toàn bộ 41 trang, với vị trí chi tiết ở bảng dưới. Đây là nhận xét về phần trình bày trong nguồn, không phải kết luận rằng mã nguồn thực nghiệm của tác giả có cùng lỗi; bản trích không chứa mã nguồn đó.

| Vị trí trang PDF | Vấn đề | Cách viết đúng |
|---|---|---|
| 15–16, ví dụ dưới (1.2), (1.4); lặp lại ở 29, 32–33 | Công thức tổng quát ALO từng hàng/cột đúng, nhưng ví dụ nối tất cả ô thành **một OR toàn bàn**. Điều đó chỉ yêu cầu ít nhất một hậu trên bàn | Mỗi hàng/cột phải có một clause riêng, sau đó AND các clause: `AND_r OR_c x[r,c]` và `AND_c OR_r x[r,c]` |
| 16, (1.5), (1.6); 29–30, (3.5), (3.6) | Miền chỉ số dùng `<= n` dù chỉ số ô là `0..n-1`. Đường chéo phụ dùng cùng lúc `i<i'`, `j<j'` nhưng `i+j=i'+j'`, là điều không thể | Dùng tập nhóm theo `r-c=d`, `r+c=s`; tạo AMO trên từng nhóm. Nếu viết theo cặp, dùng `0<=r<r'<n` và `abs(c-c')=r'-r` |
| 18, mục Negation | Bảng cho “phủ định” lại mang hai biến và nhãn kéo theo | `A, NOT A` có hai dòng: `T,F` và `F,T` |
| 19, bảng kéo theo | Dòng `F,F` của `A -> B` bị ghi `F` | `A -> B` tương đương `NOT A OR B`, nên dòng `F,F` phải là `T` |
| 20 | Viết SAT “requiring algorithms with exponential worst-case complexity” dễ bị hiểu là đã chứng minh cận dưới lũy thừa cho mọi thuật toán | Chỉ viết SAT là NP-complete; chưa biết thuật toán đa thức cho trường hợp tổng quát. Không suy từ NP-complete ra cận dưới thời gian lũy thừa đã chứng minh |
| 22, mô tả binary | Dùng dấu tương đương `Xi <-> code(i)` trong phần ý tưởng, còn clauses thực chỉ thể hiện `Xi -> code(i)` | Với AMO dùng một chiều là đủ. Nếu ép hai chiều trên mọi mã khi số biến là lũy thừa của 2, có thể vô tình buộc ALO, không còn là AMO thuần |
| 24, công thức pairwise trong commander | Cận chỉ số trong nhóm dùng `q=i+1` trong khi cặp là `p,q` | Dùng mọi cặp `p<q` trong cùng nhóm |
| 26, ví dụ product với 8 biến | `X1 -> r1` bị lặp thay vì có `X1 -> c1`; `X8 -> c3` không khớp ô trong lưới được vẽ | Mỗi biến ô phải có đủ hai liên kết đến đúng hàng và cột phụ. Với lưới hiển thị, `X8 -> c2` |
| 26, cách ALO (ii) của product | Chỉ ALO trên hai tập selector và các liên kết ngược ở ô có thật chưa đủ khi lưới có ô trống | Dùng trực tiếp `X1 OR ... OR Xm` khi cần ALO; nếu dùng selector ALO thì phải cấm chọn ô trống hoặc có mô hình bảo đảm tương ứng đầy đủ |
| 27, mục 3.2 | Viết “exactly one queen in each row, column, and diagonal” | Đúng một ở mỗi hàng/cột, **nhiều nhất một** ở mỗi đường chéo. Không đặt ALO trên đường chéo |
| 28–30, biến binary | Ký hiệu `Y0,Y1` được dùng lại trong ví dụ hàng, cột, đường chéo; nếu hiểu là cùng biến sẽ nối các nhóm không liên quan | Mỗi lần gọi AMO có tập biến phụ riêng; dùng bộ cấp phát ID chung để tránh đụng ID với biến bàn cờ và nhóm khác |
| 31, ví dụ commander | Dòng cuối dùng `NOT c1 -> NOT B02/B03` cho nhóm 2 | Nhóm 2 phải dùng `NOT c2 -> NOT B02/B03`, tương đương `B02/B03 -> c2` |
| 32, (3.7), (3.9) | Dấu của biến ô ở clause cuối bị dương; các vòng trung gian chạy tới vị trí cuối gây sai số lượng biến phụ; chỉ số `Sj`, `Si` không nhất quán | Dùng công thức Sinz chuẩn ở mục 6 bên dưới, kết thúc bằng `NOT s[m-1] OR NOT x[m]` |
| 32, ví dụ sequential | Ví dụ dưới công thức lại là các clauses pairwise | Thay bằng đúng clauses liên kết `x` với `s`, không gọi một công thức pairwise là sequential |
| 33, ví dụ đường chéo phụ | Kết thúc bằng `S2 -> B11` | Phải là `S2 -> NOT B11` |
| 34, ví dụ product | Selector AMO đánh chỉ số 1,2 nhưng liên kết dùng 0,1; dòng cuối dùng `B01 -> c1` thay vì `B03 -> c1` | Dùng cùng một quy ước chỉ số và liên kết đúng cả hai selector cho mọi biến |
| 36, môi trường và bảng 4.2 | Timeout được ghi 100 giây nhưng một số thời gian lớn hơn 100, ví dụ 129.0981 giây | Không suy diễn nguyên nhân. Báo cáo mới phải định nghĩa timeout áp dụng cho solver hay tổng quy trình, và tách các loại thời gian |
| 37–39, phân tích/kết luận | Một số nhận xét khái quát vượt dữ liệu; ví dụ “timeout từ n>=125 ở phần lớn phương pháp” không phù hợp trực tiếp hàng n=125 trong bảng | Chỉ kết luận theo dữ liệu đã đo, cấu hình đã chạy. Không khẳng định product luôn tốt nhất hoặc ít clause luôn giải nhanh hơn |
| 40–41, danh mục tham khảo | Tài liệu [15] được dẫn sau “MiniSat” nhưng mục [15] là bài về Chaff | Không sao chép trích dẫn máy móc; dùng đúng bài/phần mềm đã thực sự đọc và chạy |

Các lỗi sao chép nhỏ ở Module3 cũng cần tránh: slide 9 có nhãn `X4` ở dòng nói về `X5`; slide 13 lặp cặp `X4,X5` thay vì đủ các cặp của nhóm; slide 16 ví dụ n=6 vẫn ghi sqrt(5) và 5/3. Các lỗi đó không thay đổi ý tưởng mã hóa nhưng không nên xuất hiện trong báo cáo mới.

## 5. Mô hình N-Queens nhất quán

**Phạm vi nguồn:** bài N-Queens trang 10–16 và 27–34; Module3 trang 3–16. Các công thức dưới đây được viết lại và kiểm tra bằng lập luận độc lập.

Đặt `x[r,c]` là biến Boolean cho ô hàng `r`, cột `c`, với `0 <= r,c < N`. Mã DIMACS an toàn là `id(r,c)=r*N+c+1`; ID biến phụ bắt đầu sau `N*N`.

Định nghĩa các tập:

- `R[r] = {x[r,c] : 0 <= c < N}`.
- `C[c] = {x[r,c] : 0 <= r < N}`.
- `Dminus[d] = {x[r,c] : r-c=d}`, với `1-N <= d <= N-1`.
- `Dplus[s] = {x[r,c] : r+c=s}`, với `0 <= s <= 2N-2`.

`ALO(X)` là một clause chứa OR của mọi phần tử X. `AMO(X)` buộc tối đa một phần tử X đúng. `EXO(X)=ALO(X) AND AMO(X)`.

Mô hình đầy đủ dễ kiểm chứng:

```
F = AND_r EXO(R[r])
    AND_c EXO(C[c])
    AND_d AMO(Dminus[d])
    AND_s AMO(Dplus[s]).
```

Nhóm đường chéo có 0 hoặc 1 phần tử không cần AMO clause. **Không có ALO trên đường chéo.**

Lập luận tính đúng gồm hai chiều:

1. Từ mô hình SAT: EXO hàng tạo đúng N hậu; EXO cột và AMO đường chéo loại mọi cặp tấn công. Giải mã chỉ dùng biến bàn cờ có ID từ 1 đến N²; bỏ qua biến phụ.
2. Từ lời giải N-Queens: đặt các biến ô được chọn là True. Mỗi nhóm thỏa AMO/ALO tương ứng, do đó có thể gán biến phụ của từng mã hóa độc lập để thỏa toàn bộ CNF.

Thuật ngữ đúng là **đồng khả thỏa sau khi lượng hóa tồn tại biến phụ (equisatisfiable under existential projection)**: `AMO(X)` tương đương `exists Y: Enc(X,Y)`. Không nói các biến phụ bắt buộc có ngữ nghĩa tương đương hai chiều nếu clauses chỉ ràng buộc một chiều.

ALO cột là dư thừa khi đã có EXO hàng và AMO cột: N hậu vào N cột, mỗi cột tối đa một, suy ra mỗi cột đúng một. Có thể bỏ nó trong một biến thể tối ưu, nhưng phải nói rõ và không dùng công thức đếm của mô hình đầy đủ. So sánh năm encoding nên giữ cùng mô hình cấu trúc để cô lập ảnh hưởng của encoding.

Mô hình đối chứng ILP/MIP: biến nhị phân `x[r,c]`, tổng từng hàng và cột bằng 1, tổng từng đường chéo không quá 1; dùng bài toán khả thi với mục tiêu hằng 0. Mô hình CP/CP-SAT gọn: biến nguyên `q[r]` là cột của hậu ở hàng r, miền `0..N-1`; `AllDifferent(q)`, `AllDifferent(q[r]+r)`, `AllDifferent(q[r]-r)`. Nếu CP-SAT cần biến trung gian cho biểu thức thì lập đẳng thức rõ ràng. Đây là bài tìm một nghiệm, không cần tối ưu một mục tiêu giả.

## 6. Các mã hóa AMO chuẩn và cách đếm

**Phạm vi nguồn:** Module3 trang 4–16; bài N-Queens trang 21–26. Công thức tổng kích thước bàn cờ ở mục 7 là suy ra độc lập, không lấy từ biểu đồ nguồn.

Cho nhóm `X=(x1,...,xm)`, với `m>=2`. Biến phụ của mọi nhóm phải khác nhau.

### Pairwise / binomial

Thêm `(NOT xi OR NOT xj)` cho mọi `1<=i<j<=m`.

- Biến phụ: 0.
- Clauses: `m*(m-1)/2`.

### Binary

Đặt `k=ceil(log2(m))`, cấp `k` biến phụ `b1,...,bk`, gán mỗi `xi` một mã nhị phân riêng. Với mỗi bit, thêm `(NOT xi OR literal(code(i),j))`.

- Biến phụ: `k`.
- Clauses của phiên bản trực tiếp: `m*k`.
- Hai biến cùng True đòi selector có hai mã khác nhau nên mâu thuẫn. Khi tất cả xi=False, selector có thể tùy ý; AMO được giữ đúng.
- ALO, nếu cần, là một clause riêng trên X.

### Sequential counter của Sinz, phiên bản trực tiếp

Cấp `s1,...,s[m-1]`:

```
(NOT x1 OR s1)
for i=2,...,m-1:
    (NOT xi OR si)
    (NOT s[i-1] OR si)
    (NOT xi OR NOT s[i-1])
(NOT xm OR NOT s[m-1])
```

- Biến phụ: `m-1`.
- Clauses: `3m-4`.
- Nếu xi đúng thì si đúng và trạng thái đúng truyền về sau; mọi xj sau đó bị cấm. Ngược lại, với tối đa một xi đúng, chọn si bằng OR của tiền tố `x1..xi` sẽ thỏa clauses.
- Không diễn giải clauses này là buộc `si <-> OR(x1..xi)` cho mọi mô hình: chiều ngược không được mã hóa đầy đủ, nhưng không cần cho tính đúng dưới phép chiếu.
- PySAT hoặc code có thể dùng trường hợp đặc biệt cho nhóm 2–3 phần tử; khi đó số clauses/biến đo được có thể khác công thức trực tiếp trên. Phải ghi rõ số đếm lý thuyết áp dụng cho phiên bản nào và so với số đếm thực trong chương trình.

### Commander

Chia X thành các nhóm con, mỗi nhóm có commander `ci`:

- AMO nội bộ từng nhóm.
- Với mọi x thuộc nhóm i, thêm `(NOT x OR ci)`.
- AMO trên các commander.
- Có thể thêm `(NOT ci OR OR_{x in Gi} x)` để commander phản ánh sự tồn tại một biến đúng; clause này không bắt buộc cho AMO dưới phép chiếu.
- Tuyệt đối không thêm ALO trên commander khi nhóm gốc chỉ có AMO (như đường chéo), nếu không sẽ buộc ít nhất một hậu trên nhóm đó.

Một mức với số nhóm khoảng sqrt(m), AMO pairwise ở cả nhóm con và commander, có số clauses cỡ `Theta(m^(3/2))`, **không tự động là O(m)**. Phiên bản nhóm con có kích thước hằng, ví dụ 3, và **đệ quy AMO trên commander** có số biến phụ và clauses O(m). Báo cáo phải nói rõ biến thể và kích thước nhóm được cài.

### Product, hai chiều, một mức

Đặt `p=ceil(sqrt(m))`, `q=ceil(m/p)`. Gán mỗi xi vào một ô riêng `(u,v)` của lưới p×q. Cấp selector `r1..rp,c1..cq`:

- Pairwise AMO trên các r và trên các c.
- Với mỗi xi tại (u,v), thêm `(NOT xi OR ru)` và `(NOT xi OR cv)`.

Số biến phụ `p+q`, số clauses `2m + C(p,2)+C(q,2)`. Hai xi khác nhau khác hàng hoặc cột selector, nên không thể đồng thời True. Cả nhóm False luôn có mở rộng bằng tất cả selector False. Nếu cần EXO thì thêm ALO trực tiếp trên X. Product cân bằng có O(m) clauses và O(sqrt(m)) biến phụ mỗi nhóm; tối ưu về kích thước không bảo đảm tối ưu thời gian giải.

## 7. Công thức tổng cho mô hình đầy đủ

**Phạm vi nguồn/suy luận:** dựa trên mô hình N-Queens ở trang 15–16 của bài tham khảo và công thức AMO ở Module3 trang 4, 10; toàn bộ phép cộng dưới đây được tự suy ra. Không phải số liệu thực nghiệm.

Với `N>=2`, giữ EXO cho N hàng và N cột; bỏ các đường chéo độ dài 1 khỏi lời gọi AMO:

- Có `6N-6` nhóm AMO.
- Tổng độ dài các nhóm AMO là `4N²-4`.
- Có `2N` ALO clauses.

**Pairwise:**

```
V = N²
C_AMO = 2N*C(N,2) + 2*C(N,2) + 4*C(N,3)
      = N*(N-1)*(5N-1)/3
C_total = N*(N-1)*(5N-1)/3 + 2N
```

Do đó số clause `Theta(N³)`.

**Sequential trực tiếp không rút gọn các nhóm nhỏ:**

```
V_aux = (4N²-4) - (6N-6) = 4N²-6N+2
V_total = 5N²-6N+2
C_AMO = 3*(4N²-4) - 4*(6N-6) = 12*(N-1)²
C_total = 12*(N-1)² + 2N
```

Ví dụ N=4: pairwise có 16 biến/84 clauses; sequential trực tiếp có 58 biến/116 clauses. Sequential không nhất thiết ít clauses hơn pairwise khi N nhỏ. Các ví dụ này là phép đếm theo định nghĩa, không phải kết quả chạy solver.

**Bậc tăng trưởng cho cả bàn:** binary có `Theta(N² log N)` clauses và `Theta(N log N)` biến phụ; sequential trực tiếp có `Theta(N²)` clauses và biến phụ; product hai chiều cân bằng có `Theta(N²)` clauses và `Theta(N^(3/2))` biến phụ; commander đệ quy nhóm hằng có O(N²) clauses và biến phụ, trong khi commander một mức nhóm căn bậc hai có cỡ `Theta(N^(5/2))` clauses.

N=1 cần xử lý riêng; có một ô và một nghiệm. Nếu giữ cả ALO hàng/cột sẽ có hai clauses đơn vị trùng nhau; nếu chuẩn hóa thì còn một. N=2,3 phải UNSAT; N>=4 có nghiệm. Không áp dụng công thức sequential N>=2 vào N=1 một cách máy móc.

## 8. Phạm vi độ khó và những tuyên bố nên tránh

**Phạm vi nguồn:** bài N-Queens trang 10–14, 19–20, 35–39; phần phân biệt dưới đây là kiểm tra phạm vi bài toán, không phải một định lý NP-completeness được chứng minh trong ba tài liệu chính.

- Bài toán đang giải là **N-Queens trên bàn trống, tìm một nghiệm**. Với N nguyên dương, chỉ N=2 và N=3 không có nghiệm; N=1 và mọi N>=4 có nghiệm. Bài toán quyết định cho bàn trống không nên được gọi là NP-complete chỉ vì có thể mã hóa sang SAT.
- **N-Queens Completion** là bài toán khác: đã có một số hậu cố định và hỏi có thể đặt tiếp để hoàn tất hay không. Nếu báo cáo nhắc kết quả NP-completeness của biến thể completion, cần thêm nguồn nghiên cứu gốc phù hợp và kiểm chứng nguồn đó; kết quả ấy không chuyển nguyên sang bài toán trên bàn trống.
- Liệt kê mọi nghiệm, đếm nghiệm và tìm một nghiệm cũng là ba nhiệm vụ khác nhau. Thí nghiệm “dừng ở nghiệm đầu tiên” không chứng minh khả năng đếm/liệt kê nhanh.
- Không gọi việc áp dụng bốn mã hóa đã có là phát minh mã hóa mới. Đóng góp phù hợp: cài đặt thống nhất, kiểm chứng tính đúng, so sánh thực nghiệm tái lập và phân tích giới hạn.
- Không suy “nhiều biến hơn” là mô hình mạnh hơn, hoặc “ít clauses hơn” là luôn nhanh hơn. Cấu trúc lan truyền, heuristic, thứ tự biến và solver đều có thể ảnh hưởng.

## 9. Thiết kế thực nghiệm và tính trung thực của dữ liệu

**Phạm vi nguồn:** bài N-Queens trang 35–39; tệp mẫu trang 10–20, 25–30; yêu cầu trang 1/1.

1. **Không dùng bảng 4.2 của bài tham khảo làm số liệu tự chạy.** Bài cũ ghi Glucose3, i7-1165G7, RAM 16GB và timeout 100 giây. Đó là số liệu của tác giả và máy khác. Nếu trích để bàn luận thì ghi “kết quả công bố trong tài liệu tham khảo”, tách khỏi bảng mới, không tính speedup trực tiếp giữa hai máy.
2. Tệp mẫu 2DBMP tách kết quả tự chạy và kết quả công bố, giới hạn so sánh runtime khi khác môi trường; có thể học cách này. Toàn bộ số liệu Regular/Harwell–Boeing trong mẫu không liên quan trực tiếp tới N-Queens.
3. Đo ít nhất thời gian xây mô hình, thời gian solve và tổng thời gian. Nêu phạm vi tổng thời gian có bao gồm nhập thư viện, tạo tiến trình, kiểm tra nghiệm hay không. Dùng đồng hồ đơn điệu độ phân giải cao.
4. Thời gian nhỏ nên lặp nhiều lần và báo median cùng độ phân tán hoặc min/max; nếu chỉ một lần thì ghi rõ, không suy ý nghĩa thống kê. Dùng cùng giới hạn số luồng nếu muốn so sánh có kiểm soát.
5. Lưu từng dòng kết quả thô: N, phương pháp, solver, encoding, repetition/seed, trạng thái, thời gian, số biến/clauses, giới hạn, kết quả kiểm tra nghiệm, phiên bản và mô tả lỗi nếu có.
6. Một lời giải phải qua validator độc lập kiểm tra đúng N hậu, cột nằm trong miền, khác cột và khác hai loại đường chéo. Solver trả SAT nhưng validator thất bại là **lỗi cài đặt**, không phải kết quả thành công.
7. Dùng N=1,2,3,4 làm kiểm tra biên. Kiểm tra AMO bằng duyệt các gán nhỏ và giải tồn tại biến phụ; với N nhỏ có thể đối chiếu tập nghiệm bàn cờ giữa các encoding hoặc backtracking để phát hiện cả mất nghiệm lẫn nhận nghiệm sai.
8. Nếu có symmetry breaking thì định nghĩa điều kiện và chứng minh còn ít nhất một đại diện; phải đồng nhất giữa các phương pháp hoặc báo như một thí nghiệm riêng. Không so sánh một solver được giảm đối xứng với solver khác không giảm mà bỏ qua khác biệt.
9. Timeout là dữ liệu kiểm duyệt (censored data): không thay timeout bằng thời gian đã giải đúng bằng ngưỡng; nếu vẽ điểm tại ngưỡng phải có ký hiệu timeout. Không tính trung bình đơn giản chỉ trên các bài giải được của từng solver rồi xếp hạng như thể các tập giống nhau.
10. Nếu cấp phát hoặc sinh CNF quá lớn, dùng trạng thái giới hạn bộ nhớ/kích thước hoặc timeout xây dựng đúng sự thật; không coi đó là UNSAT. Có thể báo công thức kích thước dự kiến riêng với số đếm đã tạo thật.
11. Trong kết luận, phạm vi hợp lệ là **bộ N, cấu hình máy, phiên bản, timeout và số lần chạy được mô tả**. Nhanh nhất ở bộ này không đồng nghĩa nhanh nhất cho mọi N-Queens hoặc biến thể completion.

## 10. Khuyến nghị ưu tiên cho nhóm triển khai

**Phạm vi đã đọc cho khuyến nghị:** đủ 1/1 trang yêu cầu, 41/41 trang bài N-Queens, 32/32 trang mẫu, 17/17 trang Module3 và 27/27 trang Module2 như mục 1.

Nên dùng mô hình đầy đủ EXO hàng/cột + AMO đường chéo làm cấu hình chính, cài năm mã hóa với biến phụ riêng, validator độc lập và bộ đếm clause thực. Dùng CP-SAT với ba AllDifferent và MIP với biến ô làm đối chứng; thử cả bốn công cụ được nêu trong đề và báo rõ giới hạn khả dụng. Báo cáo theo dạng bài báo Elsevier, lấy kết quả trực tiếp từ tệp dữ liệu thô tự chạy. Phần còn thiếu thông tin cá nhân hoặc URL repository phải hiện rõ là cần bổ sung, không tạo dữ liệu nhận dạng hay URL giả.
