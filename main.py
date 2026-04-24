import tkinter as tk
from tkinter import ttk, messagebox
import psutil

class TaskManagerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Aloof Task Manager")
        self.root.geometry("600x400")
        
        # Track sorting state
        self.sort_col = None
        self.reverse = False

        columns = ("PID", "Name", "CPU", "MEM")
        self.tree = ttk.Treeview(root, columns=columns, show='headings')
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=100)
        self.tree.pack(fill=tk.BOTH, expand=True)

        btn_frame = tk.Frame(root)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Kill Selected", command=self.kill_process).pack(side=tk.LEFT, padx=5)

        self.update_list()

    def sort_column(self, col):
        # Toggle reverse if same column, otherwise default to False
        if self.sort_col == col:
            self.reverse = not self.reverse
        else:
            self.sort_col = col
            self.reverse = False
        self._apply_sort()

    def _apply_sort(self):
        if not self.sort_col:
            return
        
        l = [(self.tree.set(k, self.sort_col), k) for k in self.tree.get_children('')]
        try:
            l.sort(key=lambda t: float(t[0]), reverse=self.reverse)
        except ValueError:
            l.sort(key=lambda t: t[0], reverse=self.reverse)

        for index, (val, k) in enumerate(l):
            self.tree.move(k, '', index)

    def update_list(self):
        # 1. Fetch data
        new_data = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                new_data.append((proc.info['pid'], proc.info['name'], proc.info['cpu_percent'], round(proc.info['memory_percent'], 2)))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        # 2. Update Treeview
        for i in self.tree.get_children():
            self.tree.delete(i)
        for item in new_data:
            self.tree.insert("", "end", values=item)
        
        # 3. Re-apply the sort state
        self._apply_sort()
            
        self.root.after(3000, self.update_list)

    def kill_process(self):
        selected = self.tree.selection()
        if selected:
            pid = int(self.tree.item(selected[0])['values'][0])
            try:
                psutil.Process(pid).terminate()
            except Exception as e:
                messagebox.showerror("Error", f"Failed: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = TaskManagerGUI(root)
    root.mainloop()
