import pygame
import random
import os
import cv2
import pytesseract

# Inicializa o pygame para poder usar a biblioteca
pygame.init()

# Define as dimensões da tela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))

def abrir_imagem(letra):
    # Concatena o caractere com a string 'imagem_' para formar o nome da imagem
    nome_imagem = f"imagem_{letra}.png"
    # Verifica se a imagem existe
    if os.path.exists(f'assets/{nome_imagem}'):
        # Abre a imagem usando a biblioteca pygame
        imagem = pygame.image.load(f'assets/{nome_imagem}').convert_alpha()
        # Define o tamanho da imagem
        tamanho = (100, 100)
        imagem = pygame.transform.scale(imagem, tamanho)
        # Retorna a imagem
        return imagem

    return None

# Carrega uma imagem com palavras manuscritas
img = cv2.imread('palavras.png')

# Verifica se a imagem foi carregada corretamente
if img is None:
    print('Erro ao carregar a imagem.')
else:
    # Converte a imagem em escala de cinza
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Aplica uma limiarização binária para melhorar o contraste
    thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]

    # Usa a biblioteca pytesseract para extrair o texto da imagem
    texto = pytesseract.image_to_string(thresh, lang='por')

    # Imprime o texto extraído
    print(texto)

    # Verifica se o texto é uma das vogais a, e, i, o ou u e, se sim, abre a imagem correspondente
    if 'a' in texto.lower():
        imagem = abrir_imagem('a')
    elif 'e' in texto.lower():
        imagem = abrir_imagem('e')
    elif 'i' in texto.lower():
        imagem = abrir_imagem('i')
    elif 'o' in texto.lower():
        imagem = abrir_imagem('o')
    elif 'u' in texto.lower():
        imagem = abrir_imagem('u')

# Define a posição inicial da imagem
x, y = random.randint(0, WIDTH-100), random.randint(0, HEIGHT-100)

# Loop principal
while True:
    # Processa eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    # Gera um deslocamento aleatório
    dx, dy = random.randint(-5, 5), random.randint(-5, 5)

    # Atualiza a posição da imagem
    x += dx
    y += dy

    # Abre a imagem na posição atual
    screen.fill((255, 255, 255))
    screen.blit(imagem, (x, y))

    # Atualiza a tela
    pygame.display.flip()
