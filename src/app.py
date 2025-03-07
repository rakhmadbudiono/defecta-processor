import streamlit as st
import pandas as pd
import openai
import pdfplumber
from fuzzywuzzy import process
from pydantic import BaseModel
import logging

logging.basicConfig(level=logging.INFO)


class Product(BaseModel):
    product_name: str
    final_price: float


class Distributor(BaseModel):
    products: list[Product]
    distributor_name: str


def read_excel(file):
    try:
        return pd.read_excel(file)
    except Exception as e:
        logging.error(f"Error reading Excel file: {e}")
        return pd.DataFrame()


def read_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() or ""
        return text
    except Exception as e:
        logging.error(f"Error reading PDF file: {e}")
        return ""


def split_text_into_chunks(text, max_length=40000, overlap=10):
    words = text.split()
    chunks = []
    current_chunk = []
    overlap_words = words[:overlap]

    for word in words:
        current_chunk.append(word)
        if len(" ".join(current_chunk)) >= max_length:
            chunks.append(" ".join(current_chunk[:-overlap]))
            current_chunk = overlap_words + [word]
            overlap_words = current_chunk[-overlap:]

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks


def process_unstructured_data(text):
    chunks = split_text_into_chunks(text)
    processed_results = []

    for chunk in chunks:
        try:
            response = openai.beta.chat.completions.parse(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a helpful assistant that extracts product information from text. Prices are in Indonesian Rupiah (IDR). Final price most of the times mentioned as HNA+PPN. Ensure to process the entire text and provide a complete list of products.",
                    },
                    {
                        "role": "user",
                        "content": f"Extract product information from the following text: {chunk}",
                    },
                ],
                response_format=Distributor,
            )
            processed_results.append(response.choices[0].message.parsed)
        except Exception as e:
            logging.error(f"Error processing chunk: {e}")

    return processed_results


def process_distributor_data(distributor_files):
    distributor_data = {}
    for file in distributor_files:
        logging.info(f"Processing file: {file.name}")
        if file.name.endswith(".xlsx"):
            distributor_df = read_excel(file)
            text = distributor_df.to_string()
        elif file.name.endswith(".pdf"):
            text = read_pdf(file)
        else:
            logging.warning(f"Unsupported file type: {file.name}")
            continue

        processed_data = process_unstructured_data(text)
        for distributor in processed_data:
            if distributor.distributor_name not in distributor_data:
                distributor_data[distributor.distributor_name] = {}
            for product in distributor.products:
                distributor_data[distributor.distributor_name][
                    product.product_name
                ] = product.final_price

    return distributor_data


st.title("Search Product in Distributor Files")

distributor_files = st.file_uploader(
    "Upload Distributor Files", type=["xlsx", "pdf"], accept_multiple_files=True
)

if distributor_files:
    if "distributor_data" not in st.session_state:
        st.session_state.distributor_data = process_distributor_data(distributor_files)
    distributor_data = st.session_state.distributor_data

    search_query = st.text_input("Search for a product in distributor files:")

    if search_query:
        found_products = []
        normalized_query = search_query.lower()

        product_names = []
        for distributor in distributor_data:
            for product in distributor_data[distributor]:
                product_names.append(product)
        matches = process.extract(normalized_query, product_names, limit=None)

        for matched_product, score in matches:
            if score >= 80:
                for distributor in distributor_data:
                    if matched_product in distributor_data[distributor]:
                        found_products.append(
                            {
                                "Product Name": matched_product,
                                "Final Price": distributor_data[distributor][
                                    matched_product
                                ],
                                "Distributor": distributor,
                            }
                        )

        if found_products:
            st.write("Found Products:")
            df_found_products = pd.DataFrame(found_products)
            st.dataframe(df_found_products)
        else:
            st.write("No products found matching your search.")
