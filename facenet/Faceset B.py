import cv2
import os
import numpy as np
from tkinter import Tk
from tkinter.filedialog import askopenfilename
from tqdm import tqdm

# Função para criar as pastas se elas não existirem
def create_faceset_folders(root_folder):
    if not os.path.exists(root_folder):
        os.makedirs(root_folder)
    aligned_folder = os.path.join(root_folder, 'Aligned')
    if not os.path.exists(aligned_folder):
        os.makedirs(aligned_folder)
    return aligned_folder

# Função para redimensionar e salvar a imagem do rosto
def save_face_image(face_image, output_path):
    resized_face = cv2.resize(face_image, (512, 512))
    cv2.imwrite(output_path, resized_face)

# Função para verificar se a GPU está disponível e configurar a rede
def configure_network(prototxt_path, model_path):
    # Carregar a rede com OpenCV
    net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

    # Verificar se há suporte a CUDA
    if cv2.cuda.getCudaEnabledDeviceCount() > 0:
        print("CUDA disponível. Usando GPU.")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
    else:
        print("CUDA não disponível. Usando CPU.")
        net.setPreferableBackend(cv2.dnn.DNN_BACKEND_DEFAULT)
        net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
    
    return net

# Função para encontrar o próximo índice disponível
def find_next_index(aligned_folder):
    existing_files = [f for f in os.listdir(aligned_folder) if os.path.isfile(os.path.join(aligned_folder, f))]
    if not existing_files:
        return 1
    existing_indices = [int(os.path.splitext(f)[0]) for f in existing_files if f.split('.')[0].isdigit()]
    return max(existing_indices) + 1 if existing_indices else 1

# Função principal para extrair rostos e salvar as imagens
def extract_faces_from_video(video_path, output_folder):
    # Caminhos absolutos para os arquivos do modelo
    base_dir = os.path.dirname(os.path.abspath(__file__))
    prototxt_path = os.path.join(base_dir, 'configs', 'deploy.prototxt')
    model_path = os.path.join(base_dir, 'configs', 'res10_300x300_ssd_iter_140000.caffemodel')
    
    # Verificar se os arquivos existem
    if not os.path.isfile(prototxt_path):
        print(f"Arquivo de configuração não encontrado: {prototxt_path}")
        return
    if not os.path.isfile(model_path):
        print(f"Arquivo do modelo não encontrado: {model_path}")
        return
    
    # Configurar a rede
    net = configure_network(prototxt_path, model_path)

    # Abrir o vídeo
    cap = cv2.VideoCapture(video_path)

    # Verificar se o vídeo foi carregado corretamente
    if not cap.isOpened():
        print("Erro ao abrir o vídeo.")
        return

    # Criar pasta para salvar os frames e a subpasta para rostos alinhados
    aligned_folder = create_faceset_folders(output_folder)

    # Encontrar o próximo índice disponível para salvar as imagens dos rostos
    index = find_next_index(aligned_folder)

    # Contar o número total de frames
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    # Inicializar a barra de progresso
    with tqdm(total=total_frames, desc="Processando iterações", unit="it", unit_scale=True) as pbar:
        while True:
            # Ler frame por frame do vídeo
            ret, frame = cap.read()
            if not ret:
                break

            # Salvar o frame
            frame_path = os.path.join(output_folder, f"{index}.jpg")
            cv2.imwrite(frame_path, frame)

            # Obter as dimensões do frame
            (h, w) = frame.shape[:2]

            # Preparar o frame para a rede
            blob = cv2.dnn.blobFromImage(cv2.resize(frame, (300, 300)), 1.0, (300, 300), (104.0, 177.0, 123.0))
            net.setInput(blob)
            detections = net.forward()

            # Iterar sobre as deteções
            for i in range(0, detections.shape[2]):
                confidence = detections[0, 0, i, 2]
                if confidence > 0.5:
                    box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                    (startX, startY, endX, endY) = box.astype("int")

                    # Adicionar uma margem ao redor do rosto
                    margin = int(0.2 * (endX - startX))
                    startX = max(startX - margin, 0)
                    startY = max(startY - margin, 0)
                    endX = min(endX + margin, w)
                    endY = min(endY + margin, h)

                    face_image = frame[startY:endY, startX:endX]

                    # Criar o caminho de saída e salvar a imagem do rosto
                    face_path = os.path.join(aligned_folder, f"{index}.jpg")
                    save_face_image(face_image, face_path)

            index += 1
            # Atualizar a barra de progresso
            pbar.update(1)

    # Liberar recursos
    cap.release()
    print("Processamento concluído.")

# Função para selecionar o vídeo usando uma caixa de diálogo
def select_video_file():
    Tk().withdraw()  # Não mostrar a janela principal
    video_file_path = askopenfilename(filetypes=[("Vídeos", "*.mp4;*.avi;*.mov")])
    return video_file_path

if __name__ == "__main__":
    video_path = select_video_file()
    if video_path:
        output_folder = "Faceset B"
        extract_faces_from_video(video_path, output_folder)
    else:
        print("Nenhum vídeo selecionado.")