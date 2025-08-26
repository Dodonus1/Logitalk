import threading
from socket import *
from customtkinter import *



class MainWindow(CTk):
    def __init__(self):
        super().__init__()
        self.geometry('1080x890')
        self.title('LogiTalk')
        self.current_color = "White"


        self.HOST = 'localhost'
        self.PORT = 8080
        self.socket = None
        self.connected = False
        self.setup_ui()


        self.connect_to_server()

    def setup_ui(self):

        self.side_panel = CTkFrame(self, width=250, height=890)
        self.side_panel.place(x=0, y=0)


        self.chat_field = CTkTextbox(self, font=('Arial', 14), state='disabled', width=800, height=700)
        self.chat_field.place(x=260, y=20)


        self.message_entry = CTkEntry(self, placeholder_text='Введіть повідомлення...', width=700, height=50)
        self.message_entry.place(x=260, y=730)
        self.message_entry.bind('<Return>', lambda e: self.send_message())


        self.send_button = CTkButton(self, text='Надіслати', width=100, height=50, command=self.send_message)
        self.send_button.place(x=970, y=730)


        self.status_label = CTkLabel(self, text="Не підключено", anchor="w", width=800)
        self.status_label.place(x=260, y=790)


        self.setup_side_panel()

    def setup_side_panel(self):

        CTkLabel(self.side_panel, text="Ваше ім'я:").place(x=10, y=20)

        self.name_entry = CTkEntry(self.side_panel, width=230)
        self.name_entry.place(x=10, y=50)
        self.name_entry.insert(0, "Гість")

        CTkButton(
            self.side_panel,
            text="Зберегти ім'я",
            width=230,
            command=self.change_name
        ).place(x=10, y=90)


        CTkLabel(self.side_panel, text="Колір тексту:").place(x=10, y=140)

        colors = [("Білий", "White"), ("Червоний", "Red"), ("Синій", "Blue")]
        self.color_var = StringVar(value="White")

        for i, (name, color) in enumerate(colors):
            CTkRadioButton(
                self.side_panel,
                text=name,
                variable=self.color_var,
                value=color,
                command=self.change_color
            ).place(x=10, y=170 + i * 40)

    def connect_to_server(self):
        try:
            self.socket = socket(AF_INET, SOCK_STREAM)
            self.socket.connect((self.HOST, self.PORT))
            self.connected = True
            self.status_label.configure(text="Підключено до сервера", text_color="green")


            threading.Thread(target=self.receive_messages, daemon=True).start()


            self.send_system_message(f"{self.name_entry.get()} приєднався до чату")
        except Exception as e:
            self.status_label.configure(text=f"Помилка підключення: {str(e)}", text_color="red")

    def receive_messages(self):
        while self.connected:
            try:
                data = self.socket.recv(4096).decode()
                if not data:
                    break

                for line in data.split('\n'):
                    if line:
                        self.display_message(line)
            except Exception as e:
                print(f"Помилка отримання: {str(e)}")
                break

        self.connected = False
        self.status_label.configure(text="Відключено від сервера", text_color="red")

    def display_message(self, message):
        parts = message.split('@', 2)
        if len(parts) < 3:
            return

        msg_type, sender, content = parts

        if msg_type == "MESSAGE":
            self.add_to_chat(f"{sender}: {content}")
        elif msg_type == "SYSTEM":
            self.add_to_chat(f"[Система] {content}", "orange")

    def send_message(self):
        message = self.message_entry.get().strip()
        if not message:
            return

        if not self.connected:
            self.add_to_chat("[Помилка] Немає підключення до сервера", "Red")
            return

        try:

            self.add_to_chat(f"Ви: {message}")


            username = self.name_entry.get()
            data = f"MESSAGE@{username}@{message}\n"
            self.socket.send(data.encode())


            self.message_entry.delete(0, 'end')
        except Exception as e:
            self.connected = False
            self.status_label.configure(text="Помилка відправки", text_color="red")
            self.add_to_chat(f"[Помилка] Не вдалося надіслати повідомлення: {str(e)}", "#FF0000")

    def send_system_message(self, message):
        if self.connected:
            try:
                data = f"SYSTEM@сервер@{message}\n"
                self.socket.send(data.encode())
            except:
                pass

    def change_name(self):
        new_name = self.name_entry.get().strip()
        if new_name and self.connected:
            self.send_system_message(f"Користувач змінив ім'я на {new_name}")
            self.add_to_chat(f"[Система] Ви змінили ім'я на {new_name}", "#FFA500")

    def change_color(self):
        self.current_color = self.color_var.get()

    def add_to_chat(self, message, color=None):
        color = color or self.current_color
        self.chat_field.configure(state='normal')
        tag = f"color_{color}"
        self.chat_field.tag_config(tag, foreground=color)
        self.chat_field.insert('end', message + '\n', tag)
        self.chat_field.configure(state='disabled')
        self.chat_field.see('end')


app = MainWindow()
app.mainloop()