import csv
import io
import json
from langchain_openai import ChatOpenAI
from langchain_core.utils.json import parse_json_markdown # 🚀 Bulletproof parser
from config import LOCAL_MODEL, OLLAMA_BASE_URL, OPENAI_API_KEY

async def parse_messy_csv(csv_content: str) -> list[dict]:
    """Reads a messy CSV and standardizes it using an LLM to map columns (ASYNC)."""
    if not csv_content or not csv_content.strip():
        return []

    # 1. Read raw CSV
    f = io.StringIO(csv_content.strip())
    reader = csv.reader(f)
    rows = list(reader)
    
    if len(rows) < 2:
        return []

    headers = rows[0]
    sample_data = rows[1:4] 
    
    # 🚀 ENFORCING STRICT JSON MODE USING CONFIG VARIABLES
    llm = ChatOpenAI(
        model=LOCAL_MODEL, 
        base_url=OLLAMA_BASE_URL, 
        api_key=OPENAI_API_KEY, 
        temperature=0,
        model_kwargs={"response_format": {"type": "json_object"}} # Forces pure JSON output
    )
    
    prompt = f"""
    You are a data extraction tool. I have a CSV with the following headers: {headers}
    Here is some sample data: {sample_data}
    
    Map the CSV headers to these exact standard keys: "name", "email", "phone", "role".
    If a standard key doesn't exist in the data, map it to null.
    
    Return ONLY a valid JSON dictionary where the keys are the original CSV headers, and the values are the standard keys.
    Example: {{"Participant Name": "name", "Contact Mail": "email", "Phone #": "phone", "Type": "role"}}
    
    CRITICAL: Output ONLY the JSON object. Do not include greetings, explanations, or markdown formatting blocks like ```json.
    """
    
    try:
        # 🚀 USE AINVOKE FOR NON-BLOCKING SPEED
        response = await llm.ainvoke(prompt)
        
        # 🚀 USE THE BULLETPROOF PARSER
        column_mapping = parse_json_markdown(response.content)
        
    except Exception as e:
        print(f"[*] CSV Parser Error: {e}")
        # Hardcoded fallback
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
                val = row[i].strip() if i < len(row) else ""
                contact[standard_key] = val
        standardized_contacts.append(contact)
        
    return standardized_contacts