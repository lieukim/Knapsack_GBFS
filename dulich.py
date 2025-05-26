import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
import heapq
from datetime import datetime
import os
import graphviz

place_names = ['Bảo tàng Quốc gia', 'Công viên Trung tâm', 'Di tích Lịch Sử',
               'Đồi Nghệ Thuật', 'Chợ đêm Sài Gòn', 'Hồ Thiên Nga']
places = [(2, 10), (1, 7), (4, 15), (3, 8), (1, 5), (3, 11)]

# Ma trận khoảng cách
raw_distances = {
    (0, 1): 2, (0, 2): 5, (0, 3): 6, (0, 4): 3, (0, 5): 4,
    (1, 2): 3, (1, 3): 4, (1, 4): 2, (1, 5): 5,
    (2, 3): 2, (2, 4): 4, (2, 5): 3,
    (3, 4): 3, (3, 5): 2,
    (4, 5): 4
}
distances = raw_distances.copy()
distances.update({(j, i): d for (i, j), d in raw_distances.items()})

positions = {
    0: (120, 90), 1: (300, 150), 2: (100, 240),
    3: (180, 350), 4: (380, 280), 5: (500, 100),
}

icons = ['🏛', '🌳', '🏰', '⛰', '🛍', '🦢']
selected_indices = []
final_summary = ""

root = tk.Tk()
root.title("Quản lý Tour - GBFS")
root.geometry("1000x600")
root.configure(bg="#f0f0f0")

frame_input = tk.Frame(root, bg="#f0f0f0")
frame_input.pack(side="left", fill="y", padx=10, pady=10)

frame_center = tk.Frame(root, bg="#ffffff", relief="sunken", bd=1)
frame_center.pack(side="left", fill="both", expand=True, padx=5, pady=10)

frame_output = tk.Frame(root, bg="#f0f0f0")
frame_output.pack(side="right", fill="y", padx=10, pady=10)

ttk.Label(frame_input, text="Chọn địa điểm:", font=("Arial", 11, "bold")).pack(anchor="w")
checkbox_vars = []
for i, name in enumerate(place_names):
    var = tk.IntVar(value=1)
    cb = tk.Checkbutton(frame_input, text=f"{name} ({places[i][0]}h - {places[i][1]} điểm)",
                        variable=var, bg="#f0f0f0")
    cb.pack(anchor="w")
    checkbox_vars.append(var)

hours = [f"{h:02d}" for h in range(7, 23)]
minutes = [f"{m:02d}" for m in range(60)]

tk.Label(frame_input, text="Giờ bắt đầu:").pack(anchor="w")
start_hour = ttk.Combobox(frame_input, values=hours, width=3)
start_hour.set("09")
start_hour.pack(anchor="w")
start_min = ttk.Combobox(frame_input, values=minutes, width=3)
start_min.set("00")
start_min.pack(anchor="w")

tk.Label(frame_input, text="Giờ kết thúc:").pack(anchor="w")
end_hour = ttk.Combobox(frame_input, values=hours, width=3)
end_hour.set("17")
end_hour.pack(anchor="w")
end_min = ttk.Combobox(frame_input, values=minutes, width=3)
end_min.set("00")
end_min.pack(anchor="w")

canvas = tk.Canvas(frame_center, width=600, height=500, bg="white")
canvas.pack()

desc = tk.Text(frame_output, width=40, height=20)
desc.pack(padx=5, pady=5)

def heuristic(index, remaining_time, selected_places):
    total_score = 0
    count = 0
    for t, s in sorted(selected_places[index:], key=lambda x: x[0]):
        if t <= remaining_time:
            total_score += s
            count += 1
            remaining_time -= t
    return total_score + count * 2

def gbfs_tour_knapsack(max_time, selected_places, selected_ids):
    pq = []
    heapq.heappush(pq, (-heuristic(0, max_time, selected_places), 0, 0, 0, []))
    best_score = 0
    best_tour = []
    while pq:
        h, cur_val, cur_time, idx, selected = heapq.heappop(pq)
        if cur_val > best_score:
            best_score = cur_val
            best_tour = selected
        if idx >= len(selected_places):
            continue
        time_needed, score = selected_places[idx]
        place_id = selected_ids[idx]
        heapq.heappush(pq, (-heuristic(idx+1, max_time-cur_time, selected_places),
                            cur_val, cur_time, idx+1, selected))
        if cur_time + time_needed <= max_time:
            heapq.heappush(pq, (-heuristic(idx+1, max_time-(cur_time+time_needed), selected_places),
                                cur_val+score, cur_time+time_needed, idx+1, selected + [place_id]))
    return best_tour, best_score

def draw_map():
    canvas.delete("all")
    for (a, b), dist in distances.items():
        if a < b:
            x1, y1 = positions[a]
            x2, y2 = positions[b]
            canvas.create_line(x1, y1, x2, y2, fill="#ccc")
    for i, name in enumerate(place_names):
        x, y = positions[i]
        r = 20
        canvas.create_oval(x - r, y - r, x + r, y + r, fill="#fff", outline="black")
        canvas.create_text(x, y, text=icons[i], font=("Arial", 14))
        canvas.create_text(x, y + 28, text=name, font=("Arial", 9), anchor="n")

def draw_graph(selected):
    for i in range(len(selected) - 1):
        a, b = selected[i], selected[i + 1]
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        canvas.create_line(x1, y1, x2, y2, width=4, fill="#FF6F00")
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        canvas.create_text(mid_x, mid_y, text=str(i + 1), font=("Arial", 10, "bold"), fill="black")

def export_summary():
    if not final_summary:
        messagebox.showinfo("Thông báo", "Chưa có tour nào để xuất!")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_summary)
        messagebox.showinfo("Thành công", f"Đã lưu lộ trình tại: {filepath}")

def show_tree_image():
    # Vẽ cây theo heuristic điểm/thời gian
    heuristics = [(s / t, t, s, i) for i, (t, s) in enumerate(places)]
    heuristics.sort(reverse=True)
    max_time = 8
    dot = graphviz.Digraph(format='png')
    dot.attr(rankdir='TB', size='8')
    dot.node('Start', 'Start\n(0h, 0đ)')

    def build_gbfs_tree(parent, remaining_time, used, prefix=""):
        for ratio, t, s, idx in heuristics:
            if idx in used:
                continue
            if remaining_time >= t:
                node_id = f"{prefix}{idx}"
                label = f"{place_names[idx]}\n({t}h, {s}đ)\n[h={ratio:.2f}]"
                dot.node(node_id, label)
                dot.edge(parent, node_id)
                build_gbfs_tree(node_id, remaining_time - t, used + [idx], prefix + f"{idx}_")

    build_gbfs_tree("Start", max_time, [])
    dot.render("gbfs_tree_integration", format='png', cleanup=True)

    top = tk.Toplevel(root)
    top.title("Cây lựa chọn GBFS")
    img = Image.open("gbfs_tree_integration.png")
    img = img.resize((900, 700))
    tk_img = ImageTk.PhotoImage(img)
    lbl = tk.Label(top, image=tk_img)
    lbl.image = tk_img
    lbl.pack()

def start_tour():
    global selected_indices, final_summary
    try:
        start = datetime.strptime(f"{start_hour.get()}:{start_min.get()}", "%H:%M")
        end = datetime.strptime(f"{end_hour.get()}:{end_min.get()}", "%H:%M")
        max_time = (end - start).seconds // 3600
    except:
        messagebox.showerror("Lỗi", "Sai định dạng thời gian.")
        return
    selected_indices = [i for i, var in enumerate(checkbox_vars) if var.get() == 1]
    if not selected_indices:
        messagebox.showinfo("Thông báo", "Chọn ít nhất 1 địa điểm.")
        return
    sub_places = [places[i] for i in selected_indices]
    tour, score = gbfs_tour_knapsack(max_time, sub_places, selected_indices)
    selected_indices = tour
    draw_map()
    draw_graph(selected_indices)
    desc.delete("1.0", tk.END)
    summary = f"🎯 Tổng điểm đạt được: {score} điểm\n"
    summary += f"🕐 Tổng thời gian sử dụng: {sum(places[i][0] for i in selected_indices)}h\n"
    summary += f"📍 Đã tham quan: {len(selected_indices)} địa điểm\n"
    summary += "🔗 Lộ trình:\n"
    for idx, i in enumerate(selected_indices, 1):
        summary += f"   {idx}. {place_names[i]}\n"
    desc.insert(tk.END, summary)
    final_summary = summary

tk.Button(frame_input, text="Tìm Tour Tối Ưu", command=start_tour, bg="#4CAF50", fg="white").pack(pady=10, fill="x")
tk.Button(frame_output, text="📤 Xuất lộ trình", command=export_summary, bg="#2196F3", fg="white").pack(pady=5, fill="x")
tk.Button(frame_output, text="🌲 Xem cây GBFS", command=show_tree_image, bg="#9C27B0", fg="white").pack(pady=5, fill="x")

draw_map()
root.mainloop()
