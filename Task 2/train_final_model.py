# train_final_model.py
"""
Train step for Face Verification (Task 2).
Builds a gallery by computing the mean embedding for each person folder under `data/`.
Saves embeddings and labels to gallery_embeddings.npz
Usage:
    python train_final_model.py --data_dir data --out gallery_embeddings.npz
"""

import os
import numpy as np
from PIL import Image
import argparse
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
from tqdm import tqdm

def get_image_paths(data_dir):
    people = [d for d in os.listdir(data_dir) if os.path.isdir(os.path.join(data_dir, d))]
    paths = {}
    for person in people:
        folder = os.path.join(data_dir, person)
        imgs = [os.path.join(folder, f) for f in os.listdir(folder)
                if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if imgs:
            paths[person] = imgs
    return paths

def compute_mean_embeddings(data_dir, device='cpu'):
    mtcnn = MTCNN(keep_all=False, device=device)
    resnet = InceptionResnetV1(pretrained='vggface2').eval().to(device)

    person_embeddings = {}
    paths = get_image_paths(data_dir)
    for person, imgs in paths.items():
        embs = []
        for img_path in tqdm(imgs, desc=f"Processing {person}", unit="img"):
            try:
                img = Image.open(img_path).convert('RGB')
            except Exception as e:
                print("  Cannot open:", img_path, e)
                continue
            # detect and crop face
            face = mtcnn(img)
            if face is None:
                # no face detected
                continue
            # face is a tensor (3,160,160)
            face = face.unsqueeze(0).to(device)  # add batch dim
            with torch.no_grad():
                emb = resnet(face)  # (1,512)
            emb = emb.cpu().numpy().flatten()
            embs.append(emb)
        if embs:
            mean_emb = np.mean(np.stack(embs), axis=0)
            # normalize
            mean_emb = mean_emb / np.linalg.norm(mean_emb)
            person_embeddings[person] = mean_emb
            print(f"Saved embedding for {person} ({len(embs)} images)")
        else:
            print(f"No valid faces found for {person}; skipping.")

    return person_embeddings

def save_gallery(gallery, out_path):
    labels = list(gallery.keys())
    vectors = np.stack([gallery[l] for l in labels], axis=0)
    np.savez(out_path, labels=labels, vectors=vectors)
    print(f"Gallery saved to {out_path}. {len(labels)} identities.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--data_dir", type=str, default="data", help="data/<person_name>/*.jpg")
    parser.add_argument("--out", type=str, default="gallery_embeddings.npz")
    parser.add_argument("--device", type=str, default="cpu", help="cpu or cuda")
    args = parser.parse_args()

    gallery = compute_mean_embeddings(args.data_dir, device=args.device)
    if gallery:
        save_gallery(gallery, args.out)
    else:
        print("No embeddings computed; check dataset.")
