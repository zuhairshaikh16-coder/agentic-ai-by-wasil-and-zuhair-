from flask import Flask, render_template, request, jsonify
from agent import Agent

app = Flask(__name__)

agent = Agent()


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()

    user_message = data.get("message", "").strip()

    if not user_message:
        return jsonify({"error": "Message is required"}), 400

    try:
        answer = agent.run(user_message, verbose=False)

        return jsonify({
            "response": answer
        })

    except Exception as e:
        return jsonify({
            "error": str(e)
        }), 500


if __name__ == "__main__":
    app.run(debug=True)