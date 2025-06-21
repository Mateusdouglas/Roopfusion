import os
from PIL import Image
import imagehash
from tqdm import tqdm
from tkinter import Tk, filedialog

def hash_image(image_path):
    """Gera um hash perceptual da imagem para comparar duplicatas."""
    with Image.open(image_path) as img:
        hash = imagehash.phash(img)  # pHash (Perceptual Hashing)
        return hash

def remove_duplicates(folder_path):
    """Remove imagens duplicadas e mantém a sequência ordenada."""
    images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    images.sort(key=lambda x: int(os.path.splitext(x)[0]))  # Ordena pelo nome numérico

    hashes = {}
    duplicates = []

    # Identifica duplicatas
    for image in tqdm(images, desc="Processando imagens"):
        image_path = os.path.join(folder_path, image)
        img_hash = hash_image(image_path)
        
        if img_hash in hashes:
            duplicates.append(image_path)
        else:
            hashes[img_hash] = image_path

    # Remove duplicatas
    for duplicate in tqdm(duplicates, desc="Removendo duplicatas"):
        os.remove(duplicate)

    # Reordena arquivos restantes para manter a sequência
    remaining_images = [f for f in os.listdir(folder_path) if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
    remaining_images.sort(key=lambda x: int(os.path.splitext(x)[0]))

    for index, image in enumerate(remaining_images, start=1):
        old_path = os.path.join(folder_path, image)
        new_name = f"{index}.jpg"  # Ajuste a extensão conforme necessário
        new_path = os.path.join(folder_path, new_name)
        if old_path != new_path:
            os.rename(old_path, new_path)

def select_folder():
    """Abre uma caixa de diálogo para selecionar a pasta."""
    root = Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Selecione a pasta com imagens")
    return folder_path

if __name__ == "__main__":
    folder = select_folder()
    if folder:
        remove_duplicates(folder)
        print("Processo concluído.")
    else:
        print("Nenhuma pasta selecionada.")