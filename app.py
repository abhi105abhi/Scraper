import os
import traceback
from flask import Flask, render_template, request, jsonify
from agent import DeepScraperAgent

app = Flask(__name__)

# GLOBAL STATUS
agent_logs = []

execution_status = {
    "running": False,
    "progress": 0,
    "message": "Idle"
}


def add_log(message):
    global agent_logs

    print(message)

    agent_logs.append(message)

    if len(agent_logs) > 200:
        agent_logs = agent_logs[-200:]


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/health")
def health():
    return jsonify({
        "status": "online"
    })


@app.route("/logs")
def logs():
    return jsonify({
        "logs": agent_logs,
        "progress": execution_status["progress"],
        "running": execution_status["running"],
        "message": execution_status["message"]
    })


@app.route("/progress")
def progress():
    return jsonify({
        "logs": agent_logs,
        "progress": execution_status["progress"],
        "running": execution_status["running"],
        "message": execution_status["message"]
    })


@app.route("/launch", methods=["POST"])
def launch_scraper():

    global execution_status
    global agent_logs

    # RESET
    agent_logs = []

    execution_status = {
        "running": True,
        "progress": 0,
        "message": "Initializing..."
    }

    try:

        # SUPPORT JSON + FORM DATA
        data = request.get_json(silent=True)

        if not data:
            data = request.form

        city = data.get("city", "").strip()
        api_key = data.get("api_key", "").strip()

        if not city:
            raise Exception("Target city missing.")

        if not api_key:
            raise Exception("Gemini API key missing.")

        add_log("[System] Initializing connection stream...")
        execution_status["progress"] = 10

        add_log("[System] Initializing temporary folder arrays...")
        execution_status["progress"] = 20

        # INIT AGENT
        agent = DeepScraperAgent(
            api_key=api_key,
            logger=add_log
        )

        execution_status["progress"] = 35

        add_log("[System] Linked to Gemini AI. Building targeted logic prompts...")

        # TEST API
        test = agent.test_connection()

        if not test:
            raise Exception("Gemini API connection failed.")

        execution_status["progress"] = 50

        add_log("[Agent] Gemini API verified.")

        # GENERATE STRATEGY
        strategy = agent.generate_scraping_strategy(city)

        if not strategy:
            raise Exception("Gemini returned empty strategy.")

        execution_status["progress"] = 85

        add_log("[Agent] Parsing architecture generated successfully.")

        execution_status["progress"] = 100
        execution_status["running"] = False
        execution_status["message"] = "Execution completed."

        add_log("[System] Scraper agent execution completed successfully.")

        return jsonify({
            "success": True,
            "strategy": strategy,
            "logs": agent_logs
        })

    except Exception as e:

        execution_status["running"] = False
        execution_status["progress"] = 0
        execution_status["message"] = "Execution Interrupted."

        error_msg = f"[Error] {str(e)}"

        add_log(error_msg)

        traceback.print_exc()

        return jsonify({
            "success": False,
            "error": str(e),
            "logs": agent_logs
        }), 500


if __name__ == "__main__":

    port = int(os.environ.get("PORT", 5000))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False
    )
