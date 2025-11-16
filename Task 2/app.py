# app.py
"""
FastAPI face verification service.
POST /verify - multipart form upload with two image files (file1, file2)
Response JSON includes similarity and bounding boxes.
Run:
    uvicorn app:app --host 0.0.0.0 --port 8000
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
import numpy as np
import torch
from facenet_pytorch import MTCNN, InceptionResnetV1

app = FastAPI(title="Face Verification API")

DEVICE = "cpu"  # switch to 'cuda' if available
mtcnn = MTCNN(keep_all=False, device=DEVICE)
resnet = InceptionResnetV1(pretrained='vggface2').eval().to(DEVICE)

def read_imagefile(file) -> Image.Image:
    contents = file.file.read()
    return Image.open(BytesIO(contents)).convert("RGB")

def get_face_and_box(img: Image.Image):
    # Returns cropped face tensor and bounding box
    boxes, probs = mtcnn.detect(img)
    if boxes is None:
        return None, None
    # since keep_all=False we expect a single box (choose the largest if multiple)
    if isinstance(boxes, np.ndarray) and boxes.shape[0] > 1:
        # choose box with largest area
        areas = [(b[2]-b[0])*(b[3]-b[1]) for b in boxes]
        idx = int(np.argmax(areas))
        box = boxes[idx]
    else:
        box = boxes[0]
    # crop and align face using mtcnn.forward? simpler: use mtcnn to get the tensor directly
    face_tensor = mtcnn(img)  # returns 3x160x160 tensor or batch
    if face_tensor is None:
        return None, box.tolist()
    return face_tensor, box.tolist()

def tensor_to_embedding(tensor):
    if tensor.ndim == 3:
        tensor = tensor.unsqueeze(0)
    tensor = tensor.to(DEVICE)
    with torch.no_grad():
        emb = resnet(tensor).cpu().numpy().flatten()
    emb = emb / np.linalg.norm(emb)
    return emb

def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

@app.post("/verify")
async def verify(file1: UploadFile = File(...), file2: UploadFile = File(...), threshold: float = 0.6):
    """
    Accepts two image files. Returns verification result, boxes and similarity score.
    """
    try:
        img1 = read_imagefile(file1)
        img2 = read_imagefile(file2)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Invalid image upload: {e}")

    face1, box1 = get_face_and_box(img1)
    face2, box2 = get_face_and_box(img2)

    if face1 is None or face2 is None:
        return JSONResponse(status_code=200, content={
            "ok": False,
            "reason": "Face not detected in one or both images.",
            "boxes1": box1,
            "boxes2": box2
        })

    emb1 = tensor_to_embedding(face1)
    emb2 = tensor_to_embedding(face2)
    score = cosine_similarity(emb1, emb2)
    same = score >= threshold
    result = "same person" if same else "different person"

    response = {
        "ok": True,
        "verification_result": result,
        "similarity_score": score,
        "threshold": threshold,
        "boxes1": box1,
        "boxes2": box2
    }
    return JSONResponse(status_code=200, content=response)
