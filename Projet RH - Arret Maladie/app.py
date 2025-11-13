from __future__ import annotations

import io
import re
import zipfile
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from tempfile import NamedTemporaryFile, TemporaryDirectory
from typing import Iterable, List, Tuple

import pandas as pd
import pdfplumber
import streamlit as st


DATE_PATTERN = re.compile(r"\d{2}/\d{2}/\d{4}")
AMOUNT_PATTERN = re.compile(r"(\d[\d\s]*,\d{2})\s*€")


class ExtractionError(Exception):
    """Custom exception raised when data cannot be extracted from a PDF document."""


@dataclass
class ExtractionResult:
    """Container for a single PDF extraction result."""

    payment_date: str
    beneficiary: str
    benefit_type: str
    start_date: str
    end_date: str
    quantity: int
    gross_amount: float
    net_amount: float

    def to_row(self) -> dict:
        """Return a dictionary formatted for DataFrame consumption."""
        return {
            "Date de paiement": self.payment_date,
            "Bénéficiaire": self.beneficiary,
            "Nature de la prestation": self.benefit_type,
            "Du": self.start_date,
            "Au": self.end_date,
            "Quantité": self.quantity,
            "Montant remboursé brut": self.gross_amount,
            "Montant remboursé net": self.net_amount,
        }


def _initialise_session_state() -> None:
    """Ensure all expected keys exist in Streamlit session state."""
    defaults = {
        "uploaded_file": None,
        "dataframe": None,
        "excel_bytes": None,
        "excel_filename": None,
        "errors": [],
        "summary": {"success": 0, "failed": 0},
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def normalise_text_lines(text: str) -> List[str]:
    """Split PDF text into cleaned, whitespace-normalised lines."""
    cleaned = text.replace("\xa0", " ").replace("\u202f", " ")
    return [line.strip() for line in cleaned.splitlines() if line.strip()]


def parse_amount(value: str) -> float:
    """Convert a French-formatted amount string into a float."""
    normalised = value.replace("€", "").replace(" ", "").replace("\xa0", "")
    return float(normalised.replace(",", "."))


def extract_payment_date(text: str) -> str:
    """Extract the payment (journée) date from the PDF text."""
    match = re.search(r"Journée du\s*(\d{2}/\d{2}/\d{4})", text)
    if not match:
        raise ExtractionError("Date de paiement introuvable.")
    return match.group(1)


def extract_beneficiary(lines: Iterable[str]) -> str:
    """Extract the beneficiary name located in the document heading."""
    for line in lines:
        if "Détail des prestations pour" in line:
            return line.split("pour", 1)[-1].strip()
    raise ExtractionError("Bénéficiaire introuvable.")


def extract_benefit_row(lines: Iterable[str]) -> Tuple[str, str, str, int, float]:
    """
    Extract the main benefit row containing start/end dates, benefit type,
    quantity, and gross amount.
    """
    for line in lines:
        if " au " not in line:
            continue
        dates = DATE_PATTERN.findall(line)
        if len(dates) < 2:
            continue
        start_date, end_date = dates[0], dates[1]
        after_end = line.split(end_date, 1)[-1].strip()
        amount_matches = AMOUNT_PATTERN.findall(after_end)
        if not amount_matches:
            continue
        gross_amount = parse_amount(amount_matches[-1])
        benefit_match = re.search(r"(.+?)\s+(\d+)\s+\d[\d\s]*,\d{2}\s*€", after_end)
        if not benefit_match:
            continue
        benefit_type = benefit_match.group(1).strip()
        quantity = int(benefit_match.group(2))
        return start_date, end_date, benefit_type, quantity, gross_amount
    raise ExtractionError("Ligne de prestation principale introuvable.")


def extract_total_amount(lines: Iterable[str]) -> float:
    """Extract the total reimbursed amount from the PDF text."""
    for line in lines:
        if line.lower().startswith("total"):
            amount_match = AMOUNT_PATTERN.search(line)
            if amount_match:
                return parse_amount(amount_match.group(0))
    raise ExtractionError("Montant total remboursé introuvable.")


@st.cache_data(show_spinner=False)
def extract_pdf_text(file_bytes: bytes) -> str:
    """Return the concatenated text extracted from all pages of a PDF file."""
    try:
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            text_fragments = [(page.extract_text() or "") for page in pdf.pages]
    except Exception as exc:  # pragma: no cover - defensive
        raise ExtractionError(f"Impossible de lire le fichier PDF ({exc}).") from exc
    return "\n".join(text_fragments)


def extract_from_pdf(pdf_path: Path) -> ExtractionResult:
    """Extract structured information from a single PDF document."""
    full_text = extract_pdf_text(pdf_path.read_bytes())
    lines = normalise_text_lines(full_text)
    payment_date = extract_payment_date(full_text)
    beneficiary = extract_beneficiary(lines)
    start_date, end_date, benefit_type, quantity, gross_amount = extract_benefit_row(lines)
    net_amount = extract_total_amount(lines)

    return ExtractionResult(
        payment_date=payment_date,
        beneficiary=beneficiary,
        benefit_type=benefit_type,
        start_date=start_date,
        end_date=end_date,
        quantity=quantity,
        gross_amount=gross_amount,
        net_amount=net_amount,
    )


def build_dataframe(records: List[ExtractionResult]) -> pd.DataFrame:
    """Construct a pandas DataFrame from extracted records."""
    data = [record.to_row() for record in records]
    df = pd.DataFrame(data)
    date_columns = ["Date de paiement", "Du", "Au"]
    for column in date_columns:
        df[column] = pd.to_datetime(df[column], format="%d/%m/%Y", errors="coerce")
    return df


def export_to_excel(df: pd.DataFrame) -> Tuple[bytes, str]:
    """Create an Excel file in-memory and return bytes and filename."""
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Extraction")
    buffer.seek(0)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"extractions_{timestamp}.xlsx"
    return buffer.getvalue(), filename


def process_zip_bytes(file_bytes: bytes) -> Tuple[List[ExtractionResult], List[str]]:
    """
    Unzip and process all PDF documents contained in the uploaded archive.
    Returns a tuple of successful records and error messages.
    """
    with TemporaryDirectory() as temp_dir_name:
        temp_dir = Path(temp_dir_name)
        with NamedTemporaryFile(delete=False, suffix=".zip") as tmp_zip:
            tmp_zip.write(file_bytes)
            zip_path = Path(tmp_zip.name)

        try:
            with zipfile.ZipFile(zip_path, "r") as archive:
                archive.extractall(temp_dir)
        except zipfile.BadZipFile as exc:
            raise ExtractionError("Le fichier ZIP semble corrompu.") from exc
        finally:
            zip_path.unlink(missing_ok=True)

        pdf_files = sorted(temp_dir.rglob("*.pdf"))
        if not pdf_files:
            raise ExtractionError("Aucun fichier PDF trouvé dans l'archive.")

        results: List[ExtractionResult] = []
        errors: List[str] = []
        progress_bar = st.progress(0, text="Préparation de l'extraction...")

        with st.status("Extraction des documents en cours...", expanded=True) as status:
            total_files = len(pdf_files)
            for index, pdf_file in enumerate(pdf_files, start=1):
                status.update(label=f"Traitement de `{pdf_file.name}`", state="running")
                try:
                    record = extract_from_pdf(pdf_file)
                    results.append(record)
                    status.write(f"✅ `{pdf_file.name}` traité avec succès.")
                except ExtractionError as error:
                    message = f"{pdf_file.name} — {error}"
                    errors.append(message)
                    status.write(f"❌ {message}")
                except Exception as unexpected_error:  # pragma: no cover - defensive
                    message = f"{pdf_file.name} — Erreur inattendue : {unexpected_error}"
                    errors.append(message)
                    status.write(f"❌ {message}")
                finally:
                    progress_bar.progress(index / total_files)

            if results:
                status.update(label="Extraction terminée ✅", state="complete")
            else:
                status.update(label="Extraction terminée sans succès ❌", state="error")

        return results, errors


def render_results() -> None:
    """Display extraction results, download option, and error summary."""
    dataframe: pd.DataFrame | None = st.session_state.get("dataframe")
    errors: List[str] = st.session_state.get("errors", [])
    summary = st.session_state.get("summary", {"success": 0, "failed": 0})

    if dataframe is not None:
        st.success(f"✅ Extraction terminée : {summary['success']} document(s) traités.")
        with st.expander("📊 Aperçu des données extraites", expanded=True):
            st.dataframe(dataframe.head(), use_container_width=True)

        excel_bytes = st.session_state.get("excel_bytes")
        excel_filename = st.session_state.get("excel_filename", "extractions.xlsx")
        st.download_button(
            label="📥 Télécharger le fichier Excel",
            data=excel_bytes,
            file_name=excel_filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            type="primary",
        )
    else:
        st.info("Aucune donnée disponible pour le moment. Importez un fichier ZIP pour commencer.")

    if errors:
        st.error(
            "❌ Certains documents n'ont pas pu être traités. Consultez les détails ci-dessous."
        )
        with st.expander("📄 Détails des erreurs"):
            for error in errors:
                st.write(f"- {error}")


def main() -> None:
    """Streamlit entry point."""
    st.set_page_config(page_title="Extraction CPAM", page_icon="📁", layout="wide")
    _initialise_session_state()

    st.title("📁 Extraction des remboursements CPAM")
    st.markdown(
        """
        Cette application extrait automatiquement les principales informations de paiement
        à partir d'un lot de relevés CPAM (format PDF) et génère un fichier Excel récapitulatif.
        Chargez un fichier ZIP contenant vos documents pour lancer l'analyse. 📄
        """
    )

    upload_col, action_col = st.columns([3, 1])
    with upload_col:
        uploaded_file = st.file_uploader(
            "Déposez ici votre archive ZIP contenant les relevés CPAM",
            type=["zip"],
            accept_multiple_files=False,
            help="Le fichier ne doit pas dépasser 200 Mo.",
        )
        if uploaded_file:
            st.session_state["uploaded_file"] = uploaded_file

    with action_col:
        st.markdown("### ")
        extraction_ready = st.session_state.get("uploaded_file") is not None
        extract_clicked = st.button(
            "📄 Extraire les données",
            type="primary",
            use_container_width=True,
            disabled=not extraction_ready,
        )

    if extract_clicked and st.session_state.get("uploaded_file"):
        uploaded_file = st.session_state["uploaded_file"]
        file_bytes = uploaded_file.getvalue()
        try:
            records, errors = process_zip_bytes(file_bytes)
            dataframe = build_dataframe(records) if records else pd.DataFrame(
                columns=[
                    "Date de paiement",
                    "Bénéficiaire",
                    "Nature de la prestation",
                    "Du",
                    "Au",
                    "Quantité",
                    "Montant remboursé brut",
                    "Montant remboursé net",
                ]
            )
            st.session_state["dataframe"] = dataframe
            st.session_state["errors"] = errors
            st.session_state["summary"] = {"success": len(records), "failed": len(errors)}

            if not dataframe.empty:
                excel_bytes, excel_filename = export_to_excel(dataframe)
                st.session_state["excel_bytes"] = excel_bytes
                st.session_state["excel_filename"] = excel_filename
            else:
                st.session_state["excel_bytes"] = None
                st.session_state["excel_filename"] = None

        except ExtractionError as critical_error:
            st.session_state["dataframe"] = None
            st.session_state["errors"] = [str(critical_error)]
            st.session_state["summary"] = {"success": 0, "failed": 1}
            st.error(f"❌ Extraction interrompue : {critical_error}")

    render_results()

    st.divider()
    if st.button("🔄 Recommencer", type="secondary"):
        st.session_state.clear()
        st.rerun()


if __name__ == "__main__":
    main()
import re
import zipfile
from datetime import datetime
from io import BytesIO
from pathlib import Path
from typing import Dict, List, Tuple

import pandas as pd
import pdfplumber
import streamlit as st


FRENCH_DATE_PATTERN = r"\d{2}/\d{2}/\d{4}"


def initialize_state() -> None:
    """Ensure Streamlit session state contains expected keys."""
    defaults = {
        "uploaded_file": None,
        "extraction_results": [],
        "extraction_errors": [],
        "is_processing": False,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def format_french_number(value: str) -> float:
    """Convert French-formatted numbers (comma decimal, spaces) into float."""
    normalized = (
        value.replace("\u202f", "")
        .replace("\xa0", "")
        .replace(" ", "")
        .replace("€", "")
        .strip()
        .replace(",", ".")
    )
    return float(normalized)


def extract_payment_date(text: str) -> str:
    match = re.search(r"Journée du\s+(%s)" % FRENCH_DATE_PATTERN, text)
    return match.group(1) if match else ""


def extract_beneficiary(text: str) -> str:
    match = re.search(
        r"D[ée]tail des prestations pour\s+([A-ZÀÂÄÇÉÈÊËÎÏÔÖÙÛÜŸ'’ -]+)", text
    )
    if match:
        return " ".join(match.group(1).split())
    return ""


def extract_table_line(text: str) -> Tuple[str, str, str, str, str]:
    """
    Extract the row containing the benefit information.
    Expected structure:
    02/01/2025 au 05/01/2025 Indemnités journalières 3 450,00 €
    """
    pattern = re.compile(
        r"(?P<start>{date})\s+au\s+(?P<end>{date})\s+(?P<benefit>.+?)\s+"
        r"(?P<quantity>\d+(?:[.,]\d+)?)\s+(?P<amount>{number})".format(
            date=FRENCH_DATE_PATTERN, number=r"[\d\s.,]+"
        ),
        re.MULTILINE,
    )
    for match in pattern.finditer(text):
        benefit = match.group("benefit").strip()
        # Sometimes the benefit name can include trailing price columns;
        # safeguard by stopping before obvious monetary patterns.
        benefit = re.split(r"\s+\d+(?:[.,]\d+)?\s+(?:€|{n})".format(n=r"[\d\s.,]+"), benefit)[0].strip()
        return (
            match.group("start"),
            match.group("end"),
            benefit,
            match.group("quantity"),
            match.group("amount"),
        )
    return "", "", "", "", ""


def extract_total_amount(text: str) -> str:
    match = re.search(r"Total\s*:\s*([\d\s.,]+)", text)
    return match.group(1).strip() if match else ""


def extract_document_data(pdf_path: Path) -> Dict[str, str]:
    """Extract required data fields from a PDF document using pdfplumber."""
    with pdfplumber.open(pdf_path) as pdf:
        pages_text = "\n".join(page.extract_text() or "" for page in pdf.pages)

    if not pages_text.strip():
        raise ValueError("Aucun texte lisible n'a été détecté dans le PDF.")

    payment_date = extract_payment_date(pages_text)
    beneficiary = extract_beneficiary(pages_text)
    start_date, end_date, benefit_type, quantity, gross_amount = extract_table_line(
        pages_text
    )
    net_amount = extract_total_amount(pages_text)

    missing_fields = [
        field
        for field, value in {
            "Date de paiement": payment_date,
            "Bénéficiaire": beneficiary,
            "Du": start_date,
            "Au": end_date,
            "Nature de la prestation": benefit_type,
            "Quantité": quantity,
            "Montant remboursé brut": gross_amount,
            "Montant remboursé net": net_amount,
        }.items()
        if not value
    ]

    if missing_fields:
        raise ValueError(
            "Informations manquantes: " + ", ".join(missing_fields)
        )

    return {
        "Date de paiement": payment_date,
        "Bénéficiaire": beneficiary,
        "Nature de la prestation": benefit_type,
        "Du": start_date,
        "Au": end_date,
        "Quantité": quantity,
        "Montant remboursé brut": gross_amount,
        "Montant remboursé net": net_amount,
    }


def generate_excel(data: List[Dict[str, str]]) -> BytesIO:
    """Create an Excel file from extracted data and return it as a buffer."""
    df = pd.DataFrame(data)
    df["Quantité"] = df["Quantité"].apply(format_french_number)
    df["Montant remboursé brut"] = df["Montant remboursé brut"].apply(format_french_number)
    df["Montant remboursé net"] = df["Montant remboursé net"].apply(format_french_number)

    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, sheet_name="Extraction")
    buffer.seek(0)
    return buffer


def process_zip_file(zip_bytes: BytesIO) -> Tuple[List[Dict[str, str]], List[str]]:
    """Unzip uploaded file and process each contained PDF."""
    results: List[Dict[str, str]] = []
    errors: List[str] = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        with zipfile.ZipFile(zip_bytes) as zip_ref:
            zip_ref.extractall(tmp_dir)

        pdf_paths = sorted(Path(tmp_dir).rglob("*.pdf"))

        if not pdf_paths:
            errors.append("Aucun fichier PDF trouvé dans l'archive.")
            return results, errors

        progress_bar = st.progress(0)
        status_placeholder = st.empty()

        total = len(pdf_paths)
        for idx, pdf_path in enumerate(pdf_paths, start=1):
            status_placeholder.info(f"Extraction du document {idx}/{total} : {pdf_path.name}")
            try:
                data = extract_document_data(pdf_path)
                results.append(data)
            except Exception as error:  # noqa: BLE001
                errors.append(f"{pdf_path.name} — {error}")
            finally:
                progress_bar.progress(idx / total)

        status_placeholder.empty()

    return results, errors


def reset_app() -> None:
    """Reset all session state keys to initial values."""
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    initialize_state()


def main() -> None:
    st.set_page_config(
        page_title="Extraction CPAM",
        page_icon="🩺",
        layout="centered",
    )

    initialize_state()

    st.title("Extraction des remboursements CPAM")
    st.markdown(
        """
        Téléversez une archive `.zip` contenant vos relevés PDF CPAM. 
        L'application extraira automatiquement les informations de remboursement
        et générera un fichier Excel prêt à l'emploi.
        """
    )

    with st.expander("Instructions"):
        st.markdown(
            """
            1. Cliquez sur **Parcourir** pour sélectionner votre archive `.zip`.
            2. Vérifiez que les documents sont lisibles et non protégés par mot de passe.
            3. Appuyez sur **Extraire les données** pour lancer le traitement.
            4. Téléchargez le fichier Excel généré.
            """
        )

    uploaded_file = st.file_uploader(
        "Archive CPAM (.zip)", type="zip", accept_multiple_files=False
    )

    if uploaded_file is not None:
        st.session_state.uploaded_file = BytesIO(uploaded_file.getvalue())

    extract_button = st.button(
        "Extraire les données",
        disabled=st.session_state.is_processing
        or st.session_state.uploaded_file is None,
        type="primary",
    )

    if extract_button and st.session_state.uploaded_file:
        st.session_state.is_processing = True
        with st.spinner("Extraction en cours..."):
            results, errors = process_zip_file(st.session_state.uploaded_file)
        st.session_state.extraction_results = results
        st.session_state.extraction_errors = errors
        st.session_state.is_processing = False

    results = st.session_state.extraction_results
    errors = st.session_state.extraction_errors

    if results:
        st.success(f"{len(results)} document(s) traités avec succès.")
        st.dataframe(pd.DataFrame(results))

        excel_buffer = generate_excel(results)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"extractions_{timestamp}.xlsx"
        st.download_button(
            "Télécharger le fichier Excel",
            data=excel_buffer,
            file_name=filename,
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

    if errors:
        st.error("Certains documents n'ont pas pu être traités :")
        for error in errors:
            st.markdown(f"- {error}")

    if st.button("Recommencer", type="secondary"):
        reset_app()
        st.experimental_rerun()


if __name__ == "__main__":
    main()

