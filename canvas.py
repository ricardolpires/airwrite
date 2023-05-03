import cv2
import mediapipe as mp
import os
import numpy as np
import pygame
#from time import sleep

# Definindo algumas constantes para cores
BRANCO = (255, 255, 255)
PRETO = (0, 0, 0)
AZUL = (255, 0, 0)
VERDE = (0, 255, 0)
VERMELHO = (0, 0, 255)
AZUL_CLARO = (255, 255, 0)

# Configurando o uso da biblioteca MediaPipe para detecção de mãos
mp_maos = mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils
maos = mp_maos.Hands()

# Definindo a resolução da câmera e capturando o vídeo
resolucao_x = 800
resolucao_y = 600
camera = cv2.VideoCapture(1)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolucao_x)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolucao_y)

# Criando uma imagem em branco para o quadro e definindo as propriedades do pincel
img_quadro = np.ones((resolucao_y, resolucao_x, 3), np.uint8) * 255
cor_pincel = (255, 0, 0)
espessura_pincel = 5

# Definindo as coordenadas do canto superior esquerdo do quadro (V)
x_quadro, y_quadro = 0, 0

def encontra_coordenadas_maos(img, lado_invertido=False):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB) # converte a imagem BGR para RGB
    resultado = maos.process(img_rgb) # processa a imagem para detectar as mãos
    todas_maos = []
    if resultado.multi_hand_landmarks: # verifica se há mãos detectadas na imagem
        for lado_mao, marcacoes_maos in zip(resultado.multi_handedness, resultado.multi_hand_landmarks):
            #frames na tela
            print(marcacoes_maos)
            # percorre cada uma das mãos detectadas e suas marcações
            info_mao = {}
            coordenadas = []
            for marcacao in marcacoes_maos.landmark:
                # obtém as coordenadas (x,y,z) de cada marcação e as armazena na lista coordenadas
                coord_x, coord_y, coord_z = int(marcacao.x * resolucao_x), int(marcacao.y * resolucao_y), int(
                    marcacao.z * resolucao_x)
                coordenadas.append((coord_x, coord_y, coord_z))

            info_mao['coordenadas'] = coordenadas # armazena as coordenadas da mão em info_mao
            if lado_invertido:
                if lado_mao.classification[0].label == 'Left':
                    info_mao['lado'] = 'Right' # inverte o lado da mão caso lado_invertido seja True
                else:
                    info_mao['lado'] = 'Left'
            else:
                info_mao['lado'] = lado_mao.classification[0].label

            todas_maos.append(info_mao) # adiciona as informações da mão na lista todas_maos
            mp_desenho.draw_landmarks(img,
                                      marcacoes_maos,
                                      mp_maos.HAND_CONNECTIONS) # desenha as marcações da mão na imagem

    return img, todas_maos # retorna a imagem com as marcações das mãos e as informações das mãos detectadas

def dedos_levantados(mao):
    dedos = []
    for ponta_dedo in [8, 12, 16, 20]:
        if mao['coordenadas'][ponta_dedo][1] < mao['coordenadas'][ponta_dedo - 2][1]:
            dedos.append(True)
        else:
            dedos.append(False)
    return dedos

while True:
    # Lê o frame da câmera
    sucesso, img = camera.read()
    # Inverte a imagem horizontalmente
    img = cv2.flip(img, 1)

    # Detecta as coordenadas das mãos na imagem
    img, todas_maos = encontra_coordenadas_maos(img)

    # Se houver apenas uma mão detectada
    if len(todas_maos) == 1:
        # Calcula quais dedos estão levantados na mão detectada
        info_dedos_mao1 = dedos_levantados(todas_maos[0])
        #print(info_dedos_mao1)
    # Se houverem duas mãos detectadas
    if len(todas_maos) == 2:
        # Calcula quais dedos estão levantados em cada mão
        info_dedos_mao1 = dedos_levantados(todas_maos[0])

        info_dedos_mao2 = dedos_levantados(todas_maos[1])
        # Obtém as coordenadas do dedo indicador da primeira mão
        indicador_x, indicador_y, indicador_z = todas_maos[0]['coordenadas'][8]

        # Define a cor do pincel com base na quantidade de dedos levantados na segunda mão
        if sum(info_dedos_mao2) == 1:
            cor_pincel = AZUL
        elif sum(info_dedos_mao2) == 2:
            cor_pincel = VERDE
        elif sum(info_dedos_mao2) == 3:
            cor_pincel = VERMELHO
        elif sum(info_dedos_mao2) == 4:
            cor_pincel = BRANCO
        else:
            # Cria um quadro em branco
            img_quadro = np.ones((resolucao_y, resolucao_x, 3), np.uint8) * 255

        # Calcula a espessura do pincel com base na profundidade do dedo indicador da primeira mão
        espessura_pincel = int(abs(indicador_z)) // 3 + 5
        cv2.circle(img, (indicador_x, indicador_y), espessura_pincel, cor_pincel, cv2.FILLED)

        # Se o polegar da primeira mão estiver levantado
        if info_dedos_mao1 == [True, False, False, False]:
            # Se a posição anterior do dedo indicador não for definida, define como a posição atual
            if x_quadro == 0 and y_quadro == 0:
                # Se a posição anterior do dedo indicador não for definida, define como a posição atual
                x_quadro, y_quadro = indicador_x, indicador_y

            # Desenha uma linha do dedo indicador até a posição anterior do dedo indicador
            cv2.line(img_quadro, (x_quadro, y_quadro), (indicador_x, indicador_y), cor_pincel, espessura_pincel)

            # Atualiza a posição
            x_quadro, y_quadro = indicador_x, indicador_y  # Define a posição do quadrado na imagem
        else:
            x_quadro, y_quadro = 0, 0  # Define a posição do quadrado como (0, 0) se não houver uma detecção válida

        img = cv2.addWeighted(img, 1, img_quadro, 0.2, 0)  # Adiciona o quadrado à imagem original com uma opacidade de 0,2

    cv2.imshow("Imagem", img)  # Mostra a imagem original com o quadrado
    cv2.imshow('Quadro', img_quadro)  # Mostra o quadrado isolado em uma janela separada
    tecla = cv2.waitKey(1)  # Aguarda por uma tecla ser pressionada por 1 milissegundo
    if tecla == 27:  # Se a tecla ESC for pressionada, sai do loop
        break

#with open('texto.txt', 'w') as arquivo:
#    arquivo.write(texto)

cv2.imwrite('quadro.png', img_quadro)  # Salva o quadrado em um arquivo de imagem
#cv2.destroyAllWindows()  # Fecha todas as janelas abertas
#camera.release()  # Libera o acesso à câmera.


