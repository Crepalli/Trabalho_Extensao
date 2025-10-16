import os
from flask import Flask, request, jsonify
from flask_cors import CORS
import cloudinary
import cloudinary.uploader
import cloudinary.utils

# 1. Configuração da Aplicação
app = Flask(__name__)
CORS(app)

# Obtendo variáveis de ambiente (Credenciais de acesso ao Cloudinary)
CLOUD_NAME = os.environ.get("CLOUDINARY_CLOUD_NAME")
API_KEY = os.environ.get("CLOUDINARY_API_KEY")
API_SECRET = os.environ.get("CLOUDINARY_API_SECRET")

# Configuração do Cloudinary
if CLOUD_NAME and API_KEY and API_SECRET:
    cloudinary.config( 
      cloud_name = CLOUD_NAME, 
      api_key = API_KEY, 
      api_secret = API_SECRET,
      secure = True
    )
else:
    # Se as chaves não estiverem no Vercel, o código falha aqui
    print("ERRO CRÍTICO: Credenciais do Cloudinary ausentes nas Variáveis de Ambiente!")


@app.route("/remover-fundo", methods=["POST"])
def remover_fundo():
    # Primeira verificação: Garantir que as credenciais foram carregadas
    if not CLOUD_NAME or not API_KEY or not API_SECRET:
        return jsonify({"erro": "Configuração do Cloudinary ausente. Verifique as Variáveis de Ambiente no Vercel."}), 500

    try:
        arquivos = request.files.getlist("imagens")
        urls_processadas = []

        if not arquivos:
            return jsonify({"erro": "Nenhuma imagem enviada"}), 400

        for arquivo in arquivos:
            # 2. FAZ O UPLOAD do arquivo diretamente para o Cloudinary
            # Usando 'resource_type="auto"' para suportar múltiplos formatos
            upload_result = cloudinary.uploader.upload(
                arquivo, 
                folder="background-removal-temp",
                resource_type="auto"
            )
            
            # 3. VERIFICAÇÃO DE SUCESSO DO UPLOAD
            if 'public_id' not in upload_result:
                 # Esta exceção aparecerá nos logs do Vercel
                 raise Exception(f"Upload para o Cloudinary falhou. Resposta: {upload_result}")

            original_public_id = upload_result['public_id']
            
            # 4. GERA A URL DA IMAGEM COM A TRANSFORMAÇÃO
            # e_background_removal - Remove o fundo (exige o Add-on ativo)
            # f_auto, q_auto - Otimização de formato e qualidade
            transformed_url = cloudinary.utils.cloudinary_url(
                original_public_id,
                fetch_format="png", # PNG para manter a transparência
                effect="e_background_removal", 
                quality="auto" 
            )[0]
            
            urls_processadas.append(transformed_url)

        # 5. RETORNA UMA LISTA DE URLS (e não Base64)
        return jsonify({"imagens": urls_processadas})
        
    except Exception as e:
        # Retorna o erro capturado para o cliente e logs
        return jsonify({"erro": f"Erro no processamento: {str(e)}"}), 500
