# Face Authentication — Task 2 (FastAPI + facenet-pytorch)

**Project**: Face Verification service that accepts two images, detects faces, computes embeddings and returns verification result, similarity score and bounding boxes.

---

## Features
- MTCNN face detection (facenet-pytorch)
- InceptionResnetV1 (pretrained on VGGFace2) for face embeddings
- Cosine-similarity based verification
- FastAPI service: `POST /verify` accepts two images and returns JSON
- Train script to build a gallery of mean embeddings per identity (saved as `gallery_embeddings.npz`)
- Test script to verify pairs and query gallery

---

## Requirements
See `requirements.txt`. Install with:
```bash
pip install -r requirements.txt
