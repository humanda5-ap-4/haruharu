from flask import Flask, request, jsonify, render_template_string
from utils import save_log

app = Flask(__name__)

def generate_dummy_response(user_input):
    return f"임시 응답: '{user_input}'에 대한 답변입니다."

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_input = data.get('text', '').strip()

    if not user_input:
        return jsonify({'error': 'No input text provided.'}), 400

    response = generate_dummy_response(user_input)
    save_log(user_input, response)
    return jsonify({'response': response})

@app.route('/', methods=['GET', 'POST'])
def home():
    response_text = ''
    if request.method == 'POST':
        user_input = request.form.get('user_input', '').strip()
        if user_input:
            response_text = generate_dummy_response(user_input)
            save_log(user_input, response_text)
    return render_template_string('''
        <!doctype html>
        <html>
        <head><title>챗봇 입력폼</title></head>
        <body>
            <h2>챗봇에게 질문하세요</h2>
            <form method="post">
                <input type="text" name="user_input" style="width:300px;" placeholder="여기에 입력하세요" required>
                <button type="submit">전송</button>
            </form>
            {% if response_text %}
            <h3>챗봇 답변:</h3>
            <p>{{ response_text }}</p>
            {% endif %}
        </body>
        </html>
    ''', response_text=response_text)

if __name__ == '__main__':
    app.run(debug=True)

