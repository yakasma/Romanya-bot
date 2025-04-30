import requests
import fitz  # PyMuPDF
import smtplib
from email.mime.text import MIMEText
from bs4 import BeautifulSoup
import os

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
        filename = "temp.pdf"
        with open(filename, 'wb') as f:
            f.write(response.content)
        doc = fitz.open(filename)
        for page in doc:
            text = page.get_text()
            for ref in REFERENCE_CODES:
                if ref in text:
                    found_refs.append(ref)
        return found_refs
    except Exception as e:
        print(f"Hata: {e}")
        return []

# E-posta gönderme
def send_email(found_refs, pdf_url):
    body = f"Aşağıdaki referanslar bulundu:\n\n{', '.join(found_refs)}\n\nPDF Link: {pdf_url}"
    msg = MIMEText(body)
    msg['Subject'] = "✅ Romanya Vatandaşlık Listesi - Referans Bulundu"
    msg['From'] = os.environ['romanyabot@gmail.com']
    msg['To'] = os.environ['yigit.akasma@gmail.com']

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(os.environ['romanyabot@gmail.com'], os.environ['2330438y'])
        smtp.send_message(msg)

# Ana Fonksiyon
def main():
    print("Kontrol başlatıldı...")
    pdf_links = get_latest_pdf_links()
    for pdf_url in pdf_links:
        found = search_references_in_pdf(pdf_url)
        if found:
            send_email(found, pdf_url)
            break  # Birinde bulunduysa diğerlerini kontrol etmeye gerek yok
    print("Kontrol tamamlandı.")

if __name__ == "__main__":
    main()
