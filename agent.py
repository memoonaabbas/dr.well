"""
agent.py — Dr. Well AI Agent (Fixed Version)
"""

import os
import re
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage

load_dotenv()

# ─────────────────────────────────────────────
# Model Setup
# ─────────────────────────────────────────────
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=0.3,
)

# ─────────────────────────────────────────────
# Doctor Prompt
# ─────────────────────────────────────────────
DOCTOR_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are Dr. Well, a caring and professional AI doctor.

IMPORTANT RULES (follow strictly):

1. First ask about symptoms - never give treatment without understanding the problem
2. Keep messages SHORT (max 3-4 lines per reply)
3. Use simple, friendly English - like talking to a friend
4. Be calm, helpful, and professional
5. Once symptoms are clear, suggest home care + medicine if needed
6. For EMERGENCIES say: "Please go to hospital immediately!" or "Call 911!"
7. If patient needs a specialist, mention it clearly

RESPONSE FORMAT when prescribing medicine:
- Always write: "Take [MedicineName] [dosage]" (e.g., "Take Paracetamol 500mg")

EXAMPLES:

Dr. Well: Hello! I'm Dr. Well. What symptoms are you experiencing today?

Dr. Well: Any fever or body pain with that cough?

Dr. Well: Sounds like a mild cold. Rest well, drink warm water. Take Paracetamol 500mg if you have fever.

Dr. Well: Chest pain can be serious. Please go to hospital immediately!

DO NOT:
- Write very long responses
- Use complicated medical terms
- Give treatment without knowing symptoms
- Say "As an AI..."

AVAILABLE DOCTORS IN NETWORK:
{doctors_info}

PATIENT INFORMATION:
{patient_info}
"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# ─────────────────────────────────────────────
# Nutrition Prompt
# ─────────────────────────────────────────────
NUTRITION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """You are NutriBot, a friendly and knowledgeable nutritionist.

Give practical, personalized diet advice based on the user's condition or goal.

Structure your response as:
✅ **What to Eat** (list 4-5 items with brief reason)
❌ **What to Avoid** (list 3-4 items)
🍽️ **Sample Meal Plan** (breakfast, lunch, dinner)
💡 **Quick Tip** (one helpful tip)

Keep it short, clear, and easy to follow. Use bullet points.
"""),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}")
])

# ─────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────

def extract_medications(response_text: str) -> list:
    """Extract medicine names and dosages from response"""
    meds = []
    seen = set()

    # Pattern: "Take Paracetamol 500mg"
    pattern1 = r"[Tt]ake\s+([A-Za-z][A-Za-z\s]{1,30}?)\s+(\d+\s*(?:mg|ml|g|mcg|tablet|cap|capsule)s?)"
    matches1 = re.findall(pattern1, response_text)
    for match in matches1:
        name = match[0].strip()
        if name.lower() not in seen:
            seen.add(name.lower())
            meds.append({
                "name": name,
                "dosage": match[1].strip(),
                "timing": "As needed"
            })

    # Pattern: "Medicine: X | Dose: Y"
    pattern2 = r"[Mm]edicine:?\s*([^|\n,]+?)\s*\|?\s*[Dd]ose:?\s*([^|\n,]+)"
    matches2 = re.findall(pattern2, response_text)
    for match in matches2:
        name = match[0].strip()
        if name.lower() not in seen:
            seen.add(name.lower())
            meds.append({
                "name": name,
                "dosage": match[1].strip(),
                "timing": "As advised"
            })

    return meds


def detect_specialty_needed(response_text: str) -> str | None:
    """Detect if a specialist referral is mentioned"""
    specialty_map = {
        "cardiologist": "Cardiologist",
        "heart specialist": "Cardiologist",
        "chest pain": "Cardiologist",
        "dermatologist": "Dermatologist",
        "skin specialist": "Dermatologist",
        "neurologist": "Neurologist",
        "brain specialist": "Neurologist",
        "orthopedic": "Orthopedic Surgeon",
        "bone specialist": "Orthopedic Surgeon",
        "pediatrician": "Pediatrician",
        "child specialist": "Pediatrician",
        "psychiatrist": "Psychiatrist",
        "mental health": "Psychiatrist",
        "ophthalmologist": "Ophthalmologist",
        "eye specialist": "Ophthalmologist",
        "ent specialist": "ENT Specialist",
        "ear nose throat": "ENT Specialist",
        "gynecologist": "Gynecologist",
        "general physician": "General Physician",
    }

    text_lower = response_text.lower()
    for keyword, specialty in specialty_map.items():
        if keyword in text_lower:
            return specialty
    return None


def is_nutrition_question(message: str) -> bool:
    """Check if the message is about food or diet"""
    keywords = [
        "diet", "food", "eat", "nutrition", "meal", "recipe",
        "what should i eat", "avoid food", "healthy food",
        "weight loss", "weight gain", "calories", "nutrients",
        "diet advice", "nutribot", "diabetes food", "bp food"
    ]
    return any(kw in message.lower() for kw in keywords)


def build_history(history: list) -> list:
    """Convert dict history to LangChain message objects"""
    messages = []
    for msg in history:
        if isinstance(msg, dict):
            role = msg.get("role", "")
            content = msg.get("content", "")
            if role == "user":
                messages.append(HumanMessage(content=content))
            elif role == "assistant":
                messages.append(AIMessage(content=content))
        elif isinstance(msg, (HumanMessage, AIMessage)):
            messages.append(msg)
    # Keep last 10 messages to avoid context overflow
    return messages[-10:]


# ─────────────────────────────────────────────
# Core Response Functions
# ─────────────────────────────────────────────

def get_doctor_response(user_input: str, history: list, doctors_info: str, patient_info: str) -> str:
    """Get medical advice from Dr. Well"""
    chain = DOCTOR_PROMPT | llm
    response = chain.invoke({
        "doctors_info": doctors_info or "No doctor info available",
        "patient_info": patient_info or "New patient",
        "history": build_history(history),
        "input": user_input
    })
    return response.content


def get_nutrition_response(user_input: str, history: list) -> str:
    """Get diet/nutrition advice from NutriBot"""
    chain = NUTRITION_PROMPT | llm
    response = chain.invoke({
        "history": build_history(history),
        "input": user_input
    })
    return response.content


# ─────────────────────────────────────────────
# Main run_agent Function (called by main.py)
# ─────────────────────────────────────────────

def run_agent(
    user_message: str,
    user_id: int,
    session_id: str,
    history: list,
    doctors_info: str,
    patient_info: str
) -> dict:
    """
    Main agent entry point called by main.py.
    Returns a dict with:
      - response: str
      - extracted_meds: list
      - referred_specialty: str | None
    """
    try:
        # Route to nutrition or doctor
        if is_nutrition_question(user_message) or session_id == "nutrition":
            response_text = get_nutrition_response(user_message, history)
            return {
                "response": response_text,
                "extracted_meds": [],
                "referred_specialty": None
            }
        else:
            response_text = get_doctor_response(user_message, history, doctors_info, patient_info)
            meds = extract_medications(response_text)
            specialty = detect_specialty_needed(response_text)
            return {
                "response": response_text,
                "extracted_meds": meds,
                "referred_specialty": specialty
            }

    except Exception as e:
        return {
            "response": f"I'm sorry, I encountered an issue. Please try again. ({str(e)[:100]})",
            "extracted_meds": [],
            "referred_specialty": None
        }


# ─────────────────────────────────────────────
# CLI Chatbot (for testing)
# ─────────────────────────────────────────────

def chat_with_doctor():
    """Simple CLI chatbot loop"""
    print("""
    🏥 ======================================
       Welcome to Dr. Well AI Clinic
       Your caring virtual doctor
    ======================================
    """)
    print("🤖 Dr. Well: Hello! I'm Dr. Well. What symptoms are you experiencing?\n")
    print("💡 Type 'exit', 'quit', or 'bye' to end the chat\n")

    doctors_info = "Dr. Sarah - Cardiologist | Dr. Ahmed - General Physician | Dr. Priya - Dermatologist"
    patient_info = "New patient"
    history = []

    while True:
        user_input = input("🧑‍⚕️ You: ").strip()
        if user_input.lower() in ["exit", "quit", "bye"]:
            print("\n🤖 Dr. Well: Take care! Visit a real doctor if needed. Goodbye! 👋\n")
            break
        if not user_input:
            continue

        result = run_agent(
            user_message=user_input,
            user_id=0,
            session_id="cli",
            history=history,
            doctors_info=doctors_info,
            patient_info=patient_info
        )

        response = result["response"]

        if result["extracted_meds"]:
            print("\n💊 Medicines suggested:")
            for med in result["extracted_meds"]:
                print(f"   - {med['name']} ({med['dosage']})")
            print()

        if result["referred_specialty"]:
            print(f"👨‍⚕️ Referral: Please consult a {result['referred_specialty']}\n")

        print(f"🤖 Dr. Well: {response}\n")

        history.append({"role": "user", "content": user_input})
        history.append({"role": "assistant", "content": response})
        if len(history) > 12:
            history = history[-12:]


if __name__ == "__main__":
    chat_with_doctor()