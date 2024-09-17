from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import os

# Configuração do perfil do Chrome
options = Options()
options.binary_location = 'C:/Program Files/Google/Chrome/Application/chrome.exe'  # Caminho correto do Chrome
options.add_experimental_option("excludeSwitches", ["enable-logging"])
options.add_argument("--profile-directory=Default")  # Usa o perfil padrão do Chrome
options.add_argument("--user-data-dir=/var/tmp/chrome_user_data")  # Caminho do diretório de dados do usuário

# Inicializa o WebDriver
driver = webdriver.Chrome(options=options)

# Função para abrir os links e remover o utilizado
def abrir_links():
    with open('telefones.txt', 'r') as file:
        lines = file.readlines()

    for line in lines:
        link = line.strip()  # Remove espaços extras ou quebras de linha
        if link:
            # Abre o link no WhatsApp Web
            driver.get(link)
            print(f'Abrindo link: {link}')

            # Espera a página carregar (ajuste conforme necessário)
            time.sleep(14)  # Aguarda 10 segundos (pode ajustar conforme a velocidade de sua conexão)

            # Após abrir o link, remover da lista
            with open('telefones.txt', 'w') as file:
                # Escreve todas as linhas, exceto a que foi usada
                file.writelines(lines[1:])
                print(f'Removendo link: {link}')

            # Atualiza a lista para o próximo loop
            lines = lines[1:]

    print("Todos os links foram abertos e removidos.")

# Executa a função para abrir os links
abrir_links()

# Fecha o WebDriver ao final
driver.quit()
