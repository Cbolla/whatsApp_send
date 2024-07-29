import json
import time
from threading import Thread, Event
from tkinter import Tk, StringVar, Label, Entry, Button, filedialog
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from ttkbootstrap import Style
import requests

# Variáveis globais
pause_event = Event()

# Função para carregar as configurações salvas
def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"wait_time": 300, "messages_before_break": 50, "telefones": "", "mensagem": ""}

# Função para salvar as configurações
def save_config(config):
    with open('config.json', 'w') as f:
        json.dump(config, f)

# Função para verificar a chave de acesso
def verify_access_key(key):
    response = requests.get('https://sheetdb.io/api/v1/rzsowr8xfy3f3')
    data = response.json()
    for item in data:
        if item.get("key_zap") == key:
            return True
    return False

# Função para iniciar o navegador e carregar o WhatsApp Web
def start_browser():
    global driver
    options = Options()
    options.binary_location = 'C:/Program Files/Google/Chrome/Application/chrome.exe'  # Substitua pelo caminho correto
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("--profile-directory=Default")
    options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")

    driver = webdriver.Chrome(options=options)
    driver.get('https://web.whatsapp.com')
    print("Escaneie o QR code se necessário e clique no botão de Enviar na interface.")

# Função para enviar mensagens
def send_messages():
    wait_time = int(wait_time_var.get())
    messages_before_break = int(messages_before_break_var.get())
    telefones_file = telefones_var.get()
    mensagem_file = mensagem_var.get()

    with open(mensagem_file, 'r') as file:
        mensagem = file.read().strip()

    count = 0
    while True:
        with open(telefones_file, 'r') as file:
            telefones = file.readlines()

        if not telefones:
            print("Todos os números foram processados.")
            break

        telefone = telefones[0].strip()
        driver.get(f'https://web.whatsapp.com/send?phone={telefone}&text={mensagem}')

        try:
            send_button = WebDriverWait(driver, 30).until(
                EC.presence_of_element_located((By.XPATH, '//span[@data-icon="send"]'))
            )
            send_button.click()
            time.sleep(5)
            count += 1

            # Remover o número usado do arquivo
            with open(telefones_file, 'w') as file:
                file.writelines(telefones[1:])  # Reescrever o arquivo sem a primeira linha

            # Checar se é necessário pausar
            if pause_event.is_set():
                print("Pausado. Clique em Continuar para prosseguir.")
                pause_event.wait()

            if count % messages_before_break == 0:
                print(f"Aguardando {wait_time} segundos antes de continuar...")
                time.sleep(wait_time)
        except Exception as e:
            print(f"Erro ao enviar mensagem para {telefone}: {e}")

    driver.quit()

# Função para selecionar arquivo de telefones
def select_telefones_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    telefones_var.set(file_path)

# Função para selecionar arquivo de mensagem
def select_mensagem_file():
    file_path = filedialog.askopenfilename(filetypes=[("Text Files", "*.txt")])
    mensagem_var.set(file_path)

# Função para iniciar o navegador em uma thread separada
def start_browser_thread():
    browser_thread = Thread(target=start_browser)
    browser_thread.start()

# Função para enviar mensagens em uma thread separada
def send_messages_thread():
    messages_thread = Thread(target=send_messages)
    messages_thread.start()

# Função para verificar a chave de acesso e iniciar o navegador
def verify_and_start_browser():
    access_key = access_key_var.get()
    if verify_access_key(access_key):
        status_var.set("Chave válida! Iniciando...")
        start_browser_thread()
    else:
        status_var.set("Chave inválida! Tente novamente.")

# Função para pausar ou continuar o envio
def toggle_pause():
    if pause_event.is_set():
        pause_event.clear()
        pause_button.config(text="Pausar")
        status_var.set("Continuando...")
    else:
        pause_event.set()
        pause_button.config(text="Continuar")
        status_var.set("Pausado.")

# Carregar configurações iniciais
config = load_config()

# Configurar a interface gráfica
root = Tk()
root.title("WhatsApp Message Sender")
root.geometry("340x400") 
style = Style(theme="darkly")

wait_time_var = StringVar(value=config["wait_time"])
messages_before_break_var = StringVar(value=config["messages_before_break"])
telefones_var = StringVar(value=config.get("telefones", ""))
mensagem_var = StringVar(value=config.get("mensagem", ""))
access_key_var = StringVar()
status_var = StringVar()

Label(root, text="Chave de Acesso:").grid(row=0, column=0, columnspan=3, pady=5)
Entry(root, textvariable=access_key_var, width=50).grid(row=1, column=0, columnspan=3, pady=5)

Label(root, text="Tempo de espera (segundos):").grid(row=2, column=0, columnspan=3, pady=5)
Entry(root, textvariable=wait_time_var, width=50).grid(row=3, column=0, columnspan=3, pady=5)

Label(root, text="Mensagens antes do descanso:").grid(row=4, column=0, columnspan=3, pady=5)
Entry(root, textvariable=messages_before_break_var, width=50).grid(row=5, column=0, columnspan=3, pady=5)

Label(root, text="Arquivo de telefones:").grid(row=6, column=0, columnspan=3, pady=5)
Entry(root, textvariable=telefones_var, width=50).grid(row=7, column=0, columnspan=3, pady=5)
Button(root, text="Selecionar arquivo", command=select_telefones_file, width=15).grid(row=7, column=2, pady=5)

Label(root, text="Arquivo de mensagem:").grid(row=8, column=0, columnspan=3, pady=5)
Entry(root, textvariable=mensagem_var, width=50).grid(row=9, column=0, columnspan=3, pady=5)
Button(root, text="Selecionar arquivo", command=select_mensagem_file, width=15).grid(row=9, column=2, pady=5)

Button(root, text="Iniciar", command=lambda: [verify_and_start_browser(), save_config({"wait_time": int(wait_time_var.get()), "messages_before_break": int(messages_before_break_var.get()), "telefones": telefones_var.get(), "mensagem": mensagem_var.get()})], width=15).grid(row=10, column=0, pady=20)
Button(root, text="Enviar", command=send_messages_thread, width=15).grid(row=10, column=1, pady=20)
pause_button = Button(root, text="Pausar", command=toggle_pause, width=15)
pause_button.grid(row=10, column=2, pady=20)

Label(root, textvariable=status_var).grid(row=11, column=0, columnspan=3, pady=5)

root.mainloop()
