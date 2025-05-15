#engine.py: 최종 챗봇 로직이 구현될 실제 엔진

# engine.py
from nlp.matcher import IntentMatcher
from nlp.parser import EntityParser

class ChatbotEngine:
    def __init__(self):
        self.matcher = IntentMatcher()
        self.parser = EntityParser()

    def respond(self, user_input):
        intent = self.matcher.match(user_input)
        if intent == 'weather':
            location = self.parser.extract_location(user_input)
            if location:
                return f"The weather in {location} is sunny!"  # 여기 나중에 API 연결 가능
            else:
                return "Which location are you asking about?"
        elif intent == 'greeting':
            return "Hello! How can I help you today?"
        elif intent == 'farewell':
            return "Goodbye! Have a great day."
        else:
            return "Sorry, I didn't understand that."

# 테스트용 실행
if __name__ == '__main__':
    bot = ChatbotEngine()
    while True:
        user_input = input("You: ")
        if user_input.lower() in ['quit', 'exit']:
            break
        print("Bot:", bot.respond(user_input))

