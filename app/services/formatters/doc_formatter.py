import shutil
import subprocess
from pathlib import Path

from app.core.exceptions import ExtractionError
from app.core.logging_config import logger
from app.interfaces.formatter import ExtractionResult
from app.services.formatters.base import BaseFormatter
from app.services.formatters.docx_formatter import DocxFormatter


class DocFormatter(BaseFormatter):
    """Legacy .doc support via local LibreOffice conversion to .docx.

    We do not claim to parse .doc directly. If LibreOffice (``soffice``) is not
    available, a clear error is raised instead of a silent failure. The
    conversion happens entirely on the local machine.
    """

    extensions = (".doc",)

    def __init__(self):
        self._docx = DocxFormatter()

    @staticmethod
    def libreoffice() -> str:
        for candidate in ("soffice", "libreoffice"):
            path = shutil.which(candidate)
            if path:
                return path
        return ""

    def _convert_to_docx(self, file_path: Path, workdir: Path) -> Path:
        soffice = self.libreoffice()
        if not soffice:
            raise ExtractionError(
                "Le format .doc nécessite LibreOffice pour la conversion locale. "
                "Installez-le : sudo apt install libreoffice-writer."
            )
        workdir.mkdir(parents=True, exist_ok=True)
        cmd = [soffice, "--headless", "--convert-to", "docx",
               "--outdir", str(workdir), str(file_path)]
        try:
            proc = subprocess.run(cmd, capture_output=True, timeout=180)
        except subprocess.TimeoutExpired:
            raise ExtractionError("Conversion .doc expirée (LibreOffice).")
        out = workdir / (file_path.stem + ".docx")
        if not out.exists():
            logger.warning("Sortie soffice: %s", proc.stdout.decode(errors="ignore"))
            raise ExtractionError("La conversion .doc vers .docx a échoué.")
        return out

    def extract(self, file_path: Path, options: dict = None) -> ExtractionResult:
        workdir = file_path.parent / (file_path.stem + "_conv")
        docx_path = self._convert_to_docx(file_path, workdir)
        result = self._docx.extract(docx_path, options)
        result.structure["_converted_docx"] = str(docx_path)
        result.warnings.append(
            "Fichier .doc converti localement via LibreOffice avant traduction."
        )
        return result

    def reconstruct(self, original_path, translations, structure, output_path):
        docx_path = Path(structure["_converted_docx"])
        result_docx = self._docx.reconstruct(docx_path, translations, structure,
                                             output_path.with_suffix(".docx"))
        return result_docx
