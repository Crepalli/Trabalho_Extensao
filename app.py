from flask import Flask, request, jsonify
from flask_cors import CORS
from rembg import remove
from PIL import Image
import io
import base64

app = Flask(__name__)
CORS(app)

@app.route("/remover-fundo", methods=["POST"])
def remover_fundo():
    try:
        arquivos = request.files.getlist("imagens")
        resultados = []

        for arquivo in arquivos:
            input_bytes = arquivo.read()
            output_bytes = remove(input_bytes)

            # Mantém em PNG (com transparência)
            img = Image.open(io.BytesIO(output_bytes)).convert("RGBA")

            buffer = io.BytesIO()
            img.save(buffer, format="PNG")  # Exporta como PNG
            img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

            resultados.append(f"data:image/png;base64,{img_base64}")

        return jsonify({"imagens": resultados})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True, port=3000)
