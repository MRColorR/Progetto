from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/factorial', methods=['POST'])
def factorial():
    data = request.get_json()
    number = data.get('number')
    if not number:
        return jsonify({'error': 'number is required'}), 400
    result = 1
    for i in range(1, number+1):
        result *= i
    return jsonify({'number': number, 'factorial': result})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
