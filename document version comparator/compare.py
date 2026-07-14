from difflib import ndiff
import time
import os

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity



def read_file(path):

    text = ""

    extension = os.path.splitext(path)[1].lower()



    # TXT

    if extension == ".txt":

        with open(
            path,
            "r",
            encoding="utf-8"
        ) as file:

            text = file.read()





    # DOCX

    elif extension == ".docx":

        from docx import Document

        doc = Document(path)


        for para in doc.paragraphs:

            text += para.text + "\n"






    # PDF

    elif extension == ".pdf":

        import PyPDF2


        with open(
            path,
            "rb"
        ) as pdf:

            reader = PyPDF2.PdfReader(pdf)


            for page in reader.pages:

                text += page.extract_text() or ""







    # HTML

    elif extension in [".html", ".htm"]:


        from bs4 import BeautifulSoup



        with open(
            path,
            "r",
            encoding="utf-8",
            errors="ignore"
        ) as file:


            soup = BeautifulSoup(
                file,
                "lxml"
            )





        # Remove unwanted HTML tags

        for tag in soup.find_all(
            [
                "script",
                "style",
                "noscript",
                "svg",
                "meta",
                "link",
                "code"
            ]
        ):

            tag.decompose()





        # Extract visible text

        text = soup.get_text(
            separator=" ",
            strip=True
        )






        # Remove web scraping / notebook unwanted text

        remove_words = [

            "In [",

            "Out[",

            "import requests",

            "import pandas",

            "import numpy",

            "response.status_code",

            "BeautifulSoup",

            "plt.show()"

        ]



        for word in remove_words:

            text = text.replace(
                word,
                ""
            )






        # Remove extra spaces

        text = " ".join(
            text.split()
        )






        # Limit very large files

        text = text[:200000]





    return text.strip()







def highlight_difference(old, new):


    old_words = old.split()

    new_words = new.split()



    diff = ndiff(
        old_words,
        new_words
    )



    old_html = ""

    new_html = ""




    for word in diff:


        code = word[:2]

        value = word[2:]



        if code == "- ":


            old_html += (

                "<span class='removed'>"

                + value

                + "</span> "

            )




        elif code == "+ ":


            new_html += (

                "<span class='added'>"

                + value

                + "</span> "

            )




        elif code == "  ":


            old_html += value + " "

            new_html += value + " "



    return (

        old_html.strip(),

        new_html.strip()

    )
def compare_documents(file1, file2):

    start_time = time.time()

    text1 = read_file(file1)
    text2 = read_file(file2)



    # Similarity Calculation (Fast)

    vectorizer = TfidfVectorizer()



    tfidf = vectorizer.fit_transform(

        [
            text1,
            text2
        ]

    )



    similarity = cosine_similarity(

        tfidf[0:1],

        tfidf[1:2]

    )[0][0]




    similarity = round(

        similarity * 100,

        2

    )







    # Line wise comparison

    lines1 = [

        line.strip()

        for line in text1.split("\n")

        if line.strip()

    ]




    lines2 = [

        line.strip()

        for line in text2.split("\n")

        if line.strip()

    ]







    comparison = []

    differences = 0





    max_length = max(

        len(lines1),

        len(lines2)

    )






    for i in range(max_length):


        line1 = (

            lines1[i]

            if i < len(lines1)

            else ""

        )



        line2 = (

            lines2[i]

            if i < len(lines2)

            else ""

        )







        if line1 == line2:


            status = "Same"


            doc1 = line1

            doc2 = line2




        else:


            status = "Different"


            differences += 1




            doc1, doc2 = highlight_difference(

                line1,

                line2

            )








        comparison.append(
    {
        "line": i + 1,
        "doc1": doc1,
        "doc2": doc2,
        "status": status
    }
)
        
    end_time = time.time()

    return {

    "diff": comparison,

    "similarity": similarity,

    "status": differences,

    "compare_time": round(end_time - start_time, 3),

    "total_lines": max_length,

    "words1": len(text1.split()),

    "words2": len(text2.split()),

    "characters1": len(text1),

    "characters2": len(text2)

}