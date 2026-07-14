from flask import Flask, render_template, request, send_file, redirect
from compare import compare_documents
from database import create_table,save_history,get_history,delete_history,get_dashboard_data

import os
import csv
from datetime import datetime

from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle
)

from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors


app = Flask(__name__)


# Create database table
create_table()


UPLOAD_FOLDER = "uploads"

ALLOWED_EXTENSIONS = {
    "pdf",
    "docx",
    "txt",
    "html",
    "htm"
}


if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


latest_result = {}



def allowed_file(filename):

    return (
        "." in filename
        and
        filename.rsplit(".", 1)[1].lower()
        in ALLOWED_EXTENSIONS
    )



@app.route("/")
def home():

    return render_template(
        "index.html"
    )





@app.route("/compare", methods=["POST"])
def compare():


    if "file1" not in request.files or "file2" not in request.files:

        return "Please upload both files."



    file1 = request.files["file1"]
    file2 = request.files["file2"]



    if file1.filename == "" or file2.filename == "":

        return "Please select both files."



    if not allowed_file(file1.filename):

        return "Invalid File 1. Allowed: PDF, DOCX, TXT, HTML"



    if not allowed_file(file2.filename):

        return "Invalid File 2. Allowed: PDF, DOCX, TXT, HTML"




    path1 = os.path.join(
        UPLOAD_FOLDER,
        file1.filename
    )


    path2 = os.path.join(
        UPLOAD_FOLDER,
        file2.filename
    )



    file1.save(path1)

    file2.save(path2)



    # Compare documents

    result = compare_documents(
        path1,
        path2
    )



    similarity = result["similarity"]

    comparison = result["diff"]

    differences = result["status"]


    compare_time = result["compare_time"]

    total_lines = result["total_lines"]

    words1 = result["words1"]

    words2 = result["words2"]

    characters1 = result["characters1"]

    characters2 = result["characters2"]




    # Store latest result for PDF

    latest_result["similarity"] = similarity

    latest_result["differences"] = differences

    latest_result["comparison"] = comparison

    latest_result["compare_time"] = compare_time

    latest_result["total_lines"] = total_lines

    latest_result["words1"] = words1

    latest_result["words2"] = words2

    latest_result["characters1"] = characters1

    latest_result["characters2"] = characters2




    # Save history

    save_history(

        file1.filename,

        file2.filename,

        similarity,

        differences

    )





    return render_template(

        "result.html",

        similarity=similarity,

        differences=differences,

        comparison=comparison,

        compare_time=compare_time,

        total_lines=total_lines,

        words1=words1,

        words2=words2,

        characters1=characters1,

        characters2=characters2

    )







@app.route("/download")
def download():


    pdf_file = "comparison_report.pdf"



    doc = SimpleDocTemplate(
        pdf_file
    )



    styles = getSampleStyleSheet()


    content = []



    content.append(

        Paragraph(
            "Document Comparison Report",
            styles["Heading1"]
        )

    )


    content.append(
        Spacer(1,20)
    )



    content.append(

        Paragraph(
            f"Generated On: {datetime.now().strftime('%d-%m-%Y %H:%M')}",
            styles["Normal"]
        )

    )



    content.append(
        Spacer(1,10)
    )



    content.append(

        Paragraph(
            f"Similarity Score: {latest_result.get('similarity')}%",
            styles["Normal"]
        )

    )



    content.append(

        Paragraph(
            f"Total Differences: {latest_result.get('differences')}",
            styles["Normal"]
        )

    )



    content.append(

        Paragraph(
            f"Comparison Time: {latest_result.get('compare_time')} seconds",
            styles["Normal"]
        )

    )



    content.append(
        Spacer(1,20)
    )



    table_data = [

        [
            "Line",
            "Document 1",
            "Document 2",
            "Status"
        ]

    ]



    for item in latest_result.get("comparison", []):


        doc1 = item["doc1"]

        doc2 = item["doc2"]



        # Remove HTML tags

        for tag in [
            "<span class='removed'>",
            "<span class='added'>",
            "</span>"
        ]:

            doc1 = doc1.replace(tag, "")

            doc2 = doc2.replace(tag, "")



        table_data.append(

            [

                str(item.get("line", "")),

                doc1,

                doc2,

                item["status"]

            ]

        )




    table = Table(

        table_data,

        repeatRows=1

    )



    table.setStyle(

        TableStyle(

            [

                (
                    "BACKGROUND",
                    (0,0),
                    (-1,0),
                    colors.grey
                ),

                (
                    "TEXTCOLOR",
                    (0,0),
                    (-1,0),
                    colors.white
                ),

                (
                    "GRID",
                    (0,0),
                    (-1,-1),
                    1,
                    colors.black
                )

            ]

        )

    )



    content.append(table)


    doc.build(content)



    return send_file(

        pdf_file,

        as_attachment=True

    )

@app.route("/history")
def history():

    search = request.args.get("search","")

    filter_value = request.args.get("filter","all")


    records = get_history(
        search,
        filter_value
    )


    return render_template(
        "history.html",
        records=records
    )



@app.route("/delete/<int:id>")
def delete(id):

    delete_history(id)

    return redirect("/history")








    
@app.route("/dashboard")
def dashboard():

    data = get_dashboard_data()


    return render_template(
        "dashboard.html",
        data=data
    )



    


    


    






if __name__ == "__main__":

    app.run(debug=True)