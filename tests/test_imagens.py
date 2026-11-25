import io
import unittest
from pathlib import Path
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest

from analise import abrir_imagem


def jpeg_com_imagem_auxiliar():
    buffer = io.BytesIO()
    exif = Image.Exif()
    exif[274] = 6
    Image.new("RGB", (1600, 1200), "red").save(
        buffer, format="MPO", save_all=True, exif=exif,
        append_images=[Image.new("RGB", (400, 300), "blue")],
    )
    return buffer.getvalue()


class LeituraDeImagens(unittest.TestCase):
    def test_jpeg_com_imagem_auxiliar_usa_foto_principal_e_orientacao(self):
        conteudo = jpeg_com_imagem_auxiliar()
        with Image.open(io.BytesIO(conteudo)) as original:
            self.assertEqual(original.format, "MPO")
            self.assertEqual(original.n_frames, 2)
        imagem = abrir_imagem(conteudo)
        self.assertEqual(imagem.mode, "RGB")
        self.assertEqual(imagem.size, (768, 1024))
        vermelho, verde, azul = imagem.getpixel((0, 0))
        self.assertGreater(vermelho, 240)
        self.assertLess(verde, 10)
        self.assertLess(azul, 10)

    def test_formatos_convencionais_continuam_aceitos(self):
        for formato in ("JPEG", "PNG", "WEBP"):
            with self.subTest(formato=formato):
                buffer = io.BytesIO()
                Image.new("RGB", (80, 60), "white").save(buffer, format=formato)
                self.assertEqual(abrir_imagem(buffer.getvalue()).size, (80, 60))

    def test_formato_nao_suportado_continua_rejeitado(self):
        buffer = io.BytesIO()
        Image.new("RGB", (80, 60), "white").save(buffer, format="GIF")
        with self.assertRaisesRegex(ValueError, "JPG, PNG ou WebP"):
            abrir_imagem(buffer.getvalue())

    def test_upload_jpeg_com_imagem_auxiliar_habilita_analise(self):
        with patch("vlm_client.verificar_configuracao", return_value=None):
            app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py")).run()
            app.file_uploader[0].set_value(
                ("foto.jpeg", jpeg_com_imagem_auxiliar(), "image/jpeg")
            ).run()
        self.assertFalse(app.exception)
        self.assertFalse(app.error)
        self.assertFalse(app.button(key="analisar").disabled)


if __name__ == "__main__":
    unittest.main()
