import csv
import io
import json
import re
from langchain_openai import ChatOpenAI
from config import LOCAL_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY

def parse_messy_csv(csv_content: str) -> list[dict]:
    """Reads a messy CSV and standardizes it using an LLM to map columns."""
    if not csv_content.strip():
        return []

    # 1. Read raw CSV
    f = io.StringIO(csv_content.strip())
    reader = csv.reader(f)
    rows = list(reader)
    
    if len(rows) < 2:
        return []

    headers = rows[0]
    sample_data = rows[1:4] # Just give the LLM a taste of the data to help it guess
    
    # 2. Ask the Local LLM to map the messy headers to standard keys
    llm = ChatOpenAI(model=LOCAL_MODEL, base_url=OLLAMA_BASE_URL, api_key=OPENAI_API_KEY, temperature=0)
    
    prompt = f"""
    You are a data extraction tool. I have a CSV with the following headers: {headers}
    Here is some sample data: {sample_data}
    
    Map the CSV headers to these exact standard keys: "name", "email", "phone", "role".
    If a standard key doesn't exist in the data, map it to null.
    
    Return ONLY a valid JSON dictionary where the keys are the original CSV headers, and the values are the standard keys.
    Example: {{"Participant Name": "name", "Contact Mail": "email", "Phone #": "phone", "Type": "role"}}
    """
    
    try:
        response = llm.invoke(prompt)
        raw_output = response.content
        
        # 👇 --- HIGHLIGHT: REGEX EXTRACTION ADDED HERE --- 👇
        # Find everything between the first { and last }
        match = re.search(r'\{.*\}', raw_output, re.DOTALL)
        if match:
            clean_json = match.group(0)
        else:
            clean_json = raw_output.replace("```json", "").replace("```", "").strip()
            
        column_mapping = json.loads(clean_json)
        
    except Exception as e:
        print(f"[*] CSV Parser Error: Failed to parse LLM JSON: {e}")
        print(f"[*] Raw LLM output was: {raw_output if 'raw_output' in locals() else 'None'}")
        
        # 👇 --- HIGHLIGHT: HARDCODED FALLBACK IF LLM FAILS --- 👇
        # If the model goes crazy, we do a basic manual check of the headers so it doesn't crash
        column_mapping = {}
        for h in headers:
            hl = h.lower()
            if "name" in hl or "identity" in hl: column_mapping[h] = "name"
            elif "mail" in hl: column_mapping[h] = "email"
            elif "phone" in hl or "mobile" in hl or "digit" in hl: column_mapping[h] = "phone"
            elif "type" in hl or "role" in hl: column_mapping[h] = "role"
            else: column_mapping[h] = "null"

    # 3. Standardize the entire dataset
    standardized_contacts = []
    for row in rows[1:]:
        contact = {}
        for i, header in enumerate(headers):
            standard_key = column_mapping.get(header)
            if standard_key and standard_key != "null":
                # Basic cleanup
                val = row[i].strip() if i < len(row) else ""
                contact[standard_key] = val
        standardized_contacts.append(contact)
        
    return standardized_contacts