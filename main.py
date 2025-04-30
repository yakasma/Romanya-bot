import requests
import fitz  # PyMuPDF
import smtplib
from email.mime.text import MIMEText

# REFERANSLAR
reference_numbers = ["ABC123", "XYZ456", "LMN789"]

# PDF İNDİR
def download_pdf(url, filename):
    response = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(response.content)

# REFERANS ARA
def search_references_in_pdf(pdf_path, references):
    found = []
    doc = fitz.open(pdf_path)
    for page in doc:
        text = page.get_text()
        for ref in references:
            if ref in text:
                found.append(ref)
    return found

# E-POSTA GÖNDER
def send_email(found_refs):
    msg = MIMEText(f"Bulunan referanslar: {', '.join(found_refs)}")
    msg['Subject'] = "Romanya Vatandaşlık Kontrolü"
    msg['From'] = "seninmailin@gmail.com"
    msg['To'] = "seninmailin@gmail.com"

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("seninmailin@gmail.com", "GMAIL_APP_SIFRESI")
        smtp.send_message(msg)

def main():
    pdf_url = "https://siteadresin.com/sonuclar.pdf"
    filename = "sonuclar.pdf"
    download_pdf(pdf_url, filename)
    found = search_references_in_pdf(filename, reference_numbers)
    if found:
        send_email(found)

if __name__ == "__main__":
    main()
