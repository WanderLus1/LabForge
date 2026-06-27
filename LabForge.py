import subprocess
import os


# --------------------------------------------------
# Escape LaTeX Special Characters (for text fields)
# --------------------------------------------------
def escape_latex(text):

    replacements = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }

    for key, value in replacements.items():
        text = text.replace(key, value)

    return text


# --------------------------------------------------
# Build Full LaTeX Document
# --------------------------------------------------
def build_document(name, roll_no, lab_no, date,
                   questions, codes, outputs,
                   language=None):

    body = ""

    for i in range(len(questions)):

        q = escape_latex(questions[i]).replace("\n", "\\\\\n")
        o = escape_latex(outputs[i]).replace("\n", "\\\\\n")
        c = codes[i].replace("\r\n", "\n")  # listings handles special chars safely

        body += f"""
\\textbf{{Question {i+1}:}}

{q}

\\textbf{{Solution {i+1}:}}

Code:
\\begin{{lstlisting}}
{c}
\\end{{lstlisting}}

Output:
\\begin{{outputbox}}
\\ttfamily
{o}
\\end{{outputbox}}

\\vspace{{1em}}
\\hrule
\\vspace{{1em}}
"""

    document = f"""
\\documentclass[12pt]{{article}}

\\usepackage[a4paper,margin=1in]{{geometry}}
\\usepackage{{hyperref}}
\\usepackage{{xurl}}
\\usepackage{{parskip}}
\\usepackage{{xcolor}}
\\usepackage{{listings}}
\\usepackage{{float}}
\\usepackage{{tcolorbox}}

\\lstset{{
    basicstyle=\\ttfamily\\small,
    numbers=left,
    numbersep=8pt,
    breaklines=true,
    frame=single
}}

\\newtcolorbox{{outputbox}}{{
  colback=gray!8,
  colframe=gray!50,
  boxrule=0.6pt,
  arc=4pt,
}}

\\title{{Lab {escape_latex(str(lab_no))}}}
\\author{{{escape_latex(str(name))} \\\\ {escape_latex(str(roll_no))}}}
\\date{{{escape_latex(str(date))}}}

\\begin{{document}}

\\maketitle
\\hrule
\\vspace{{1em}}

{body}

\\end{{document}}
"""

    return document


# --------------------------------------------------
# Compile LaTeX to PDF
# --------------------------------------------------
def compile_latex(tex_path):

    import subprocess
    import os

    directory = os.path.dirname(tex_path)
    filename = os.path.basename(tex_path)

    result = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", filename],
        cwd=directory,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    if result.returncode != 0:
        print(result.stdout.decode())
        print(result.stderr.decode())
        raise Exception("LaTeX compilation failed.")

    pdf_path = os.path.join(
        directory,
        filename.replace(".tex", ".pdf")
    )

    return pdf_path