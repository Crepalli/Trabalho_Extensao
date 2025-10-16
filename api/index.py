import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import cloudinary.utils


app = Flask(__name__)
CORS(app)


CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
API_KEY = os.environ.get("CLOUDINARY_API_KEY")
API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")


if CLOUD_NAME and API_KEY and API_SECRET:
    cloudinary.config( 
      cloud_name = CLOUD_NAME, 
      api_key = API_KEY, 
      api_secret = API_SECRET,
      secure = True
    )
else:
    
    print("ERRO CRÍTICO: Credenciais do Cloudinary ausentes nas Variáveis de Ambiente!")


@app.route("/remover-fundo", methods=["POST"])
def remover_fundo():
    
    if not CLOUD_NAME or not API_KEY or not API_SECRET:
        return jsonify({"erro": "Configuração do Cloudinary ausente. Verifique as Variáveis de Ambiente no Vercel."}), 500

    try:
        arquivos = request.files.getlist("imagens")
        urls_processadas = []

        if not arquivos:
            return jsonify({"erro": "Nenhuma imagem enviada"}), 400

        for arquivo in arquivos:
            
            upload_result = cloudinary.uploader.upload(
                arquivo, 
                folder="background-removal-temp",
                resource_type="auto"
            )
            
            
            if 'public_id' not in upload_result:
                 
                 raise Exception(f"Upload para o Cloudinary falhou. Resposta: {upload_result}")

            original_public_id = upload_result['public_id']
            


            transformed_url = cloudinary.utils.cloudinary_url(
                original_public_id,
                fetch_format="png", 
            
                effect="background_removal", 
                flags="attachment"  
            )[0]
            
            
            urls_processadas.append(transformed_url)

        
        return jsonify({"imagens": urls_processadas})
        
    except Exception as e:
   
        return jsonify({"erro": f"Erro no processamento: {str(e)}"}), 500
