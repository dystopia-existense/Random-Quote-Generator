import tkinter as tk
from tkinter import ttk, messagebox
import random
import json
import os

# --- Константы и файлы ---
HISTORY_FILE = "quotes_history.json"   # история сгенерированных цитат
POOL_FILE = "quotes_pool.json"         # полный пул цитат (предопределённые + пользовательские)

# Предопределённый список цитат (текст, автор, тема)
DEFAULT_QUOTES = [
    {"text": "Будь переменой, которую хочешь видеть в мире.", "author": "Махатма Ганди", "topic": "Мотивация"},
    {"text": "Не ошибается лишь тот, кто ничего не делает.", "author": "Теодор Рузвельт", "topic": "Ошибки"},
    {"text": "Сложнее всего начать действовать, всё остальное зависит только от упорства.", "author": "Амелия Эрхарт", "topic": "Действие"},
    {"text": "Лучшее время посадить дерево было 20 лет назад. Второе лучшее время — сегодня.", "author": "Китайская пословица", "topic": "Время"},
    {"text": "Ваше время ограничено, не тратьте его, живя чужой жизнью.", "author": "Стив Джобс", "topic": "Жизнь"},
    {"text": "Логика приведёт вас из пункта А в пункт Б. Воображение приведёт вас куда угодно.", "author": "Альберт Эйнштейн", "topic": "Творчество"},
    {"text": "Успех — это способность шагать от неудачи к неудаче, не теряя энтузиазма.", "author": "Уинстон Черчилль", "topic": "Успех"},
    {"text": "Всё, что вы можете вообразить, реально.", "author": "Пабло Пикассо", "topic": "Творчество"},
    {"text": "Счастье — это не готовая вещь. Оно проистекает из ваших собственных действий.", "author": "Далай-лама", "topic": "Счастье"},
    {"text": "Самая большая глупость — делать то же самое и надеяться на другой результат.", "author": "Альберт Эйнштейн", "topic": "Мудрость"},
]

class QuoteGeneratorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Random Quote Generator")
        self.root.geometry("700x650")
        self.root.resizable(True, True)

        # Загрузка данных
        self.quote_pool = self.load_quote_pool()      # полный список доступных цитат
        self.history = self.load_history()            # список сгенерированных цитат
        self.filtered_history = list(self.history)    # отфильтрованный список для отображения

        # Переменные для фильтрации
        self.filter_author = tk.StringVar(value="Все")
        self.filter_topic = tk.StringVar(value="Все")

        # Построение GUI
        self.setup_ui()
        self.update_history_display()
        self.populate_filter_combos()

        # Автосохранение при закрытии окна
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    # ------------------- Работа с файлами -------------------
    def load_quote_pool(self):
        """Загружает пул цитат из JSON, если файл существует, иначе использует DEFAULT_QUOTES."""
        if os.path.exists(POOL_FILE):
            try:
                with open(POOL_FILE, "r", encoding="utf-8") as f:
                    pool = json.load(f)
                if isinstance(pool, list) and len(pool) > 0:
                    return pool
            except (json.JSONDecodeError, IOError):
                pass
        # Возвращаем копию предопределённых цитат
        return list(DEFAULT_QUOTES)

    def save_quote_pool(self):
        """Сохраняет текущий пул цитат в файл."""
        try:
            with open(POOL_FILE, "w", encoding="utf-8") as f:
                json.dump(self.quote_pool, f, ensure_ascii=False, indent=4)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить пул цитат: {e}")

    def load_history(self):
        """Загружает историю сгенерированных цитат."""
        if os.path.exists(HISTORY_FILE):
            try:
                with open(HISTORY_FILE, "r", encoding="utf-8") as f:
                    hist = json.load(f)
                if isinstance(hist, list):
                    return hist
            except (json.JSONDecodeError, IOError):
                pass
        return []

    def save_history(self):
        """Сохраняет историю в JSON."""
        try:
            with open(HISTORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.history, f, ensure_ascii=False, indent=4)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {e}")

    # ------------------- UI -------------------
    def setup_ui(self):
        # Верхняя панель – генерация цитаты
        gen_frame = ttk.LabelFrame(self.root, text="Генератор цитат", padding=10)
        gen_frame.pack(fill="x", padx=10, pady=5)

        self.quote_display = tk.Text(gen_frame, height=4, wrap="word", state="disabled",
                                     font=("Arial", 11), bg="#f0f0f0")
        self.quote_display.pack(fill="x", pady=5)

        btn_gen = ttk.Button(gen_frame, text="Сгенерировать цитату", command=self.generate_random_quote)
        btn_gen.pack(pady=5)

        # Панель добавления новой цитаты
        add_frame = ttk.LabelFrame(self.root, text="Добавить новую цитату", padding=10)
        add_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(add_frame, text="Текст цитаты:").grid(row=0, column=0, sticky="w")
        self.new_text = tk.Text(add_frame, height=2, width=60, font=("Arial", 10))
        self.new_text.grid(row=0, column=1, padx=5, pady=2, sticky="ew")

        ttk.Label(add_frame, text="Автор:").grid(row=1, column=0, sticky="w")
        self.new_author = ttk.Entry(add_frame, width=40)
        self.new_author.grid(row=1, column=1, padx=5, pady=2, sticky="w")

        ttk.Label(add_frame, text="Тема:").grid(row=2, column=0, sticky="w")
        self.new_topic = ttk.Entry(add_frame, width=40)
        self.new_topic.grid(row=2, column=1, padx=5, pady=2, sticky="w")

        btn_add = ttk.Button(add_frame, text="Добавить цитату в пул", command=self.add_new_quote)
        btn_add.grid(row=3, column=1, pady=5, sticky="e")

        add_frame.columnconfigure(1, weight=1)

        # Панель фильтрации истории
        filter_frame = ttk.LabelFrame(self.root, text="Фильтрация истории", padding=10)
        filter_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(filter_frame, text="Автор:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.combo_author = ttk.Combobox(filter_frame, textvariable=self.filter_author,
                                         state="readonly", width=25)
        self.combo_author.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.combo_author.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        ttk.Label(filter_frame, text="Тема:").grid(row=0, column=2, padx=5, pady=5, sticky="w")
        self.combo_topic = ttk.Combobox(filter_frame, textvariable=self.filter_topic,
                                        state="readonly", width=25)
        self.combo_topic.grid(row=0, column=3, padx=5, pady=5, sticky="w")
        self.combo_topic.bind("<<ComboboxSelected>>", lambda e: self.apply_filter())

        btn_clear_filter = ttk.Button(filter_frame, text="Сбросить фильтр", command=self.reset_filter)
        btn_clear_filter.grid(row=0, column=4, padx=10, pady=5)

        # История цитат (список)
        hist_frame = ttk.LabelFrame(self.root, text="История сгенерированных цитат", padding=10)
        hist_frame.pack(fill="both", expand=True, padx=10, pady=5)

        scrollbar = ttk.Scrollbar(hist_frame)
        scrollbar.pack(side="right", fill="y")

        self.history_listbox = tk.Listbox(hist_frame, yscrollcommand=scrollbar.set,
                                          font=("Courier New", 9), activestyle="none")
        self.history_listbox.pack(fill="both", expand=True)
        scrollbar.config(command=self.history_listbox.yview)

        # Нижние кнопки управления
        ctrl_frame = ttk.Frame(self.root)
        ctrl_frame.pack(fill="x", padx=10, pady=5)

        ttk.Button(ctrl_frame, text="Сохранить историю", command=self.save_history).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Загрузить историю заново", command=self.reload_history).pack(side="left", padx=5)
        ttk.Button(ctrl_frame, text="Очистить историю", command=self.clear_history).pack(side="left", padx=5)

    # ------------------- Логика -------------------
    def generate_random_quote(self):
        if not self.quote_pool:
            messagebox.showwarning("Пустой пул", "Нет доступных цитат. Добавьте хотя бы одну.")
            return
        quote = random.choice(self.quote_pool)
        # Добавляем в историю с отметкой времени (для наглядности можно добавить дату, но не требуем)
        self.history.append(quote)
        self.update_history_display()
        self.populate_filter_combos()

        # Показываем сгенерированную цитату в текстовом поле
        self.quote_display.config(state="normal")
        self.quote_display.delete("1.0", tk.END)
        self.quote_display.insert("1.0", f'«{quote["text"]}»\n— {quote["author"]} ({quote["topic"]})')
        self.quote_display.config(state="disabled")

    def add_new_quote(self):
        text = self.new_text.get("1.0", tk.END).strip()
        author = self.new_author.get().strip()
        topic = self.new_topic.get().strip()

        # Валидация: текст не должен быть пустым
        if not text:
            messagebox.showwarning("Ошибка ввода", "Текст цитаты не может быть пустым.")
            return
        # Если автор или тема не указаны, задаём значения по умолчанию
        if not author:
            author = "Неизвестный автор"
        if not topic:
            topic = "Без темы"

        new_quote = {"text": text, "author": author, "topic": topic}
        self.quote_pool.append(new_quote)
        self.save_quote_pool()

        # Очистка полей ввода
        self.new_text.delete("1.0", tk.END)
        self.new_author.delete(0, tk.END)
        self.new_topic.delete(0, tk.END)

        messagebox.showinfo("Успех", "Цитата добавлена в общий пул.")

    def update_history_display(self):
        """Обновляет Listbox в соответствии с отфильтрованной историей."""
        self.history_listbox.delete(0, tk.END)
        for i, q in enumerate(self.filtered_history, start=1):
            line = f"{i}. «{q['text'][:60]}{'...' if len(q['text'])>60 else ''}» — {q['author']} [{q['topic']}]"
            self.history_listbox.insert(tk.END, line)

    def apply_filter(self):
        author_sel = self.filter_author.get()
        topic_sel = self.filter_topic.get()
        self.filtered_history = [
            q for q in self.history
            if (author_sel == "Все" or q["author"] == author_sel) and
               (topic_sel == "Все" or q["topic"] == topic_sel)
        ]
        self.update_history_display()

    def reset_filter(self):
        self.filter_author.set("Все")
        self.filter_topic.set("Все")
        self.filtered_history = list(self.history)
        self.update_history_display()

    def populate_filter_combos(self):
        """Заполняет выпадающие списки уникальными авторами и темами из истории."""
        authors = sorted({q["author"] for q in self.history})
        topics = sorted({q["topic"] for q in self.history})

        # Добавляем опцию "Все"
        authors.insert(0, "Все")
        topics.insert(0, "Все")

        self.combo_author["values"] = authors
        self.combo_topic["values"] = topics

        # Если текущее значение отсутствует в новом списке, сбрасываем на "Все"
        if self.filter_author.get() not in authors:
            self.filter_author.set("Все")
        if self.filter_topic.get() not in topics:
            self.filter_topic.set("Все")
        # Применяем фильтр с учётом возможного сброса
        self.apply_filter()

    def reload_history(self):
        """Перезагружает историю из файла (на случай, если файл изменился)."""
        self.history = self.load_history()
        self.filtered_history = list(self.history)
        self.populate_filter_combos()
        self.update_history_display()

    def clear_history(self):
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history.clear()
            self.filtered_history.clear()
            self.update_history_display()
            self.populate_filter_combos()
            self.save_history()

    def on_close(self):
        """Обработчик закрытия окна: сохраняем историю и пул."""
        self.save_history()
        self.save_quote_pool()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = QuoteGeneratorApp(root)
    root.mainloop()