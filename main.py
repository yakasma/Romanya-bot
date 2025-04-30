import requests
import fitz  # PyMuPDF
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import os
import time

# REFERANSLAR
REFERENCE_CODES = ["21530/RD/2022", "21522/RD/2022", "21489/RD/2022"]

# PDF URL'lerini alma
def get_latest_pdf_links():
    url = "https://cetatenie.just.ro/ordine-articolul-1-1/"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")

    links = []
    for a in soup.find_all("a", href=True):
        href = a['href']
        if href.lower().endswith(".pdf") and "P" in href:
            if href.startswith("http"):
                links.append(href)
            else:
                links.append("https://cetatenie.just.ro" + href)
    return links[:5]  # Son 5 PDF'yi kontrol etmek yeterli

# PDF'de referans kodu arama
def search_references_in_pdf(pdf_url):
    found_refs = []
    try:
        response = requests.get(pdf_url)
        filename = f"temp_{int(time.time())}.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        doc = fitz.open(filename)
        for page in doc:
            text = page.get_text()
            for ref in REFERENCE_CODES:
                if ref in text:
                    found_refs.append(ref)
        os.remove(filename)
        return found_refs
    except Exception as e:
        print(f"Hata: {e}")
        return []

# Ortam değişkenleri
EMAIL = os.environ['EMAIL']
EMAIL_PASS = os.environ['EMAIL_PASS']

# E-posta gönderme fonksiyonu
def send_email(found_refs, found_pdf_url, checked_pdfs):
    if found_refs:
        body = (
            f"Aşağıdaki referanslar bulundu:\n\n"
            f"{', '.join(found_refs)}\n\n"
            f"Bulunduğu PDF: {found_pdf_url}\n\n"
            f"Kontrol edilen tüm PDF’ler:\n" +
            "\n".join(checked_pdfs)
        )
        subject = "✅ Romanya Vatandaşlık Listesi - Referans Bulundu"
    else:
        body = (
            "Hiçbir referans kodu bulunamadı.\n\n"
            "Bugün kontrol edilen PDF'ler:\n" +
            "\n".join(checked_pdfs)
        )
        subject = "ℹ️ Romanya Vatandaşlık - Sonuç Yok"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = EMAIL
    msg['To'] = "yigit.akasma@gmail.com"

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
            smtp.login(EMAIL, EMAIL_PASS)
            smtp.send_message(msg)
    except Exception as e:
        print(f"E-posta gönderimi sırasında hata: {e}")

# Ana fonksiyon
def main():
    print("Kontrol başlatıldı...")
    pdf_links = get_latest_pdf_links()
    checked_pdfs = []
    all_found = {}

    for pdf_url in pdf_links:
        checked_pdfs.append(pdf_url)
        found = search_references_in_pdf(pdf_url)
        if found:
            all_found[pdf_url] = found

    if all_found:
        for pdf, refs in all_found.items():
            send_email(refs, pdf, checked_pdfs)
            break
    else:
        send_email([], None, checked_pdfs)

    print("Kontrol tamamlandı.")

if __name__ == "__main__":
    main()
