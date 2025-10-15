const express = require("express");
const multer = require("multer");
const path = require("path");
const fs = require("fs");
const cors = require("cors");

const app = express();
const PORT = 5000;

app.use(cors());
app.use(express.json());
app.use(express.static("public"));

// Configuração do Multer (upload de imagens)
const storage = multer.diskStorage({
  destination: (req, file, cb) => {
    cb(null, "uploads/");
  },
  filename: (req, file, cb) => {
    cb(null, Date.now() + path.extname(file.originalname));
  },
});
const upload = multer({ storage: storage });

// Rota principal
app.get("/", (req, res) => {
  res.send("API de Remoção de Fundo está rodando 🚀");
});

// Rota para upload
app.post("/upload", upload.single("image"), (req, res) => {
  if (!req.file) {
    return res.status(400).json({ error: "Nenhum arquivo enviado" });
  }

  // Aqui você pode chamar a lógica de remoção de fundo
  // Por enquanto só retorna o caminho da imagem
  res.json({
    message: "Upload realizado com sucesso!",
    file: `/uploads/${req.file.filename}`,
  });
});

// Garantir que a pasta "uploads" existe
if (!fs.existsSync("uploads")) {
  fs.mkdirSync("uploads");
}

// Inicia o servidor
app.listen(PORT, () => {
  console.log(`Servidor rodando em http://localhost:${PORT}`);
});
