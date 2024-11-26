import cv2
import mediapipe as mp
import webbrowser
import streamlit as st
import json
import os

# Inicializar Mediapipe para detecção de mãos
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# Caminho do arquivo JSON onde as associações serão salvas
gesture_url_file = "gesture_url_mapping.json"

# Função para salvar as associações em um arquivo JSON
def save_gesture_url_mapping():
    with open(gesture_url_file, "w") as f:
        json.dump(gesture_url_mapping, f)

# Função para carregar as associações de um arquivo JSON
def load_gesture_url_mapping():
    if os.path.exists(gesture_url_file):
        with open(gesture_url_file, "r") as f:
            return json.load(f)
    return {}

# Dicionário para armazenar associações de gestos com URLs
gesture_url_mapping = load_gesture_url_mapping()

# Função para associar um gesto com uma URL e salvar a associação
def associate_gesture_with_url(gesture_name, url):
    gesture_url_mapping[gesture_name] = url
    save_gesture_url_mapping()  # Salvar as associações atualizadas
    st.write(f"Gesto '{gesture_name}' associado com a URL: {url}")

# Função para remover uma associação de gesto com URL e salvar a alteração
def remove_gesture_association(gesture_name):
    if gesture_name in gesture_url_mapping:
        del gesture_url_mapping[gesture_name]
        save_gesture_url_mapping()
        st.write(f"Gesto '{gesture_name}' foi removido.")

# Configuração da interface Streamlit com duas abas
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

# Variável para controlar a atualização manual
update_needed = False

# Aba 2: Visualização e exclusão de associações com tabela
with tab2:
    st.header("Associações Atuais")
    if gesture_url_mapping:
        # Cabeçalho da tabela
        col1, col2, col3 = st.columns([2, 3, 1])
        col1.write("**Gesto**")
        col2.write("**URL Associada**")
        col3.write("**Ações**")

        # Copiar as chaves do dicionário para evitar erro durante a exclusão
        gestures = list(gesture_url_mapping.keys())
        
        # Linhas da tabela com gestos e URLs
        for i, gesture in enumerate(gestures):
            url = gesture_url_mapping[gesture]
            col1, col2, col3 = st.columns([2, 3, 1])
            col1.write(gesture)
            col2.write(url)
            if col3.button("Excluir", key=f"delete_button_{i}"):
                remove_gesture_association(gesture)
                update_needed = True  # Sinaliza que uma atualização é necessária

        # Exibir o botão de atualização se uma exclusão ocorreu
        if update_needed:
            if st.button("Atualizar lista de associações"):
                update_needed = False
                st.experimental_rerun()  # Redesenha a interface com a lista atualizada

    else:
        st.write("Nenhuma associação encontrada.")

# Função para verificar se a mão está aberta
def is_hand_open(hand_landmarks):
    finger_tips = [4, 8, 12, 16, 20]  # IDs das pontas dos dedos
    finger_joints = [3, 6, 10, 14, 18]  # IDs das articulações médias

    open_fingers = 0
    for tip, joint in zip(finger_tips[1:], finger_joints[1:]):  # Verificando do indicador ao mindinho
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y:
            open_fingers += 1

    return open_fingers == 4  # Mão aberta se todos os quatro dedos (exceto o polegar) estão estendidos

# Função para verificar se a mão faz um gesto de "L"
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

# Gestura Pinça - "Pinch Gesture"
def is_pinch_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    ring_tip = hand_landmarks.landmark[16]
    pinky_tip = hand_landmarks.landmark[20]

    middle_joint = hand_landmarks.landmark[10]
    ring_joint = hand_landmarks.landmark[14]
    pinky_joint = hand_landmarks.landmark[18]

    thumb_index_touch = abs(thumb_tip.x - index_tip.x) < 0.02 and abs(thumb_tip.y - index_tip.y) < 0.02
    middle_bent = middle_tip.y > middle_joint.y
    ring_bent = ring_tip.y > ring_joint.y
    pinky_bent = pinky_tip.y > pinky_joint.y

    return thumb_index_touch and middle_bent and ring_bent and pinky_bent

# Gestura OK - "OK Gesture"
def is_ok_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    ring_tip = hand_landmarks.landmark[16]
    pinky_tip = hand_landmarks.landmark[20]

    middle_joint = hand_landmarks.landmark[10]
    ring_joint = hand_landmarks.landmark[14]
    pinky_joint = hand_landmarks.landmark[18]

    thumb_index_circle = abs(thumb_tip.x - index_tip.x) < 0.02 and abs(thumb_tip.y - index_tip.y) < 0.02
    middle_extended = middle_tip.y < middle_joint.y
    ring_extended = ring_tip.y < ring_joint.y
    pinky_extended = pinky_tip.y < pinky_joint.y

    return thumb_index_circle and middle_extended and ring_extended and pinky_extended

# Gestura V de Vitória - "V Gesture"
def is_victory_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    ring_tip = hand_landmarks.landmark[16]
    pinky_tip = hand_landmarks.landmark[20]

    index_joint = hand_landmarks.landmark[6]
    middle_joint = hand_landmarks.landmark[10]
    ring_joint = hand_landmarks.landmark[14]
    pinky_joint = hand_landmarks.landmark[18]

    index_extended = index_tip.y < index_joint.y
    middle_extended = middle_tip.y < middle_joint.y
    ring_bent = ring_tip.y > ring_joint.y
    pinky_bent = pinky_tip.y > pinky_joint.y

    return index_extended and middle_extended and ring_bent and pinky_bent

# Gestura Contagem de 3 - "Three Gesture"
def is_three_gesture(hand_landmarks):
    thumb_tip = hand_landmarks.landmark[4]
    index_tip = hand_landmarks.landmark[8]
    middle_tip = hand_landmarks.landmark[12]
    ring_tip = hand_landmarks.landmark[16]
    pinky_tip = hand_landmarks.landmark[20]

    ring_joint = hand_landmarks.landmark[14]
    pinky_joint = hand_landmarks.landmark[18]

    thumb_extended = thumb_tip.x < hand_landmarks.landmark[3].x
    index_extended = index_tip.y < hand_landmarks.landmark[6].y
    middle_extended = middle_tip.y < hand_landmarks.landmark[10].y
    ring_bent = ring_tip.y > ring_joint.y
    pinky_bent = pinky_tip.y > pinky_joint.y

    return thumb_extended and index_extended and middle_extended and ring_bent and pinky_bent


# Capturar vídeo da câmera
cap = cv2.VideoCapture(0)

# Variáveis para contar o número de frames consecutivos com os gestos
open_hand_frames = 0
L_gesture_frames = 0
pinch_gesture_frames = 0
ok_gesture_frames = 0
victory_gesture_frames = 0
three_gesture_frames = 0
required_gesture_frames = 30

# Variáveis para garantir que os gestos não sejam processados repetidamente
open_hand_detected = False
L_gesture_detected = False
pinch_gesture_detected = False
ok_gesture_detected = False
victory_gesture_detected = False
three_gesture_detected = False

# Executar o loop de detecção de gestos
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

    # Mostrar a imagem
    cv2.imshow('Gestos com a Câmera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
