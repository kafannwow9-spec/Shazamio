from fastapi import FastAPI, File, HTTPException, UploadFile
import os
from shazamio import Shazam

app = FastAPI()


@app.post("/recognize")
async def recognize_song(file: UploadFile = File(...)):
  # حفظ الملف الصوتي المؤقت
  temp_file_path = f"temp_{file.filename}"
  try:
    with open(temp_file_path, "wb") as buffer:
      content = await file.read()
      buffer.write(content)

    # استخدام shazamio للتعرف على الأغنية
    shazam = Shazam()
    out = await shazam.recognize(temp_file_path)

    # التحقق من وجود نتيجة
    if not out or "track" not in out:
      raise HTTPException(
          status_code=404, detail="Could not identify the song."
      )

    track = out["track"]
    return {
        "title": track.get("title"),
        "artist": track.get("subtitle"),
        "shazam_url": track.get("share", {}).get("href"),
    }

  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))

  finally:
    # حذف الملف المؤقت بعد الانتهاء
    if os.path.exists(temp_file_path):
      os.remove(temp_file_path)


if __name__ == "__main__":
  import uvicorn

  uvicorn.run(app, host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
