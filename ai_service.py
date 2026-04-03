import os
from typing import Dict, Any, List
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

class Conversation:
    def __init__(self):
        self.messages = []
    
    def add_user_message(self, message):
        self.messages.append({"role": "user", "content": message})
    
    def add_assistant_message(self, message):
        self.messages.append({"role": "assistant", "content": message})
    
    def get_history(self):
        return self.messages[-10:]  # Keep last 10 messages for context

class AIService:
    def __init__(self):
        self.gemini_key = os.getenv('GEMINI_API_KEY')
        self.provider = os.getenv('AI_PROVIDER', 'gemini')
        self.conversations = {}  # Store conversations by user/session
        
        if self.gemini_key and GEMINI_AVAILABLE:
            genai.configure(api_key=self.gemini_key)
            self.model = genai.GenerativeModel('gemini-pro')
            print("✅ Gemini AI initialized successfully")
        else:
            print("⚠️ Gemini AI not available, using enhanced fallback mode")
    
    def get_conversation(self, session_id):
        if session_id not in self.conversations:
            self.conversations[session_id] = Conversation()
        return self.conversations[session_id]
    
    def get_health_advice(self, query: str, health_data: Dict = None, session_id: str = "default"):
        try:
            conv = self.get_conversation(session_id)
            conv.add_user_message(query)
            
            context = ""
            if health_data:
                context = f"""
User Health Data:
- Blood Pressure: {health_data.get('bp_systolic', 'N/A')}/{health_data.get('bp_diastolic', 'N/A')} mmHg
- Heart Rate: {health_data.get('heart_rate', 'N/A')} BPM
- Blood Sugar: {health_data.get('blood_sugar', 'N/A')} mg/dL
- Weight: {health_data.get('weight', 'N/A')} kg
"""
            
            # Get conversation history
            history = conv.get_history()
            history_text = ""
            if len(history) > 1:
                history_text = "\nPrevious conversation:\n"
                for msg in history[-6:]:  # Last 6 messages for context
                    role = "User" if msg["role"] == "user" else "Assistant"
                    history_text += f"{role}: {msg['content']}\n"
            
            prompt = f"""You are a friendly, empathetic health assistant. Provide helpful, accurate health advice in a conversational way.
{context}
{history_text}
User: {query}
Assistant:"""
            
            if self.gemini_key and GEMINI_AVAILABLE:
                response = self.model.generate_content(prompt)
                reply = response.text
            else:
                reply = self._get_enhanced_fallback_response(query, health_data, history)
            
            conv.add_assistant_message(reply)
            
            return {
                'success': True,
                'response': reply,
                'provider': 'Google Gemini AI' if self.gemini_key else 'Enhanced Health Advisor'
            }
        except Exception as e:
            print(f"Error: {e}")
            return {
                'success': True,
                'response': self._get_enhanced_fallback_response(query, health_data, []),
                'provider': 'Fallback Mode'
            }
    
    def _get_enhanced_fallback_response(self, query: str, health_data: Dict = None, history: List = None):
        query_lower = query.lower()
        
        # Check if it's a follow-up question
        if history and len(history) > 0:
            last_assistant = None
            for msg in reversed(history):
                if msg["role"] == "assistant":
                    last_assistant = msg["content"]
                    break
            
            if last_assistant and any(word in query_lower for word in ['more', 'explain', 'tell me', 'what about', 'how']):
                return f"Based on our previous conversation about {last_assistant[:50]}... Here's more: " + self._get_detailed_response(query_lower)
        
        return self._get_detailed_response(query_lower, health_data)
    
    def _get_detailed_response(self, query: str, health_data: Dict = None):
        if 'bp' in query or 'blood pressure' in query:
            if health_data:
                bp_sys = health_data.get('bp_systolic', 120)
                bp_dia = health_data.get('bp_diastolic', 80)
                if bp_sys > 140 or bp_dia > 90:
                    return f"Your blood pressure is {bp_sys}/{bp_dia} mmHg, which is higher than normal (120/80). This could be concerning. I recommend: 1) Reduce salt intake, 2) Exercise regularly, 3) Monitor daily, 4) Consult your doctor if it persists. Would you like tips on managing high BP?"
                elif bp_sys < 90 or bp_dia < 60:
                    return f"Your blood pressure is {bp_sys}/{bp_dia} mmHg, which is lower than normal. This might cause dizziness. Make sure you're hydrated and avoid standing up too quickly. Should I share some tips to maintain healthy BP?"
                else:
                    return f"Your blood pressure is {bp_sys}/{bp_dia} mmHg, which is in the normal range! Great job maintaining healthy levels. Keep up with regular monitoring and a balanced lifestyle."
            return "Normal blood pressure is around 120/80 mmHg. To maintain healthy BP: eat less salt, exercise 30 mins daily, manage stress, and limit alcohol. Would you like specific diet recommendations?"
        
        elif 'sugar' in query or 'diabetes' in query:
            if health_data and health_data.get('blood_sugar'):
                sugar = health_data.get('blood_sugar')
                if sugar > 140:
                    return f"Your blood sugar is {sugar} mg/dL, which is high. Normal fasting sugar is 70-100 mg/dL. This needs attention. Tips: 1) Reduce sugar/carbs, 2) Exercise after meals, 3) Monitor regularly. Should I share a diabetic-friendly meal plan?"
                elif sugar < 70:
                    return f"Your blood sugar is {sugar} mg/dL, which is low! If you feel shaky or dizzy, eat something sweet immediately. Keep glucose tablets handy. Want to learn how to prevent low blood sugar?"
                else:
                    return f"Your blood sugar is {sugar} mg/dL, which is in the normal range! Keep maintaining a balanced diet and regular exercise. Would you like tips to keep it stable?"
            return "Normal blood sugar is 70-100 mg/dL fasting. To maintain healthy levels: eat complex carbs, avoid sugary drinks, exercise regularly, and monitor consistently. Want me to explain what affects blood sugar?"
        
        elif 'heart' in query or 'rate' in query or 'hr' in query:
            if health_data and health_data.get('heart_rate'):
                hr = health_data.get('heart_rate')
                if hr > 100:
                    return f"Your heart rate is {hr} BPM, which is elevated (normal: 60-100). This could be from stress, caffeine, or exercise. If persistent, consult a doctor. Would you like breathing exercises to lower heart rate?"
                elif hr < 60:
                    return f"Your heart rate is {hr} BPM, which is lower than average. This is common in athletes. If you feel dizzy or tired, please consult a doctor. Should I explain when low heart rate is concerning?"
                else:
                    return f"Your heart rate is {hr} BPM, which is in the healthy range! Good cardiovascular health. Want to learn how to improve your heart health further?"
            return "Normal resting heart rate is 60-100 BPM. Regular exercise strengthens your heart. Tips: stay hydrated, avoid excessive caffeine, manage stress. Would you like some heart-healthy exercises?"
        
        elif 'medication' in query or 'medicine' in query or 'pill' in query:
            return "Taking medications on time is crucial! Tips: 1) Set phone reminders, 2) Use a pill organizer, 3) Take with meals if needed, 4) Never skip doses. Would you like me to help you set up medication reminders in the app?"
        
        elif 'diet' in query or 'food' in query or 'eat' in query:
            return "For a healthy diet: 🥗 Eat colorful vegetables, 🍎 Fresh fruits, 🐟 Lean proteins, 🌾 Whole grains, 💧 Stay hydrated. Avoid processed foods and excess sugar. Would you like a sample meal plan for heart health or diabetes management?"
        
        elif 'exercise' in query or 'workout' in query or 'walk' in query:
            return "Aim for 150 minutes of moderate exercise weekly. Good options: 🚶 Walking 30 mins daily, 🏊 Swimming, 🧘 Yoga, 🚴 Cycling. Start slow and increase gradually. Should I create a beginner exercise plan for you?"
        
        elif 'stress' in query or 'anxiety' in query or 'relax' in query:
            return "To manage stress: 🧘 Deep breathing (4-7-8 method), 🌳 Take nature walks, 📝 Journal your thoughts, 😴 Get 7-8 hours sleep. Want to learn a quick 2-minute relaxation technique?"
        
        elif 'sleep' in query:
            return "Good sleep is essential! Tips: 😴 7-9 hours nightly, 📱 No screens 1 hour before bed, 🌙 Dark quiet room, 🕐 Consistent schedule. Would you like a bedtime routine guide?"
        
        elif 'thank' in query or 'thanks' in query:
            return "You're welcome! I'm here to help with any health questions. Remember, I'm an AI assistant, not a doctor. For medical emergencies, please use the SOS button. What else can I help you with today?"
        
        elif 'hi' in query or 'hello' in query or 'hey' in query:
            return "Hello! 👋 I'm your AI health assistant. I can help with questions about blood pressure, blood sugar, heart rate, medications, diet, exercise, and more. How are you feeling today? Or ask me anything about your health!"
        
        else:
            return f"I understand you're asking about {query[:50]}... As your health assistant, I can help with:\n\n• Blood pressure management\n• Blood sugar/diabetes care\n• Heart rate monitoring\n• Medication reminders\n• Diet & nutrition\n• Exercise plans\n• Stress & sleep tips\n\nWhat specific health topic would you like to discuss?"

    def predict_health_risk(self, health_data: Dict) -> Dict:
        try:
            bp_sys = health_data.get('bp_systolic', 120)
            bp_dia = health_data.get('bp_diastolic', 80)
            hr = health_data.get('heart_rate', 75)
            sugar = health_data.get('blood_sugar', 100)
            weight = health_data.get('weight', 70)

            risks = []
            recommendations = []

            if bp_sys > 140 or bp_dia > 90:
                risks.append("High Blood Pressure")
                recommendations.append("Monitor BP daily, reduce salt intake, exercise regularly, consult doctor")
            elif bp_sys < 90 or bp_dia < 60:
                risks.append("Low Blood Pressure")
                recommendations.append("Stay hydrated, avoid sudden position changes, increase salt slightly if advised")

            if hr > 100:
                risks.append("Tachycardia - High Heart Rate")
                recommendations.append("Rest, reduce caffeine, practice deep breathing, consult if persistent")
            elif hr < 60:
                risks.append("Bradycardia - Low Heart Rate")
                recommendations.append("Monitor for symptoms like dizziness, consult doctor if concerned")

            if sugar > 140:
                risks.append("High Blood Sugar")
                recommendations.append("Monitor diet, exercise after meals, consult doctor for management")
            elif sugar < 70:
                risks.append("Low Blood Sugar")
                recommendations.append("Have quick sugar source, eat regular meals, carry glucose tablets")

            if weight > 100:
                risks.append("High Weight")
                recommendations.append("Consider healthy diet plan, regular exercise, consult nutritionist")

            risk_level = "HIGH" if len(risks) > 1 else "MODERATE" if len(risks) == 1 else "LOW"

            return {
                'risk_level': risk_level,
                'risks': risks,
                'recommendations': recommendations,
                'summary': f"Risk Level: {risk_level}. {len(risks)} health concern(s) identified."
            }
        except Exception as e:
            return {
                'risk_level': 'MODERATE',
                'risks': ['Unable to analyze'],
                'recommendations': ['Please consult a doctor for accurate assessment'],
                'summary': 'Analysis temporary unavailable'
            }

ai_service = AIService()
