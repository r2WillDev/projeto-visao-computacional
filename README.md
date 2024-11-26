# projeto-visao-computacional

## 1. Importações de Bibliotecas
```python
import cv2
import mediapipe as mp
import webbrowser
import streamlit as st
import json
import os
```
- `cv2`: Biblioteca OpenCV usada para capturar e manipular o vídeo da câmera.
- `mediapipe`: Biblioteca de visão computacional da Google que facilita a detecção de mãos, rostos, etc.
- `webbrowser`: Módulo que permite abrir URLs no navegador da web.
- `streamlit`: Biblioteca usada para criar interfaces web interativas de maneira simples e rápida. Ideal para protótipos de dashboards e visualizações de dados.
- `json`: Módulo da biblioteca padrão do Python para manipulação de dados em formato JSON (JavaScript Object Notation). Permite converter entre strings JSON e objetos Python, como dicionários e listas.
- `os`: Módulo da biblioteca padrão do Python que oferece funcionalidades para interagir com o sistema operacional, como manipulação de arquivos e diretórios, obtenção de variáveis de ambiente e execução de comandos do sistema.

## 2. Inicialização de Detecção de Mãos do MediaPipe
```python
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands = 1)
mp_drawing = mp.solutions.drawing_utils
```
- `mp_hands`: Inicilaiza o módulo de detecção de mãos do MediaPipe
- `hands`: Cria um objeto Hands para detectar até 1 mão (max_num_hands=1)
- `mp_drawing`: Utilitário para desenhar as conexões das mãos na imagem

## 3. Carregar e Salvar Associações de Gestos com URLs
```python
gesture_url_file = "gesture_url_mapping.json"

def save_gesture_url_mapping():
    with open(gesture_url_file, "w") as f:
        json.dump(gesture_url_mapping, f)

def load_gesture_url_mapping():
    if os.path.exists(gesture_url_file):
        with open(gesture_url_file, "r") as f:
            return json.load(f)
    return {}

gesture_url_mapping = load_gesture_url_mapping()

```
- Esta parte do código permite associar gestos com URLs, como desejado no projeto.

## 4.  Funções para Associar Gestos a URLs
```python
def associate_gesture_with_url(gesture_name, url):
    gesture_url_mapping[gesture_name] = url
    save_gesture_url_mapping()  # Salvar as associações atualizadas
    st.write(f"Gesto '{gesture_name}' associado com a URL: {url}")

def remove_gesture_association(gesture_name):
    if gesture_name in gesture_url_mapping:
        del gesture_url_mapping[gesture_name]
        save_gesture_url_mapping()
        st.write(f"Gesto '{gesture_name}' foi removido.")


```
- Essas funções permitem associar ou remover gestos com URLs através da interface do usuário.

## 5. Interface de Usuário (Streamlit)
```python
st.title("Associador de Gestos com URLs")
tab1, tab2 = st.tabs(["Associar Gestos", "Visualizar/Excluir Gestos"])

# Aba 1: Associação de gestos com URLs
with tab1:
    st.header("Associar um Gesto a uma URL")
    gesture_name = st.selectbox("Escolha um gesto para associar", ["Open Hand", "L Gesture", "Three Gesture", "V Gesture", "OK Gesture", "Pinch Gesture"], key="gesture_selectbox")
    url = st.text_input("Digite a URL para o gesto selecionado", key="url_input")

    if st.button("Associar URL ao Gesto", key="associate_button"):
        if url:
            associate_gesture_with_url(gesture_name, url)
        else:
            st.write("Por favor, insira uma URL válida.")
with tab2:
    st.header("Associações Atuais")
    if gesture_url_mapping:
        # Cabeçalho da tabela
        col1, col2, col3 = st.columns([2, 3, 1])
        col1.write("**Gesto**")
        col2.write("**URL Associada**")
        col3.write("**Ações**")

        gestures = list(gesture_url_mapping.keys())
        
        for i, gesture in enumerate(gestures):
            url = gesture_url_mapping[gesture]
            col1, col2, col3 = st.columns([2, 3, 1])
            col1.write(gesture)
            col2.write(url)
            if col3.button("Excluir", key=f"delete_button_{i}"):
                remove_gesture_association(gesture)
                update_needed = True  

        if update_needed:
            if st.button("Atualizar lista de associações"):
                update_needed = False
                st.experimental_rerun()  

    else:
        st.write("Nenhuma associação encontrada.")
```
- Usamos o streamlit para criar a interface gráfica do projeto. O código inclui duas abas: uma para associar gestos a URLs e outra para visualizar/excluir associações existentes.
  
## 6. Detectar Gestos
```python
# Funções para detectar os gestos específicos
def is_hand_open(hand_landmarks):
    # Função para verificar se a mão está aberta
    ...

def is_hand_L_gesture(hand_landmarks):
    # Função para verificar se a mão faz um gesto "L"
    ...

def is_pinch_gesture(hand_landmarks):
    # Função para verificar se a mão faz um gesto de "Pinça"
    ...

def is_ok_gesture(hand_landmarks):
    # Função para verificar se a mão faz um gesto "OK"
    ...

def is_victory_gesture(hand_landmarks):
    # Função para verificar se a mão faz um gesto de "V de Vitória"
    ...

def is_three_gesture(hand_landmarks):
    # Função para verificar se a mão faz um gesto de "Contagem de 3"
    ...

```
- Aqui você implementa a lógica de detecção de gestos com base nos marcos das mãos.
  
## 7. Processamento de Vídeo e Execução de Ações

```python

cap = cv2.VideoCapture(0)

open_hand_frames = 0
L_gesture_frames = 0
pinch_gesture_frames = 0
ok_gesture_frames = 0
victory_gesture_frames = 0
three_gesture_frames = 0
required_gesture_frames = 30


open_hand_detected = False
L_gesture_detected = False
pinch_gesture_detected = False
ok_gesture_detected = False
victory_gesture_detected = False
three_gesture_detected = False

st.write("Abrindo a câmera para detecção de gestos. Aperte 'q' para sair.")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Detecção dos gestos
            if is_hand_open(hand_landmarks):
                open_hand_frames += 1
            else:
                open_hand_frames = 0
                open_hand_detected = False

            if is_hand_L_gesture(hand_landmarks):
                L_gesture_frames += 1
            else:
                L_gesture_frames = 0
                L_gesture_detected = False

            if is_pinch_gesture(hand_landmarks):
                pinch_gesture_frames += 1
            else:
                pinch_gesture_frames = 0
                pinch_gesture_detected = False

            if is_ok_gesture(hand_landmarks):
                ok_gesture_frames += 1
            else:
                ok_gesture_frames = 0
                ok_gesture_detected = False

            if is_victory_gesture(hand_landmarks):
                victory_gesture_frames += 1
            else:
                victory_gesture_frames = 0
                victory_gesture_detected = False

            if is_three_gesture(hand_landmarks):
                three_gesture_frames += 1
            else:
                three_gesture_frames = 0
                three_gesture_detected = False

            # Abrir URLs para gestos detectados
            if open_hand_frames >= required_gesture_frames and not open_hand_detected:
                url = gesture_url_mapping.get("Open Hand")
                if url:
                    webbrowser.open(url)
                    open_hand_detected = True

            if L_gesture_frames >= required_gesture_frames and not L_gesture_detected:
                url = gesture_url_mapping.get("L Gesture")
                if url:
                    webbrowser.open(url)
                    L_gesture_detected = True

            if pinch_gesture_frames >= required_gesture_frames and not pinch_gesture_detected:
                url = gesture_url_mapping.get("Pinch Gesture")
                if url:
                    webbrowser.open(url)
                    pinch_gesture_detected = True

            if ok_gesture_frames >= required_gesture_frames and not ok_gesture_detected:
                url = gesture_url_mapping.get("OK Gesture")
                if url:
                    webbrowser.open(url)
                    ok_gesture_detected = True

            if victory_gesture_frames >= required_gesture_frames and not victory_gesture_detected:
                url = gesture_url_mapping.get("V Gesture")
                if url:
                    webbrowser.open(url)
                    victory_gesture_detected = True

            if three_gesture_frames >= required_gesture_frames and not three_gesture_detected:
                url = gesture_url_mapping.get("Three Gesture")
                if url:
                    webbrowser.open(url)
                    three_gesture_detected = True

    cv2.imshow('Gestos com a Câmera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

```
- Neste trecho, você processa o vídeo da câmera e executa ações (abrir sites) ao reconhecer gestos.


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










