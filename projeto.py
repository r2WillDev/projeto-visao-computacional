import cv2
import mediapipe as mp
import webbrowser

# Inicializar mediapipe para detecção de mãos
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(max_num_hands=1)
mp_drawing = mp.solutions.drawing_utils

# Função para verificar se a mão está aberta
def is_hand_open(hand_landmarks):
    finger_tips = [4, 8, 12, 16, 20]  # IDs das pontas dos dedos (polegar, indicador, médio, anelar, mindinho)
    finger_joints = [3, 6, 10, 14, 18]  # IDs das articulações médias dos dedos

    open_fingers = 0
    for tip, joint in zip(finger_tips[1:], finger_joints[1:]):  # Verificando do indicador ao mindinho
        if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[joint].y:
            open_fingers += 1

    return open_fingers == 4  # Considera a mão aberta se todos os quatro dedos, exceto o polegar, estiverem estendidos

# Função para verificar se a mão faz um gesto de "L"
def is_hand_L_gesture(hand_landmarks):
    # Verifica se o polegar (landmark 4) e o indicador (landmark 8) estão estendidos,
    # enquanto os outros dedos estão dobrados
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

    # O polegar e o indicador devem estar estendidos (acima das articulações)
    thumb_extended = thumb_tip.x < thumb_joint.x  # Para o polegar, verificamos a coordenada x (mão direita)
    index_extended = index_tip.y < index_joint.y  # Para o indicador, verificamos a coordenada y (mão na vertical)

    # Os outros dedos devem estar dobrados (ponta abaixo da articulação)
    middle_bent = middle_tip.y > middle_joint.y
    ring_bent = ring_tip.y > ring_joint.y
    pinky_bent = pinky_tip.y > pinky_joint.y

    return thumb_extended and index_extended and middle_bent and ring_bent and pinky_bent

# Capturar vídeo da câmera
cap = cv2.VideoCapture(0)

# Variáveis para contar o número de frames consecutivos com os gestos
open_hand_frames = 0
L_gesture_frames = 0
required_gesture_frames = 30  # Número de frames necessários para confirmar o gesto

# Variáveis para garantir que os gestos não sejam processados repetidamente
open_hand_detected = False
L_gesture_detected = False

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Converter a imagem para RGB
    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(frame_rgb)

    # Desenhar as mãos detectadas
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

            # Verificar se a mão está aberta
            if is_hand_open(hand_landmarks):
                open_hand_frames += 1
                L_gesture_frames = 0  # Reseta o contador do gesto de "L"
            else:
                open_hand_frames = 0
                open_hand_detected = False  # Permite nova detecção após o gesto ser interrompido

            # Verificar se o gesto de "L" está presente
            if is_hand_L_gesture(hand_landmarks):
                L_gesture_frames += 1
                open_hand_frames = 0  # Reseta o contador do gesto de mão aberta
            else:
                L_gesture_frames = 0
                L_gesture_detected = False  # Permite nova detecção após o gesto ser interrompido

            # Verifica se o gesto de mão aberta foi mantido por frames suficientes
            if open_hand_frames >= required_gesture_frames and not open_hand_detected:
                webbrowser.open('https://www.google.com')
                open_hand_detected = True  # Impede a abertura contínua sem interrupção

            # Verifica se o gesto de "L" foi mantido por frames suficientes
            if L_gesture_frames >= required_gesture_frames and not L_gesture_detected:
                webbrowser.open('https://www.linkedin.com/feed/')
                L_gesture_detected = True  # Impede a abertura contínua sem interrupção

    # Mostrar a imagem
    cv2.imshow('Gestos com a Câmera', frame)

    # Sair com a tecla 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Liberar recursos
cap.release()
cv2.destroyAllWindows()
