# NOVO ARQUIVO: api/index.py (versão Cloudinary)

from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import os
import base64

app = Flask(__name__)
CORS(app)

# Configurações do Cloudinary (Obtenha estes valores do seu Dashboard)
# É altamente recomendável usar VARIÁVEIS DE AMBIENTE no Vercel para armazenar estas chaves!
cloudinary.config( 
  cloud_name = os.environ.get("CLOUDINARY_CLOUD_NAME"), 
  api_key = os.environ.get("CLOUDINARY_API_KEY"), 
  api_secret = os.environ.get("CLOUDINARY_API_SECRET"),
  secure = True
)

# Endpoint da API para remover fundo
@app.route("/remover-fundo", methods=["POST"])
def remover_fundo():
    try:
        arquivos = request.files.getlist("imagens")
        resultados = []

        if not arquivos:
            return jsonify({"erro": "Nenhuma imagem enviada"}), 400

        for arquivo in arquivos:
            # 1. Faz o upload da imagem original para o Cloudinary
            upload_result = cloudinary.uploader.upload(arquivo, folder="background-removal-temp")
            
            original_public_id = upload_result['public_id']
            
            # 2. Gera a URL da imagem com a transformação de remoção de fundo
            # Atenção: 'e_background_removal' é o Add-on. Pode ter custos/limites.
            # Verifique as instruções do Cloudinary sobre como habilitar e usar.
            transformed_url = cloudinary.utils.cloudinary_url(
                original_public_id,
                fetch_format="png", # PNG para manter a transparência
                effect="e_background_removal" # Comando de remoção de fundo
            )[0]
            
            # O Cloudinary retorna a URL. Agora precisamos converter para Base64 para manter a compatibilidade com o frontend
            # O código original espera Base64. É mais eficiente retornar a URL, mas manteremos o Base64 para o seu frontend.
            
            # Para manter o frontend simples, vamos carregar a imagem da URL e transformá-la em base64.
            # Isto é menos eficiente do que apenas retornar a URL transformada!
            import requests
            response = requests.get(transformed_url)
            
            if response.status_code == 200:
                img_base64 = base64.b64encode(response.content).decode("utf-8")
                resultados.append(f"data:image/png;base64,{img_base64}")
            else:
                raise Exception(f"Erro ao obter imagem processada do Cloudinary: {response.status_code}")

        # Opcional: Limpar as imagens temporárias do Cloudinary para economizar espaço
        # Não faremos aqui para manter a simplicidade.

        return jsonify({"imagens": resultados})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500
