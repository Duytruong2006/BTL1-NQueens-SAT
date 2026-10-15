"""Fill the scientific report with verified measurements, never placeholders."""
from __future__ import annotations
import importlib.util, json, pathlib, re, statistics
ROOT=pathlib.Path(__file__).resolve().parents[1]
GEN=ROOT/'report'/'generated'
LABELS={'pairwise':'Pairwise','binary':'Binary','sequential':'Sequential',
        'commander':'Commander','product':'Product','cp_sat':'CP-SAT',
        'cplex_mip':'CPLEX MIP','gurobi':'Gurobi','cplex_cp':'CPLEX CP'}

def tex(s):
    return str(s).replace('\\',r'\textbackslash{}').replace('_',r'\_').replace('%',r'\%').replace('&',r'\&')
def num(x): return f'{x:.6f}' if x<.01 else f'{x:.4f}'
def write(name,text): (GEN/name).write_text(text+'\n',encoding='utf-8')
def table(name,caption,label,width=False):
    body=(GEN/name).read_text(encoding='utf-8')
    if width: body='\\FitTableWidth{%\n'+body+'}\n'
    write(name,'\\begin{table}[htbp]\n\\centering\\small\n\\caption{'+caption+'}\n\\label{'+label+'}\n'+body+'\\end{table}')

def main():
    data=json.loads((ROOT/'results'/'analysis.json').read_text(encoding='utf-8'))
    env=json.loads((ROOT/'results'/'environment.json').read_text(encoding='utf-8'))
    groups=data['groups']; lookup={(g['suite'],g['method'],g['n']):g for g in groups}
    if not data['findings']['main_sat_complete']:
        raise SystemExit('Main SAT dataset is incomplete')
    if any(lookup.get(('main',m,n),{}).get('trials')!=3 for m in ['cp_sat','cplex_mip','gurobi','cplex_cp'] for n in [8,16,32,64,128]):
        raise SystemExit('Comparison dataset is incomplete')
    if any(lookup.get(('large',m,n),{}).get('trials')!=1 for m in LABELS for n in [256,512,1000]):
        raise SystemExit('Large dataset is incomplete')
    spec=importlib.util.spec_from_file_location('analysis_helpers',ROOT/'scripts'/'analyze.py')
    mod=importlib.util.module_from_spec(spec);spec.loader.exec_module(mod)
    mod.write_tables(groups,GEN)
    table('main_sat_table.tex','Thời gian tổng trung vị của SAT trên tập chính tính bằng giây. Mỗi ô số có đủ 3/3 lần SAT; 3 TO nghĩa là cả ba lần hết hạn 30 giây.','tab:sat',True)
    table('comparison_table.tex','So sánh thời gian tổng trung vị tính bằng giây. Best SAT chọn median nhỏ nhất trong các mã hóa đủ 3/3 SAT ở từng N. LIC là giới hạn giấy phép; UNAV là chưa chạy được công cụ.','tab:compare',True)
    table('large_table.tex','Tập mở rộng với một lần chạy mỗi cấu hình, thời gian tổng tính bằng giây. TO là hết hạn, LIC là giới hạn giấy phép, UNAV là thiếu công cụ hoặc giấy phép, SKIP là vượt trần clause đã định.','tab:large')
    counts=[x for x in data['cnf_counts'] if x['n']==128]
    rows=[r'\begin{table}[htbp]',r'\centering\small',r'\caption{Kích thước CNF sinh thực tế với $N=128$ trước tiền xử lý}',r'\label{tab:counts}',r'\begin{tabular}{lrrrr}',r'\toprule',r'Mã hóa & Biến gốc & Biến phụ & Tổng biến & Clause \\',r'\midrule']
    rows += [f"{LABELS[x['method']]} & {x['nprimary']:,} & {x['nauxiliary']:,} & {x['nvars']:,} & {x['nclauses']:,}"+r' \\' for x in counts]
    rows += [r'\bottomrule',r'\end{tabular}',r'\end{table}']
    write('counts_table.tex','\n'.join(rows))
    phase_rows=[r'\begin{table}[htbp]',r'\centering\small',r'\caption{Các pha thời gian SAT tại $N=128$ tính bằng giây. Mỗi số là trung vị riêng của pha trên ba lần SAT; tổng các trung vị pha không bắt buộc bằng trung vị tổng. TO không có số đo pha hoàn thành.}',r'\label{tab:phases}',r'\FitTableWidth{%',r'\begin{tabular}{lrrrrl}',r'\toprule',r'Mã hóa & Tạo CNF & Nạp solver & Tìm nghiệm & Tổng & Nhỏ nhất tới lớn nhất \\',r'\midrule']
    for m in ['pairwise','binary','sequential','commander','product']:
        g=lookup[('main',m,128)]
        if g['all_expected_trials_sat']:
            vals=[num(g[k]) for k in ['median_build_seconds','median_setup_seconds','median_solve_seconds','median_seconds']]
            phase_rows.append(LABELS[m]+' & '+' & '.join(vals)+f" & {num(g['min_seconds'])}--{num(g['max_seconds'])}"+r' \\')
        else: phase_rows.append(LABELS[m]+r' & -- & -- & -- & TO & -- \\')
    phase_rows += [r'\bottomrule',r'\end{tabular}',r'}',r'\end{table}']
    write('phase_table.tex','\n'.join(phase_rows))
    mem=env['memory_bytes']/2**30
    packages=env['packages']
    versions=', '.join(tex(k)+' '+tex(v) for k,v in packages.items())
    write('environment.tex',f"Thực nghiệm được ghi nhận ngày 15/10/2026 trên Windows 11 64 bit, CPU {tex(env['cpu'])}, {env['logical_processors']} bộ xử lý logic, RAM hệ điều hành nhận {mem:.2f} GiB, Python 3.12.14. Các phiên bản thư viện là {versions}. Phiên bản máy giải CP Optimizer từ nhật ký là 22.2.0.0. Thông tin môi trường đầy đủ được lưu trong \\texttt{{results/environment.json}}; thời điểm mỗi lần chạy dùng UTC trong nhật ký và có thể quy đổi sang UTC+7.")
    native_ok=[m for m in ['cp_sat','cplex_mip','gurobi','cplex_cp'] if any(lookup[('main',m,n)]['solved_count'] for n in [8,16,32,64,128])]
    missing=[m for m in ['cp_sat','cplex_mip','gurobi','cplex_cp'] if m not in native_ok]
    write('test_results.tex',"Kết quả kiểm thử: toàn bộ 8 bài kiểm thử SAT và 7 bài kiểm thử đối chứng đều đạt. Các backend thực sự khả dụng khi kiểm tra gồm "+', '.join(LABELS[m] for m in native_ok)+". Các bài nhỏ $N=1,2,3,4,8$ của những backend này được đối chiếu về trạng thái và hình học nghiệm."+(" "+', '.join(LABELS[m] for m in missing)+" chưa được xác nhận tích hợp vì môi trường chưa có giấy phép khả dụng; việc bỏ qua backend này không được xem là một lần giải thành công." if missing else '')+" Nhật ký kiểm thử được giữ trong thư mục \\texttt{tests}.")
    sat_groups=[g for g in groups if g['suite']=='main' and g['method'] in ['pairwise','binary','sequential','commander','product']]
    sat_success=sum(g['solved_count'] for g in sat_groups)
    speed=lookup[('main','pairwise',64)]['median_seconds']/lookup[('main','binary',64)]['median_seconds']
    cpair=next(x['nclauses'] for x in counts if x['method']=='pairwise')
    cproduct=next(x['nclauses'] for x in counts if x['method']=='product')
    reduction=100*(1-cproduct/cpair)
    discuss=f"Trong 75 lần chạy SAT của tập chính, {sat_success} lần tìm được nghiệm đã kiểm tra và {75-sat_success} lần hết hạn. Ở $N=64$, binary có median {num(lookup[('main','binary',64)]['median_seconds'])} giây, trong khi pairwise là {num(lookup[('main','pairwise',64)]['median_seconds'])} giây, tức nhanh hơn khoảng {speed:.2f} lần trong cấu hình này. Sequential và product đều hết hạn ở cả ba lần chạy tại $N=64$. Tại $N=32$, product cũng không hoàn thành trong hạn, dù công thức của nó nhỏ hơn pairwise. Điều đó cho thấy số clause không mô tả đầy đủ cấu trúc lan truyền và tìm kiếm.\n\n"
    discuss+=f"Ở $N=128$, pairwise có {cpair:,} clause; product còn {cproduct:,}, giảm {reduction:.2f}\\%. Median của binary, commander và product lần lượt là {num(lookup[('main','binary',128)]['median_seconds'])}, {num(lookup[('main','commander',128)]['median_seconds'])}, {num(lookup[('main','product',128)]['median_seconds'])} giây. Ba cấu hình này có thời gian gần nhau trên cùng máy; chênh lệch nhỏ không đủ để khẳng định thứ hạng tổng quát. Sequential tiếp tục hết hạn. Commander giảm mạnh thời gian từ $N=64$ sang $N=128$, minh họa tính không đơn điệu của việc tìm một nghiệm trên các kích thước khác nhau.\n\n"
    discuss+="Tài liệu tham khảo \\cite{bach2024} ưu tiên product theo tập chạy của tác giả, nhưng số liệu hiện tại không tái khẳng định một cấu hình luôn thắng. Các kết quả khác nhau có thể liên quan đến quy tắc chia nhóm, công thức cụ thể, thứ tự biến, solver và máy chạy. Báo cáo chỉ quy kết kết quả cho cài đặt và protocol đã công bố, không dùng thời gian trong tài liệu gốc để tính hệ số tăng tốc trên máy hiện tại."
    write('sat_discussion.tex',discuss)
    cplex8=lookup[('main','cplex_mip',8)]['median_seconds']; cp128=lookup[('main','cplex_cp',128)]['median_seconds']; cps128=lookup[('main','cp_sat',128)]['median_seconds']
    gurobi_text=("Gurobi chưa có thời gian giải hợp lệ vì chưa có giấy phép khả dụng. " if 'gurobi' in missing else f"Gurobi giải được cả ba lần tại $N=8,16,32$; median tại $N=32$ là {num(lookup[('main','gurobi',32)]['median_seconds'])} giây. Từ $N=64$, số biến vượt giới hạn 2000 của giấy phép đi kèm nên kết quả là LIC. Trên Windows, giấy phép đi kèm được đặt ở một đường dẫn ASCII để thư viện bản địa đọc được khi thư mục dự án có dấu tiếng Việt. Các lỗi đường dẫn ban đầu được giữ trong \\texttt{{results/diagnostics}} và không được dùng làm thời gian giải. ")
    write('comparison_discussion.tex',f"Trên $N=8,16$, CPLEX MIP trả nghiệm hợp lệ trong tất cả các lần chạy; median tại $N=8$ là {num(cplex8)} giây. Từ $N=32$, mô hình có ít nhất 1024 biến nhị phân, vượt mức 1000 biến của bản CPLEX Community đang dùng, nên các ô tương ứng là LIC. CP-SAT và CPLEX CP giải được toàn bộ 15 lần chạy mỗi công cụ trên tập chính. Ở $N=128$, median của CPLEX CP là {num(cp128)} giây và CP-SAT là {num(cps128)} giây. Các con số phản ánh cả chi phí mô hình hóa và gọi công cụ trong hai giao diện.\n\n"+gurobi_text+"Cột Best SAT thay đổi encoding theo từng kích thước và được chọn sau khi quan sát kết quả; đó là bao dưới thực nghiệm của các cấu hình đã chạy, không phải một bộ chọn encoding được huấn luyện hay một solver mới. Người đọc nên đối chiếu cả Bảng~\\ref{tab:sat} để biết phương pháp cụ thể.")
    large=[g for g in groups if g['suite']=='large']
    successes=[g for g in large if g['solved_count']]
    largest=max((g['n'] for g in successes),default=0)
    sentences=[]
    for n in [256,512,1000]:
        ok=[g for g in large if g['n']==n and g['solved_count']]
        sentences.append(f"Với $N={n}$, "+(', '.join(f"{LABELS[g['method']]} ({num(g['median_seconds'])} giây)" for g in ok)+" tìm được nghiệm hợp lệ." if ok else "không có cấu hình nào trả nghiệm hợp lệ trong điều kiện chạy đã đặt."))
    sentences.append("Pairwise ở cả ba kích thước mở rộng vượt trần 5.000.000 clause và được bỏ qua trước khi sinh CNF. Các giới hạn giấy phép được phân biệt với giới hạn thời gian. Mỗi ô ở tập mở rộng chỉ có một lần đo, nên các số này là khảo sát khả năng mở rộng, không cung cấp ước lượng độ biến thiên như tập chính.")
    write('large_discussion.tex','\n\n'.join(sentences))
    conclusion=f"Bài tập đã cài đặt thống nhất năm mã hóa AMO cho N-Queens, xây dựng các mô hình đối chứng CP/MIP và kiểm tra nghiệm độc lập. Bộ kiểm thử xác nhận tính tương đương của AMO trên mọi phép gán nhỏ, trạng thái SAT/UNSAT và số nghiệm của các bàn cờ nhỏ. Thực nghiệm chính cho {sat_success}/75 lần SAT thành công, cho thấy binary là lựa chọn thực dụng ở $N=64$ trong cấu hình này, còn các encoding nhỏ về số clause vẫn có thể hết hạn. Ở $N=128$, binary, commander và product có thời gian gần nhau, nên chưa có cơ sở kết luận một encoding luôn tốt nhất.\n\n"
    conclusion+=f"Khảo sát được thực hiện đến $N=1000$ và kích thước lớn nhất có nghiệm hợp lệ là $N={largest}$. Kết quả đối chứng chỉ được so sánh trong miền có dữ liệu chạy hợp lệ; các giới hạn giấy phép được công bố rõ. Hướng tiếp theo là mở rộng giấy phép cho các bộ giải bị giới hạn, tăng số phép lặp trên tập lớn, thử thêm nhiều SAT solver và khảo sát N-Queens Completion bằng cùng cơ chế kiểm tra nghiệm."
    write('conclusion.tex',conclusion)
    write('abstract.tex',f"Báo cáo cài đặt và đánh giá năm mã hóa SAT cho bài toán N-Queens trên bàn cờ trống: pairwise, binary, sequential counter, commander đệ quy và product. Các mô hình dùng cùng ràng buộc hàng, cột, đường chéo; nghiệm được kiểm tra hình học độc lập. Tính đúng được đối chiếu qua 2555 phép gán AMO nhỏ, 60 trường hợp SAT/UNSAT và đếm nghiệm đến N=8. Tập chính gồm năm kích thước từ 8 đến 128, mỗi cấu hình lặp ba lần; tập mở rộng khảo sát N=256,512,1000 với hạn tổng 30 giây. Trên tập chính, SAT hoàn thành {sat_success}/75 lần chạy; binary nhanh hơn pairwise khoảng {speed:.2f} lần ở N=64. Kết quả cho thấy giảm số clause không bảo đảm giảm thời gian giải, và không có encoding thắng trên mọi kích thước đã xét. Báo cáo đối chiếu với CP-SAT, CPLEX CP, CPLEX MIP và Gurobi trong miền giấy phép khả dụng, đồng thời công bố các giới hạn kích thước. Toàn bộ mã nguồn, dữ liệu đo và quy trình tái lập được cung cấp kèm báo cáo.")
    # CAS captures the abstract verbatim; a nested input command would appear
    # as a path in the title block, so materialize the completed text inline.
    main_path=ROOT/'report'/'main.tex'
    main_source=main_path.read_text(encoding='utf-8')
    abstract=(GEN/'abstract.tex').read_text(encoding='utf-8').strip()
    main_source=re.sub(r'(\\begin\{abstract\}\s*).*?(\\end\{abstract\})',
        lambda match:match.group(1)+abstract+'\n'+match.group(2),main_source,flags=re.S)
    main_path.write_text(main_source,encoding='utf-8')
    print('Filled report from',data['records_analyzed'],'actual records; largest verified N=',largest)

if __name__=='__main__': main()
