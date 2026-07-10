from flask import Flask, render_template, request, redirect, url_for
from prometheus_flask_exporter import PrometheusMetrics
import redis
import json
import os
import uuid

app = Flask(__name__)

metrics = PrometheusMetrics(app)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))

r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)

TASK_KEY = "tasks"


def get_tasks():
    data = r.get(TASK_KEY)
    if data:
        return json.loads(data)
    return []


def save_tasks(tasks):
    r.set(TASK_KEY, json.dumps(tasks))


@app.route("/")
def index():
    tasks = get_tasks()
    return render_template("index.html", tasks=tasks)


@app.route("/add", methods=["POST"])
def add_task():
    title = request.form.get("title")

    if title:
        tasks = get_tasks()

        tasks.append({
            "id": str(uuid.uuid4()),
            "title": title,
            "completed": False
        })

        save_tasks(tasks)

    return redirect(url_for("index"))


@app.route("/complete/<task_id>")
def complete_task(task_id):
    tasks = get_tasks()

    for task in tasks:
        if task["id"] == task_id:
            task["completed"] = True

    save_tasks(tasks)

    return redirect(url_for("index"))


@app.route("/delete/<task_id>")
def delete_task(task_id):
    tasks = get_tasks()

    tasks = [task for task in tasks if task["id"] != task_id]

    save_tasks(tasks)

    return redirect(url_for("index"))


@app.route("/health")
def health():
    try:
        r.ping()
        return {
            "status": "UP",
            "redis": "Connected"
        }, 200
    except Exception:
        return {
            "status": "DOWN",
            "redis": "Disconnected"
        }, 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
