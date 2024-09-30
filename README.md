# projeto-visao-computacional

## 1. Importações de Bibliotecas
```python
import cv2
import mediapipe as mp
import webbrowser
```
- `cv2`: Biblioteca OpenCV usada para capturar e manipular o vídeo da câmera.
- `mediapipe`: Biblioteca de visão computacional da Google que facilita a detecção de mãos, rostos, etc.
- `webbrowser`: Módulo que permite abrir URLs no navegador da web.

## 2. Inicialização de Detecção de Mãos do MediaPipe
```python
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands = 1)
mp_drawing = mp.solutions.drawing_utils
```
- `mp_hands`: Inicilaiza o módulo de detecção de mãos do MediaPipe
- `hands`: Cria um objeto Hands para detectar até 1 mão (max_num_hands=1)
- `mp_drawing`: Utilitário para desenhar as conexões das mãos na imagem

## 3. Função para Verificar se a Mão está aberta
```python
def is_hand_open(hand_landmarks):
    finger_tips = [4, 8, 12, 16, 20]  
    finger_joints = [3, 6, 10, 14, 18]

    open_fingers = 0
    for tip, joint in zip(finger_tips[1:], finger_joints[1:]): 
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y:
            open_fingers += 1

    return open_fingers == 4  
```
- Esta função verifica se os dedos, do indicador ao mindinho, estão estendidos.
- Para cada dedo, verifica se a ponta (tip) está acima da articulação média (joint), usando as coordenadas `y` (posição vertical).
- Se os quatro dedos (exceto o polegar) estiverem estendidos, considera que a mão está aberta.

## 4. Função para Verificar se a Mão Está Fazendo o Gesto de "L"
```python
def is_hand_L_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    ring_tip = hand_landmarks.landmark[16]
    pinky_tip = hand_landmarks.landmark[20]

    thumb_joint = hand_landmarks.landmark[3]
    index_joint = hand_landmarks.landmark[6]
    middle_joint = hand_landmarks.landmark[10]
    ring_joint = hand_landmarks.landmark[14]
    pinky_joint = hand_landmarks.landmark[18]

    thumb_extended = thumb_tip.x < thumb_joint.x
    index_extended = index_tip.y < index_joint.y

    middle_bent = middle_tip.y > middle_joint.y
    ring_bent = ring_tip.y > ring_joint.y
    pinky_bent = pinky_tip.y > pinky_joint.y

    return thumb_extended and index_extended and middle_bent and ring_bent and pinky_bent

```
- Esta função detecta o gesto de "L".
  - Verifica se o **polegar** está estendido para fora (baseado na coordenada `x`).
  - Verifica se o **indicador** está estendido (baseado na coordenada `y`).
  - Verifica se os outros três dedos (**médio, anelar e mindinho**) estão dobrados (com as pontas abaixo das articulações).



## 5. Configuração da Captura de Vídeo
```python
cap = cv2.VideoCapture(0)
```
- Inicia a captura de vídeo da câmera. O índice `0` geralmente representa a câmera padrão do sistema.
  
## 6. Variáveis para Contagem e Controle de Gestos
```python
open_hand_frames = 0
L_gesture_frames = 0
required_gesture_frames = 30

open_hand_detected = False
L_gesture_detected = False
```
- `open_hand_frames` e `L_gesture_frames`: Contadores de quantos frames consecutivos cada gesto foi detectado.
- `required_gesture_frames`: Quantos frames consecutivos o gesto precisa durar para ser reconhecido (neste caso, 30).
- `open_hand_detected` e `L_gesture_detected`: Variáveis booleanas para garantir que o gesto não seja processado repetidamente.
  
## 7. Laço Principal para Processamento de Vídeo

```python
while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)
```
- Dentro do laço, captura o vídeo quadro a quadro.
- Converte o quadro para o formato RGB, necessário para o MediaPipe.
- Usa o `hands.process(frame_rgb)` para processar o quadro e identificar mãos na imagem.


## 8. Desenho das Mãos Detectadas e Detecção de Gestos
```python
if results.multi_hand_landmarks:
    for hand_landmarks in results.multi_hand_landmarks:
        mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
```
- Se o MediaPipe detectar mãos, desenha os pontos e conexões das mãos no quadro usando `mp_drawing.draw_landmarks`.
```python
if is_hand_open(hand_landmarks):
    open_hand_frames += 1
    L_gesture_frames = 0
else:
    open_hand_frames = 0
    open_hand_detected = False
```
- Se a mão estiver aberta, aumenta o contador de frames consecutivos para o gesto de mão aberta e reseta o contador do gesto de "L". Caso contrário, reseta o contador de mão aberta.

```python
if is_hand_L_gesture(hand_landmarks):
    L_gesture_frames += 1
    open_hand_frames = 0
else:
    L_gesture_frames = 0
    L_gesture_detected = False
```
- Se o gesto de "L" for detectado, aumenta o contador de frames consecutivos e reseta o contador de mão aberta. Caso contrário, reseta o contador de "L".
## 9. Ação com Base nos Gestos Detectados
```python
if open_hand_frames >= required_gesture_frames and not open_hand_detected:
    webbrowser.open('https://www.google.com')
    open_hand_detected = True
```
- Se o gesto de mão aberta for detectado por 30 frames consecutivos e ainda não foi processado, abre o navegador na página do Google e marca que o gesto foi detectado.
```python
if L_gesture_frames >= required_gesture_frames and not L_gesture_detected:
    webbrowser.open('https://www.linkedin.com/feed/')
    L_gesture_detected = True
```
- Se o gesto de "L" for detectado por 30 frames consecutivos e ainda não foi processado, abre o navegador na página do LinkedIn.

## 10. Mostrar a Imagem na Tela
```python
cv2.imshow('Gestos com a Câmera', frame)

if cv2.waitKey(1) & 0xFF == ord('q'):
    break
```
- Exibe a imagem com as mãos detectadas em uma janela.
- A execução do laço continua até que a tecla 'q' seja pressionada.

## 11. Liberação de Recursos

```python
cap.release()
cv2.destroyAllWindows()
```
- Libera a câmera e fecha todas as janelas quando o laço principal termina.

# CASO DE USO

## Sistema de Detecção de Gestos para Navegação em Sites
**Ator Principal:**
- **Usuário**
**Descrição Geral:**
  
O sistema permite que o usuário navegue para sites específicos utilizando gestos manuais pré-definidos. Por exemplo, ao fazer um "L" com a mão, o sistema reconhece o gesto e abre o site do LinkedIn.

## Casos de Uso Principais
### 1. Realizar Gesto para Navegação
- **Ator**: Usuário

- **Pré-condições**:

  - O sistema está em operação e a câmera está funcionando corretamente.
  - Os gestos e seus sites associados estão previamente configurados.
- **Fluxo Principal**:

  1. O usuário posiciona a mão em frente à câmera e realiza um gesto pré-definido.
  2. O sistema captura a imagem do gesto.
  3. O sistema processa a imagem e reconhece o gesto realizado.
  4. O sistema verifica o site associado ao gesto reconhecido.
  5. O sistema abre o site correspondente no navegador padrão.

- **Pós-condições**:

  - O site associado ao gesto é aberto e exibido ao usuário.
- **Fluxos Alternativos**:

- **A1**: Se o gesto não for reconhecido:
  - O sistema informa ao usuário que o gesto não foi identificado e solicita que tente novamente.
- **A2**: Se o site associado não estiver disponível:
  - O sistema exibe uma mensagem de erro informando que não foi possível acessar o site.
## 2. Configurar Gestos e Sites Associados
- **Ator**: Usuário/Administrador

- **Pré-condições**:

- O usuário possui permissões para configurar o sistema.
- O sistema está em operação.
- **Fluxo Principal**:

  1. O usuário acessa a interface de configuração de gestos.
  2. O usuário seleciona um gesto existente ou cria um novo gesto.
  3. O usuário associa o gesto a um site específico.
  4. O sistema salva as configurações atualizadas.
- **Pós-condições:**

  - O novo gesto e sua associação ao site são armazenados no sistema.
- **Fluxos Alternativos:**
  - **B1:** Se o gesto já estiver associado a um site:
    -  O sistema pergunta se o usuário deseja sobrescrever a configuração existente.

## Requisitos Não Funcionais
- **Usabilidade:** O sistema deve ser intuitivo e fácil de usar, com reconhecimento preciso dos gestos.
- **Performance:** O tempo entre o reconhecimento do gesto e a abertura do site não deve exceder 2 segundos.
- **Confiabilidade:** O sistema deve ter alta taxa de acerto no reconhecimento de gestos para evitar ações incorretas.
## Exceções
- **E1:** Câmera não detectada ou com mau funcionamento.
  - O sistema notifica o usuário sobre o problema com a câmera.
- **E2:** Conexão à internet indisponível.
  - O sistema informa ao usuário que não é possível acessar o site devido à falta de conexão.










