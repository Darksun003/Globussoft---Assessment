# test_predict.py
"""
Load gallery embeddings and provide verification functions.
Example usage:
    from test_predict import verify_pair, verify_against_gallery
    result = verify_pair("a.jpg", "b.jpg")
    top_match = verify_against_gallery("unknown.jpg", "gallery_embeddings.npz")
"""

import numpy as np
from PIL import Image
from facenet_pytorch import MTCNN, InceptionResnetV1
import torch
import os

# create model instances (keep them global to avoid reloading)
DEVICE = "cpu"  # change to 'cuda' if available
_mtcnn = MTCNN(keep_all=False, device=DEVICE)
_resnet = InceptionResnetV1(pretrained='vggface2').eval().to(DEVICE)

def _get_embedding(image_path):
    img = Image.open(image_path).convert('RGB')
    face = _mtcnn(img)
    if face is None:
        return None
    face = face.unsqueeze(0).to(DEVICE)
    with torch.no_grad():
        emb = _resnet(face)
    emb = emb.cpu().numpy().flatten()
    emb = emb / np.linalg.norm(emb)
    return emb

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

def verify_pair(img1_path, img2_path, threshold=0.6):
    """
    Compute cosine similarity between two images.
    Returns dict with success flag, similarity score, and message.
    threshold ~ 0.5-0.7 typical; tune as needed.
    """
    emb1 = _get_embedding(img1_path)
    emb2 = _get_embedding(img2_path)
    if emb1 is None or emb2 is None:
        return {"ok": False, "reason": "Face not detected in one or both images."}
    score = cosine_similarity(emb1, emb2)
    same = score >= threshold
    return {"ok": True, "score": score, "same": same}

def verify_against_gallery(img_path, gallery_path="gallery_embeddings.npz", top_k=1):
    """
    Compare single image embedding against saved gallery.
    Returns best match label and score.
    """
    if not os.path.exists(gallery_path):
        return {"ok": False, "reason": "Gallery not found."}

    data = np.load(gallery_path, allow_pickle=True)
    labels = list(data["labels"])
    vectors = data["vectors"]  # shape (N,512)

    emb = _get_embedding(img_path)
    if emb is None:
        return {"ok": False, "reason": "Face not detected."}

    # compute cosine similarity with each vector
    sims = (vectors @ emb) / (np.linalg.norm(vectors, axis=1) * np.linalg.norm(emb) + 1e-10)
    idx_sorted = np.argsort(-sims)  # descending
    best_idx = idx_sorted[0]
    best_label = labels[best_idx]
    best_score = float(sims[best_idx])
    topk = [{"label": labels[i], "score": float(sims[i])} for i in idx_sorted[:top_k]]
    return {"ok": True, "best_label": best_label, "best_score": best_score, "topk": topk}
