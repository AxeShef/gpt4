import sys
import json
import os
from datetime import datetime
print("Python version:", sys.version)

try:
    import tkinter as tk
    from tkinter import filedialog
    print("Tkinter version:", tk.TkVersion)
except Exception as e:
    print("Ошибка импорта tkinter:", str(e))
    input("Нажмите Enter для выхода...")
    sys.exit(1)

try:
    import customtkinter as ctk
    print("CustomTkinter version:", ctk.__version__)
except Exception as e:
    print("Ошибка импорта customtkinter:", str(e))
    input("Нажмите Enter для выхода...")
    sys.exit(1)

try:
    import g4f
    # Отключаем предупреждения
    g4f.debug.logging = False
    # Получаем список рабочих провайдеров
    AVAILABLE_PROVIDERS = [
        provider for provider in g4f.Provider.__providers__ 
        if provider.working and not getattr(provider, 'needs_auth', False)
    ]
    print("Доступные провайдеры:", [provider.__name__ for provider in AVAILABLE_PROVIDERS])
except Exception as e:
    print("Ошибка импорта g4f:", str(e))
    input("Нажмите Enter для выхода...")
    sys.exit(1)

from tkinter import messagebox
import threading
print("Все необходимые библиотеки успешно импортированы")

print("Запуск приложения Free GPT Чат...")

try:
    class GPTChatApp:
        def __init__(self):
            print("Инициализация окна приложения...")
            self.window = ctk.CTk()
            self.window.title("Free GPT Чат")
            # Увеличиваем минимальный размер окна
            self.window.geometry("1200x800")
            self.window.minsize(1000, 700)
            
            # Устанавливаем темную тему по умолчанию
            ctk.set_appearance_mode("dark")
            ctk.set_default_color_theme("blue")
            
            # Настройки
            self.font_size = 12
            self.message_count = 0
            
            # Создаем главный контейнер с увеличенными отступами
            self.main_container = ctk.CTkFrame(self.window)
            self.main_container.pack(fill="both", expand=True, padx=30, pady=20)
            
            # Создаем верхнюю панель с элементами управления
            self.controls_frame = ctk.CTkFrame(self.main_container)
            self.controls_frame.pack(fill="x", pady=(0, 15))
            
            # Левая часть контролов
            self.left_controls = ctk.CTkFrame(self.controls_frame)
            self.left_controls.pack(side="left", fill="x", expand=True)
            
            # Добавляем выбор провайдера
            self.provider_label = ctk.CTkLabel(self.left_controls, text="Провайдер:", font=("Arial", 12, "bold"))
            self.provider_label.pack(side="left", padx=10)
            
            self.providers = AVAILABLE_PROVIDERS
            self.provider_var = ctk.StringVar(value=self.providers[0].__name__)
            self.provider_menu = ctk.CTkOptionMenu(
                self.left_controls,
                values=[p.__name__ for p in self.providers],
                variable=self.provider_var,
                width=200
            )
            self.provider_menu.pack(side="left", padx=10)

            # Добавляем счетчик сообщений
            self.message_counter = ctk.CTkLabel(
                self.left_controls,
                text="Сообщений: 0",
                font=("Arial", 12)
            )
            self.message_counter.pack(side="left", padx=20)
            
            # Правая часть контролов
            self.right_controls = ctk.CTkFrame(self.controls_frame)
            self.right_controls.pack(side="right", fill="x", padx=10)
            
            # Кнопки в одном ряду
            self.save_button = ctk.CTkButton(
                self.right_controls,
                text="Сохранить чат",
                command=self.save_chat,
                width=120,
                height=35
            )
            self.save_button.pack(side="left", padx=2)
            
            self.load_button = ctk.CTkButton(
                self.right_controls,
                text="Загрузить чат",
                command=self.load_chat,
                width=120,
                height=35
            )
            self.load_button.pack(side="left", padx=2)
            
            self.clear_button = ctk.CTkButton(
                self.right_controls,
                text="Очистить чат",
                command=self.clear_chat,
                width=120,
                height=35
            )
            self.clear_button.pack(side="left", padx=2)
            
            self.font_increase_button = ctk.CTkButton(
                self.right_controls,
                text="Увеличение",
                command=self.increase_font_size,
                width=100,
                height=35
            )
            self.font_increase_button.pack(side="left", padx=2)
            
            self.font_decrease_button = ctk.CTkButton(
                self.right_controls,
                text="Уменьшение",
                command=self.decrease_font_size,
                width=100,
                height=35
            )
            self.font_decrease_button.pack(side="left", padx=2)
            
            self.theme_button = ctk.CTkButton(
                self.right_controls,
                text="Сменить тему",
                command=self.toggle_theme,
                width=120,
                height=35
            )
            self.theme_button.pack(side="left", padx=2)
            
            # Область чата с увеличенными отступами
            self.chat_frame = ctk.CTkFrame(self.main_container)
            self.chat_frame.pack(fill="both", expand=True, pady=(0, 15))
            
            self.chat_display = ctk.CTkTextbox(
                self.chat_frame,
                wrap="word",
                font=("Arial", self.font_size),
                height=400
            )
            self.chat_display.pack(fill="both", expand=True, padx=15, pady=15)
            
            # Добавляем контекстное меню для копирования текста
            self.context_menu = tk.Menu(self.window, tearoff=0)
            self.context_menu.add_command(label="Копировать", command=self.copy_selected_text)
            self.chat_display.bind("<Button-3>", self.show_context_menu)
            
            # Область ввода сообщения
            self.input_frame = ctk.CTkFrame(self.main_container)
            self.input_frame.pack(fill="x")
            
            self.message_entry = ctk.CTkEntry(
                self.input_frame,
                placeholder_text="Введите ваше сообщение...",
                font=("Arial", self.font_size),
                height=40
            )
            self.message_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
            
            self.send_button = ctk.CTkButton(
                self.input_frame,
                text="Отправить",
                command=self.send_message,
                width=120,
                height=40,
                font=("Arial", 12, "bold")
            )
            self.send_button.pack(side="right")

            # Индикатор загрузки
            self.progress_bar = ctk.CTkProgressBar(self.main_container)
            self.progress_bar.set(0)
            self.progress_bar.pack(fill="x", pady=(5, 0))
            self.progress_bar.pack_forget()  # Скрываем до использования

            # Привязываем Enter к отправке сообщения
            self.message_entry.bind('<Return>', lambda e: self.send_message())
            
            # Статус бар
            self.status_bar = ctk.CTkLabel(
                self.main_container,
                text="Готов к работе",
                font=("Arial", 11),
                height=25
            )
            self.status_bar.pack(fill="x", pady=(10, 0))
            
            print("Окно приложения успешно инициализировано")

            # История сообщений
            self.messages = []
            
            # Текущая тема
            self.is_dark_theme = True

        def show_context_menu(self, event):
            """Показывает контекстное меню при правом клике"""
            self.context_menu.post(event.x_root, event.y_root)

        def copy_selected_text(self):
            """Копирует выделенный текст в буфер обмена"""
            try:
                selected_text = self.chat_display.selection_get()
                self.window.clipboard_clear()
                self.window.clipboard_append(selected_text)
                self.update_status("Текст скопирован")
            except:
                self.update_status("Нет выделенного текста")

        def increase_font_size(self):
            """Увеличивает размер шрифта"""
            sizes = [10, 12, 14, 16, 18, 20]
            current_index = sizes.index(self.font_size) if self.font_size in sizes else 0
            if current_index < len(sizes) - 1:
                self.font_size = sizes[current_index + 1]
                self.chat_display.configure(font=("Arial", self.font_size))
                self.message_entry.configure(font=("Arial", self.font_size))
                self.update_status(f"Размер шрифта: {self.font_size}")

        def decrease_font_size(self):
            """Уменьшает размер шрифта"""
            sizes = [10, 12, 14, 16, 18, 20]
            current_index = sizes.index(self.font_size) if self.font_size in sizes else 0
            if current_index > 0:
                self.font_size = sizes[current_index - 1]
                self.chat_display.configure(font=("Arial", self.font_size))
                self.message_entry.configure(font=("Arial", self.font_size))
                self.update_status(f"Размер шрифта: {self.font_size}")

        def save_chat(self):
            """Сохраняет историю чата в файл"""
            try:
                filename = f"chat_history_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = filedialog.asksaveasfilename(
                    defaultextension=".json",
                    initialfile=filename,
                    filetypes=[("JSON files", "*.json")]
                )
                if filepath:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(self.messages, f, ensure_ascii=False, indent=2)
                    self.update_status("Чат сохранен")
            except Exception as e:
                self.update_status(f"Ошибка при сохранении: {str(e)}")

        def load_chat(self):
            """Загружает историю чата из файла"""
            try:
                filepath = filedialog.askopenfilename(
                    filetypes=[("JSON files", "*.json")]
                )
                if filepath:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        self.messages = json.load(f)
                    self.clear_chat()
                    for msg in self.messages:
                        if msg["role"] == "user":
                            self.chat_display.insert("end", f"Вы: {msg['content']}\n")
                        else:
                            self.chat_display.insert("end", f"AI: {msg['content']}\n\n")
                    self.chat_display.see("end")
                    self.message_count = len(self.messages)
                    self.update_message_counter()
                    self.update_status("Чат загружен")
            except Exception as e:
                self.update_status(f"Ошибка при загрузке: {str(e)}")

        def update_message_counter(self):
            """Обновляет счетчик сообщений"""
            self.message_counter.configure(text=f"Сообщений: {self.message_count}")

        def toggle_theme(self):
            """Переключает тему приложения"""
            if self.is_dark_theme:
                ctk.set_appearance_mode("light")
                self.is_dark_theme = False
            else:
                ctk.set_appearance_mode("dark")
                self.is_dark_theme = True

        def clear_chat(self):
            """Очищает чат и историю сообщений"""
            self.chat_display.delete("0.0", "end")
            self.messages = []
            self.update_status("Чат очищен")

        def update_status(self, text):
            """Обновляет текст в статус баре"""
            self.status_bar.configure(text=text)
            self.window.update()

        def send_message(self):
            message = self.message_entry.get().strip()
            if not message:
                return

            # Сначала очищаем поле ввода
            self.message_entry.delete(0, "end")
            
            # Отключаем кнопку отправки и поле ввода
            self.send_button.configure(state="disabled")
            self.message_entry.configure(state="disabled")
            self.update_status("Отправка сообщения...")

            # Показываем индикатор загрузки
            self.progress_bar.pack(fill="x", pady=(5, 0))
            self.progress_bar.start()

            # Добавляем сообщение пользователя в чат
            self.chat_display.insert("end", f"Вы: {message}\n")
            self.chat_display.see("end")

            # Обновляем счетчик сообщений
            self.message_count += 1
            self.update_message_counter()

            # Добавляем сообщение в историю
            self.messages.append({"role": "user", "content": message})

            # Создаем отдельный поток для запроса к API
            thread = threading.Thread(target=self._get_ai_response)
            thread.daemon = True
            thread.start()

        def _get_ai_response(self):
            """Получает ответ от AI в отдельном потоке"""
            try:
                # Получаем выбранного провайдера
                provider_name = self.provider_var.get()
                provider = next((p for p in self.providers if p.__name__ == provider_name), None)
                
                if not provider:
                    raise ValueError(f"Провайдер {provider_name} не найден")

                self.update_status(f"Ожидание ответа от {provider_name}...")

                # Создаем сообщения для отправки
                messages = []
                for msg in self.messages[-5:]:  # Берем только последние 5 сообщений для контекста
                    messages.append(msg)

                # Получаем ответ от модели
                response = g4f.ChatCompletion.create(
                    model=None,  # Позволяем провайдеру выбрать модель по умолчанию
                    provider=provider,
                    messages=messages,
                    stream=False
                )

                if not response:
                    raise Exception("Пустой ответ от провайдера")

                # Добавляем ответ в чат
                self.chat_display.insert("end", f"AI: {response}\n\n")
                self.chat_display.see("end")

                # Добавляем ответ в историю
                self.messages.append({"role": "assistant", "content": response})
                
                # Обновляем счетчик сообщений
                self.message_count += 1
                self.update_message_counter()

                self.update_status("Готов к работе")

            except Exception as e:
                error_msg = f"Ошибка: {str(e)}"
                self.chat_display.insert("end", f"Системное сообщение: {error_msg}\n\n")
                self.chat_display.see("end")
                self.update_status(f"Ошибка: {str(e)}")
                
                # Если провайдер не работает, пробуем другого
                current_provider = next((p for p in self.providers if p.__name__ == self.provider_var.get()), None)
                if current_provider in self.providers:
                    self.providers.remove(current_provider)
                if self.providers:
                    self.provider_var.set(self.providers[0].__name__)
                    self.provider_menu.configure(values=[p.__name__ for p in self.providers])
                    self.chat_display.insert("end", "Системное сообщение: Переключение на другого провайдера...\n\n")
                    self.chat_display.see("end")
                else:
                    self.chat_display.insert("end", "Системное сообщение: Нет доступных провайдеров.\n\n")
                    self.chat_display.see("end")

            finally:
                # Скрываем индикатор загрузки
                self.progress_bar.stop()
                self.progress_bar.pack_forget()
                
                # Включаем кнопку отправки и поле ввода обратно
                self.send_button.configure(state="normal")
                self.message_entry.configure(state="normal")
                self.message_entry.focus()

        def run(self):
            print("Запуск главного цикла приложения...")
            self.window.mainloop()

    if __name__ == "__main__":
        try:
            print("Создание экземпляра приложения...")
            app = GPTChatApp()
            app.run()
        except Exception as e:
            print(f"Произошла ошибка при запуске приложения: {str(e)}")
            input("Нажмите Enter для выхода...")
except Exception as e:
    print(f"Критическая ошибка: {str(e)}")
    input("Нажмите Enter для выхода...") 