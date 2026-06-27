from flask import Flask, render_template, request, redirect, send_file, session
import uuid
import os
import tempfile

app = Flask(__name__)
app.secret_key = "replace_this_with_a_long_random_secret_key"


# ==================================
# INDEX (STEP 1 FORM)
# ==================================
@app.route("/", methods=["GET", "POST"])
def index():

    if request.method == "POST":
        name = request.form["name"]
        roll_no = request.form["roll"]
        lab_no = request.form["lab_no"]
        date = request.form["date"]
        no_of_Qn = int(request.form["num_questions"])
        language = request.form["language"]

        return render_template(
            "QnA.html",
            name=name,
            roll_no=roll_no,
            lab_no=lab_no,
            date=date,
            language=language,
            num_questions=no_of_Qn
        )

    return render_template("index.html")


# ==================================
# QnA SUBMISSION (STEP 2)
# ==================================
@app.route("/QnA", methods=["POST"])
def QnA():

    name = request.form["name"]
    roll_no = request.form["roll_no"]
    lab_no = request.form["lab_no"]
    date = request.form["date"]
    language = request.form["language"]
    num_questions = int(request.form["num_questions"])

    questions = []
    codes = []
    outputs = []

    for i in range(1, num_questions + 1):
        questions.append(request.form[f"question_{i}"])
        codes.append(request.form[f"code_{i}"].replace("\r\n", "\n"))
        outputs.append(request.form[f"output_{i}"])

    from LabForge import build_document, compile_latex

    latex_content = build_document(
        name,
        roll_no,
        lab_no,
        date,
        questions,
        codes,
        outputs,
        language
    )

    # ===== CREATE ISOLATED TEMP DIRECTORY =====
    temp_dir = tempfile.mkdtemp()
    unique_id = str(uuid.uuid4())

    tex_path = os.path.join(temp_dir, f"{unique_id}.tex")

    with open(tex_path, "w", encoding="utf-8") as f:
        f.write(latex_content)

    pdf_path = compile_latex(tex_path)

    # Store full path in session
    session["pdf_path"] = pdf_path

    return redirect("/assignment_ready")


# ==================================
# FINAL PAGE
# ==================================
@app.route("/assignment_ready")
def assignment_ready():
    return render_template("assignment_ready.html")


# ==================================
# PREVIEW
# ==================================
@app.route("/preview")
def preview():

    pdf_path = session.get("pdf_path")

    if not pdf_path or not os.path.exists(pdf_path):
        return "No PDF found. Please generate a report first.", 400

    response = send_file(pdf_path, as_attachment=False)
    response.headers["Cache-Control"] = "no-store"
    return response


# ==================================
# DOWNLOAD
# ==================================
@app.route("/download")
def download():

    pdf_path = session.get("pdf_path")

    if not pdf_path or not os.path.exists(pdf_path):
        return "No PDF found. Please generate a report first.", 400

    return send_file(pdf_path, as_attachment=True)


if __name__ == "__main__":
    app.run(debug=True)