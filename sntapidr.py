import tkinter as tk
from tkinter import messagebox, filedialog
import re
import os
import json
import asyncio
import aiohttp
import webbrowser
from threading import Thread

class APIDR:
    def __init__(self, root):
        self.root = root
        self.root.title("API Doctor")
        self.root.geometry("600x400")

        self.select_label = tk.Label(root, text="Select API:")
        self.select_label.grid(row=0, column=0, sticky='w', padx=10)

        self.api_options = tk.StringVar()
        self.api_options_menu = tk.OptionMenu(root, self.api_options, '', command=self.load_api_info)
        self.api_options_menu.grid(row=0, column=2, columnspan=2, sticky='ew', padx=10, pady=5)

        self.info_label = tk.Label(root, text="Information:")
        self.info_label.grid(row=1, column=0, columnspan=3, sticky='w', padx=10)
        self.info_text = tk.Text(root, height=10, width=50, state='disabled', wrap='word')
        self.info_text.grid(row=2, column=0, columnspan=3, sticky='nsew', padx=10, pady=5)

        self.request_label = tk.Label(root, text="Request JSON:")
        self.request_label.grid(row=3, column=0, columnspan=3, sticky='w', padx=10)
        self.request_entry = tk.Entry(root, width=50)
        self.request_entry.grid(row=4, column=0, columnspan=3, sticky='ew', padx=10, pady=5)
        self.send_btn = tk.Button(root, text="Send", command=lambda: asyncio.run(self.send_request()))
        self.send_btn.grid(row=5, column=2, sticky='ew', padx=10, pady=5)

        self.add_btn = tk.Button(root, text="Add API", command=self.open_add_window)
        self.add_btn.grid(row=5, column=1, sticky='ew', padx=10, pady=5)

        self.edit_btn = tk.Button(root, text="Edit API", command=self.open_edit_window)
        self.edit_btn.grid(row=5, column=0, sticky='ew', padx=10, pady=5)

        self.root.grid_columnconfigure(2, weight=1)
        self.root.grid_rowconfigure(2, weight=1)

        self.explainjson = "Example:\nIf you want https://example.com/search?q=hello+world\n\nURL:\thttps://example.com/search\nJSON:\t{\"q\":\"hello world\"}"

        asyncio.run(self.tooltip(self.request_entry, self.explainjson))

        self.load_apis()

    def get_apis(self):
        try:
            return [f for f in os.listdir('apis') if os.path.isfile(os.path.join('apis', f))]
        except FileNotFoundError:
            os.makedirs('apis')
            return []

    def load_apis(self):
        api_list = self.get_apis()
        if not api_list:
            self.open_add_window()
        else:
            self.api_options.set(api_list[0])
            menu = self.api_options_menu['menu']
            menu.delete(0, 'end')
            for api in api_list:
                menu.add_command(label=api, command=lambda value=api: self.api_options.set(value) or self.load_api_info(value))
            self.load_api_info(api_list[0])

    def load_api_info(self, name):
        def load_info():
            try:
                with open(os.path.join('apis', name), 'r') as api_file:
                    api_data = json.load(api_file)
                    self.info_text.config(state='normal')
                    self.info_text.delete(1.0, tk.END)
                    self.info_text.insert(tk.END, api_data.get('help', 'No help available.'))
                    self.info_text.config(state='disabled')
                    self.request_entry.delete(0, tk.END)
                    self.request_entry.insert(0, api_data.get('req', ''))
            except (FileNotFoundError, json.JSONDecodeError) as e:
                messagebox.showerror("Error", str(e))
        
        Thread(target=load_info).start()

    async def send_request(self):
        request_data = self.request_entry.get()
        name = self.api_options.get()
        try:
            with open(os.path.join('apis', name), 'r') as api_file:
                api_data = json.load(api_file)
                url = api_data.get('url')
                params = json.loads(request_data) if request_data else None
                async with aiohttp.ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        response_text = await response.text()
                        self.view_response(response_text)
        except (FileNotFoundError, json.JSONDecodeError, aiohttp.ClientError) as e:
            messagebox.showerror("Error", str(e))

    def view_response(self, response_text):
        response_window = tk.Toplevel(self.root)
        response_window.title("API Response")
        response_window.geometry("600x400")

        response_text_widget = tk.Text(response_window, height=20, width=50, wrap='word')
        response_text_widget.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        response_text_widget.tag_configure("link", foreground="pink", underline=True)
        response_text_widget.tag_bind("link", "<Button-1>", self.open_link)

        formatted_response = self.prettify_json(response_text)
        self.insert_links(response_text_widget, formatted_response)

        save_btn = tk.Button(response_window, text="Save", command=lambda: Thread(target=self.save_response, args=(formatted_response,)).start())
        save_btn.pack(pady=5)

        open_browser_btn = tk.Button(response_window, text="Open in Browser", command=lambda: Thread(target=self.open_in_browser, args=(formatted_response,)).start())
        open_browser_btn.pack(pady=5)

    def prettify_json(self, response_text):
        try:
            response_json = json.loads(response_text)
            pretty_json = json.dumps(response_json, indent=4)
            return pretty_json
        except json.JSONDecodeError:
            return response_text

    def insert_links(self, text_widget, text):
        url_pattern = re.compile(r'(https?://[^\s"\'<>]+)')
        last_end = 0
        for match in url_pattern.finditer(text):
            start, end = match.span()
            text_widget.insert(tk.END, text[last_end:start])
            text_widget.insert(tk.END, match.group(0), ("link",))
            last_end = end
        text_widget.insert(tk.END, text[last_end:])

    def open_link(self, event):
        text_widget = event.widget
        idx = text_widget.index(tk.CURRENT)
        tag_indices = text_widget.tag_ranges("link")
        for start, end in zip(tag_indices[0::2], tag_indices[1::2]):
            if text_widget.compare(start, "<=", idx) and text_widget.compare(idx, "<=", end):
                url = text_widget.get(start, end)
                webbrowser.open(url)
                return

    def save_response(self, response_text):
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, 'w') as file:
                file.write(response_text)

    def open_in_browser(self, response_text):
        temp_file = "temp_response.html"
        with open(temp_file, 'w') as file:
            file.write(f"<pre>{response_text}</pre>")
        webbrowser.open(temp_file)

    def open_add_window(self):
        add_window = tk.Toplevel(self.root)
        add_window.title("Add API")
        add_window.geometry("500x300")

        tk.Label(add_window, text="Name:").grid(row=0, column=0, sticky='w', padx=10, pady=2)
        name_entry = tk.Entry(add_window)
        name_entry.grid(row=0, column=1, sticky='ew', padx=10, pady=5)

        tk.Label(add_window, text="Description:").grid(row=1, column=0, sticky='w', padx=10, pady=2)
        desc_entry = tk.Text(add_window, height=5, width=30, wrap='word')
        desc_entry.grid(row=1, column=1, sticky='nsew', padx=10, pady=5)

        tk.Label(add_window, text="Request (JSON):").grid(row=2, column=0, sticky='w', padx=10, pady=2)
        req_entry = tk.Entry(add_window)
        req_entry.grid(row=2, column=1, sticky='ew', padx=10, pady=5)

        tk.Label(add_window, text="API URL:").grid(row=3, column=0, sticky='w', padx=10, pady=2)
        url_entry = tk.Entry(add_window)
        url_entry.insert(0, "https://")
        url_entry.grid(row=3, column=1, sticky='ew', padx=10, pady=5)

        save_btn = tk.Button(add_window, text="Save", command=lambda: Thread(target=self.save_api, args=(name_entry.get(), desc_entry.get("1.0", "end-1c"), req_entry.get(), url_entry.get(), add_window)).start())
        save_btn.grid(row=5, column=0, columnspan=2, pady=5)

        add_window.grid_columnconfigure(1, weight=1)
        add_window.grid_rowconfigure(1, weight=1)

        asyncio.run(self.tooltip(name_entry, "Enter a unique name for the API."))
        asyncio.run(self.tooltip(desc_entry, "Enter a description or help text for the API."))
        asyncio.run(self.tooltip(req_entry, f"Enter the request format in JSON.\n\n{self.explainjson}"))
        asyncio.run(self.tooltip(url_entry, "Enter the URL for the API endpoint."))

    def open_edit_window(self):
        name = self.api_options.get()
        try:
            with open(os.path.join('apis', name), 'r') as api_file:
                api_data = json.load(api_file)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            messagebox.showerror("Error", str(e))
            return

        edit_window = tk.Toplevel(self.root)
        edit_window.title("Edit API")
        edit_window.geometry("500x300")

        tk.Label(edit_window, text="Name:").grid(row=0, column=0, sticky='w', padx=10, pady=2)
        name_entry = tk.Entry(edit_window)
        name_entry.grid(row=0, column=1, sticky='ew', padx=10, pady=5)
        name_entry.insert(0, name)
        name_entry.config(state='disabled')  # API file renaming is not supported *yet*

        tk.Label(edit_window, text="Description:").grid(row=1, column=0, sticky='w', padx=10, pady=2)
        desc_entry = tk.Text(edit_window, height=5, width=30, wrap='word')
        desc_entry.grid(row=1, column=1, sticky='nsew', padx=10, pady=5)
        desc_entry.insert('1.0', api_data.get('help', ''))

        tk.Label(edit_window, text="Request (JSON):").grid(row=2, column=0, sticky='w', padx=10, pady=2)
        req_entry = tk.Entry(edit_window)
        req_entry.grid(row=2, column=1, sticky='ew', padx=10, pady=5)
        req_entry.insert(0, api_data.get('req', ''))

        tk.Label(edit_window, text="API URL:").grid(row=3, column=0, sticky='w', padx=10, pady=2)
        url_entry = tk.Entry(edit_window)
        url_entry.grid(row=3, column=1, sticky='ew', padx=10, pady=5)
        url_entry.insert(0, api_data.get('url', ''))

        save_btn = tk.Button(edit_window, text="Save", command=lambda: Thread(target=self.save_api, args=(name, desc_entry.get("1.0", "end-1c"), req_entry.get(), url_entry.get(), edit_window)).start())
        save_btn.grid(row=4, column=0, columnspan=2, pady=5)

        edit_window.grid_columnconfigure(1, weight=1)
        edit_window.grid_rowconfigure(1, weight=1)
        
        # Add tooltips
        asyncio.run(self.tooltip(desc_entry, "Enter a description or help text for the API."))
        asyncio.run(self.tooltip(req_entry, f"Enter the request format in JSON.\n\n{self.explainjson}"))
        asyncio.run(self.tooltip(url_entry, "Enter the URL for the API endpoint."))

    def save_api(self, name, desc, req, url, window):
        # Save new API to file
        if name:
            api_data = {
                'help': desc,
                'req': req,
                'url': url
            }
            with open(os.path.join('apis', name), 'w') as api_file:
                json.dump(api_data, api_file)
            window.destroy()
            self.load_apis()  # Reload the APIs and update the dropdown menu
        else:
            messagebox.showerror("Error", "API name is required")

    async def tooltip(self, widget, text):
        tooltip = tk.Toplevel(widget, padx=1, pady=1)
        tooltip.withdraw()
        tooltip.overrideredirect(True)
        tooltip.wm_attributes('-alpha', 0)
        label = tk.Label(tooltip, text=text, justify='left', relief='solid', borderwidth=1, wraplength=350)
        label.pack()

        def enter(event):
            x, y, _, _ = widget.bbox("insert")
            x += widget.winfo_rootx() - 1500
            y += widget.winfo_rooty() - 1500
            tooltip.geometry(f"+{x+10}+{y+10}") # This makes the tooltip LESS jumpy. else it renders top left before following the mouse
            tooltip.wm_attributes('-alpha', 0)
            tooltip.deiconify()

        def leave(event):
            tooltip.wm_attributes('-alpha', 0)
            tooltip.withdraw()

        def motion(event):
            x, y = event.x_root, event.y_root
            tooltip.geometry(f"+{x+5}+{y+20}")
            tooltip.wm_attributes('-alpha', 0.8)

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)
        widget.bind("<Motion>", motion)

if __name__ == "__main__":
    root = tk.Tk()
    app = APIDR(root)
    root.mainloop()
