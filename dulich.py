import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import heapq
from datetime import datetime
import os

place_names = ['Bảo tàng Quốc gia', 'Công viên Trung tâm', 'Di tích Lịch Sử',
               'Đồi Nghệ Thuật', 'Chợ đêm Sài Gòn', 'Hồ Thiên Nga', 'Làng Văn Hóa', 'Vườn Thực Vật', 'Nhà hát Thành Phố']
places = [(2, 10), (1, 7), (4, 15), (3, 8), (1, 5), (3, 11), (2, 9), (3, 6), (1, 8)]

positions = {
    0: (120, 90), 1: (300, 150), 2: (100, 240),
    3: (180, 350), 4: (380, 280), 5: (500, 100),
    6: (250, 60), 7: (400, 200), 8: (550, 180),
}

icons = ['🏛', '🌳', '🏰', '⛰', '🛕', '🦢', '🏡', '🌺', '🎭']

selected_indices = []
final_summary = ""
steps_text = ""

root = tk.Tk()
root.title("Quản lý Tour - GBFS")
root.geometry("1000x700")
root.configure(bg="#f0f0f0")

frame_input = tk.Frame(root, bg="#f0f0f0")
frame_input.pack(side="left", fill="y", padx=10, pady=10)

frame_center = tk.Frame(root, bg="#ffffff", relief="sunken", bd=1)
frame_center.pack(side="left", fill="both", expand=True, padx=5, pady=10)

frame_output = tk.Frame(root, bg="#f0f0f0")
frame_output.pack(side="right", fill="y", padx=10, pady=10)

canvas = tk.Canvas(frame_center, width=600, height=400, bg="white")
canvas.pack()

desc = tk.Text(frame_output, width=40, height=14)
desc.pack(padx=5, pady=5)

frame_steps = tk.Frame(frame_center, bg="#ffffff")
frame_steps.pack(fill="x", padx=5, pady=5)

step_label = tk.Label(frame_steps, text="🧭 Các bước thuật toán GBFS", bg="#ffffff", font=("Arial", 10, "bold"))
step_label.pack(anchor="w")

step_view = tk.Text(frame_steps, width=82, height=8, bg="#f9f9f9")
step_view.pack(padx=5, pady=(0, 5))
step_view.insert(tk.END, "Các bước lựa chọn sẽ hiển thị ở đây...")
step_view.config(state="disabled")

ttk.Label(frame_input, text="Chọn địa điểm:", font=("Arial", 11, "bold")).pack(anchor="w")
checkbox_vars = []
for i, name in enumerate(place_names):
    var = tk.IntVar(value=0)  # Không tick sẵn
    cb = tk.Checkbutton(frame_input, text=f"{name} ({places[i][0]}h - {places[i][1]} điểm)", variable=var, bg="#f0f0f0")
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
    steps = []
    pq = []
    heapq.heappush(pq, (-heuristic(0, max_time, selected_places), 0, 0, 0, []))
    best_score = 0
    best_tour = []
    while pq:
        h, cur_val, cur_time, idx, selected = heapq.heappop(pq)
        steps.append(f"Xét node {idx} | score: {cur_val} | thời gian: {cur_time} | chọn: {[place_names[i] for i in selected]}")
        if cur_val > best_score:
            best_score = cur_val
            best_tour = selected
        if idx >= len(selected_places):
            continue
        time_needed, score = selected_places[idx]
        place_id = selected_ids[idx]
        heapq.heappush(pq, (-heuristic(idx+1, max_time-cur_time, selected_places), cur_val, cur_time, idx+1, selected))
        if cur_time + time_needed <= max_time:
            heapq.heappush(pq, (-heuristic(idx+1, max_time-(cur_time+time_needed), selected_places), cur_val+score, cur_time+time_needed, idx+1, selected + [place_id]))
    return best_tour, best_score, steps

def export_summary():
    if not final_summary:
        messagebox.showinfo("Thông báo", "Chưa có tour nào để xuất!")
        return
    filepath = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files", "*.txt")])
    if filepath:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(final_summary)
        messagebox.showinfo("Thành công", f"Đã lưu lộ trình tại: {filepath}")

def draw_graph(selected):
    canvas.delete("all")
    pastel_color = "#b2ebf2"
    for i, name in enumerate(place_names):
        x, y = positions[i]
        r = 20
        fill = pastel_color if i in selected else "#fff"
        canvas.create_oval(x - r, y - r, x + r, y + r, fill=fill, outline="black")
        canvas.create_text(x, y, text=icons[i], font=("Arial", 14))
        canvas.create_text(x, y + 28, text=name, font=("Arial", 9), anchor="n")

    for i in range(len(selected) - 1):
        a, b = selected[i], selected[i + 1]
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        canvas.create_line(x1, y1, x2, y2, width=4, fill="#FF6F00")
        mid_x, mid_y = (x1 + x2) // 2, (y1 + y2) // 2
        canvas.create_text(mid_x, mid_y, text=str(i + 1), font=("Arial", 10, "bold"), fill="black")

def reset_all():
    global selected_indices, final_summary
    for var in checkbox_vars:
        var.set(0)
    start_hour.set("09")
    start_min.set("00")
    end_hour.set("17")
    end_min.set("00")
    selected_indices = []
    final_summary = ""
    desc.delete("1.0", tk.END)
    step_view.config(state="normal")
    step_view.delete("1.0", tk.END)
    step_view.insert(tk.END, "Các bước lựa chọn sẽ hiển thị ở đây...")
    step_view.config(state="disabled")
    draw_graph([])

def start_tour():
    global selected_indices, final_summary, steps_text
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
    tour, score, steps = gbfs_tour_knapsack(max_time, sub_places, selected_indices)
    selected_indices = tour
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

    step_view.config(state="normal")
    step_view.delete("1.0", tk.END)
    step_view.insert(tk.END, "\n".join(steps))
    step_view.config(state="disabled")

tk.Button(frame_input, text="Tìm Tour Tối Ưu", command=start_tour, bg="#4CAF50", fg="white").pack(pady=10, fill="x")
tk.Button(frame_input, text="🔄 Reset", command=reset_all, bg="#f44336", fg="white").pack(pady=5, fill="x")
tk.Button(frame_output, text="📤 Xuất lộ trình", command=export_summary, bg="#2196F3", fg="white").pack(pady=5, fill="x")

draw_graph([])
root.mainloop()
