import json
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import JsonOutputParser
from langchain_community.chat_models import ChatOllama

class UpdaterAgent:
    def __init__(self):
        print("[*] Initializing UpdaterAgent with Ollama (llama3.1:8b)...")
        # Connect to your local Ollama instance
        self.llm = ChatOllama(
            model="llama3.1:8b",   # Match the tag you have in Ollama
            temperature=0.1,       # Very low temperature for precise, deterministic edits
            format="json"          # 🚀 CRITICAL: Forces Llama 3.1 to output raw JSON without markdown formatting
        )

    async def process_update(self, instructions: str, schedule: list, outputs: dict) -> tuple[list, dict]:
        """
        Takes the user's instructions and smartly modifies ONLY the relevant parts 
        of the schedule or outputs using Llama 3.1.
        """
        parser = JsonOutputParser()

        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an Event Updater AI. Your job is to modify an existing event schedule or content based on user instructions.\n"
                       "You must output ONLY valid JSON. Do not include markdown blocks or conversational text.\n"
                       "Do NOT rewrite everything. Only change the specific items requested.\n"
                       "Return a strict JSON object with exactly two keys: 'schedule' and 'outputs'.\n"
                       "{format_instructions}"),
            ("human", "Current Schedule:\n{schedule}\n\n"
                      "Current Outputs:\n{outputs}\n\n"
                      "User Instruction: {instructions}\n\n"
                      "Apply the instruction and return the updated JSON.")
        ])

        # Create the LangChain pipeline
        chain = prompt | self.llm | parser
        
        print(f"[*] UpdaterAgent analyzing instruction via Ollama: '{instructions}'")
        
        try:
            # Invoke the local model asynchronously
            response = await chain.ainvoke({
                "schedule": json.dumps(schedule),
                "outputs": json.dumps(outputs),
                "instructions": instructions,
                "format_instructions": parser.get_format_instructions()
            })
            
            print("[✅] Ollama successfully generated updated JSON.")
            
            # Extract the updated values, fallback to original if the model missed a key
            updated_schedule = response.get("schedule", schedule)
            updated_outputs = response.get("outputs", outputs)
            
            return updated_schedule, updated_outputs

        except Exception as e:
            print(f"[❌] Error in UpdaterAgent (Ollama generation failed): {e}")
            # Safe fallback: return the original state so the UI doesn't crash
            return schedule, outputs