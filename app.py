from flask import Flask, request, render_template_string
import cv2
import numpy as np
import base64
import colorsys
import os

app = Flask(__name__)

HTML_CODE = """
<!DOCTYPE html>
<html>
<head>
    <title>Нүүрний өнгө тодорхойлогч</title>
    <style>
        body { font-family: Arial; text-align: center; margin-top: 50px; background-color: #f4f4f9;}
        .container { background: white; padding: 30px; border-radius: 15px; box-shadow: 0px 0px 15px rgba(0,0,0,0.1); display: inline-block;}
        button { background-color: #4CAF50; color: white; padding: 12px 24px; border: none; border-radius: 5px; cursor: pointer; font-size: 16px;}
        .result { font-size: 18px; color: #d32f2f; margin-top: 15px; line-height: 1.6;}
    </style>
</head>
<body>
    <div class="container">
        <h2>Нүүрний зургаа оруулна уу</h2>
        <form method="POST" enctype="multipart/form-data">
            <input type="file" name="file" accept="image/*" required>
            <br><br>
            <button type="submit">Шинжлэх</button>
        </form>
        {% if result %}
            <h3 class="result">{{ result|safe }}</h3>
            <img src="data:image/jpeg;base64,{{ image_data }}" style="max-width:300px; margin-top:20px; border-radius:10px;" />
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file:
            img_bytes = file.read()
            npimg = np.frombuffer(img_bytes, np.uint8)
            img = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
            img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

            face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, 1.1, 4)

            result_text = "Нүүр олдсонгүй! Өөр зураг оруулна уу."
            if len(faces) > 0:
                for (x, y, w, h) in faces:
                    roi = img_rgb[y + int(h/2):y + h, x + int(w/4):x + int(3*w/4)]
                    avg_color = np.mean(roi, axis=(0, 1)).astype(int)
                    
                    r, g, b = [val / 255.0 for val in avg_color]
                    h_val, l_val, s_val = colorsys.rgb_to_hls(r, g, b)
                    h_deg = h_val * 360
                    
                    if (h_deg >= 0 and h_deg <= 50) or (h_deg >= 330 and h_deg <= 360):
                        undertone = "Дулаан (Warm)"
                    else:
                        undertone = "Хүйтэн (Cool)"
                        
                    if l_val > 0.6: depth = "Цайвар"
                    elif l_val < 0.3: depth = "Бараан"
                    else: depth = "Дунд"
                        
                    if "Дулаан" in undertone:
                        if depth == "Цайвар": season = "Хавар 🌸"
                        elif depth == "Бараан": season = "Намар 🍁"
                        else: season = "Дулаан (Намар/Хавар)"
                    else:
                        if depth == "Цайвар": season = "Зун ☀️"
                        elif depth == "Бараан": season = "Өвөл ❄️"
                        else: season = "Хүйтэн (Зун/Өвөл)"

                    rgb_clean = f"{avg_color[0]}, {avg_color[1]}, {avg_color[2]}"
                    result_text = f"Арьсны өнгө: {undertone}<br>Гэрэлтэлт: {depth}<br>Улирлын төрөл: <b>{season}</b><br>(RGB: {rgb_clean})"
                    
                    _, buffer = cv2.imencode('.jpg', img)
                    image_data = base64.b64encode(buffer).decode('utf-8')
                    return render_template_string(HTML_CODE, result=result_text, image_data=image_data)
            
            return render_template_string(HTML_CODE, result=result_text)
    return render_template_string(HTML_CODE)

# Сервер дээр ажиллах тохиргоо
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
