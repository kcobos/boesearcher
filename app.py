import requests 
from bs4 import BeautifulSoup
import os
from datetime import datetime, timedelta

import lucene
from java.nio.file import Paths
from org.apache.lucene.analysis.miscellaneous import LimitTokenCountAnalyzer
from org.apache.lucene.analysis.es import SpanishAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.document import Document, Field, StringField, TextField
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher


from flask import Flask, request, render_template

app = Flask(__name__)
lucene.initVM(vmargs=['-Djava.awt.headless=true'])

direccion_base = "https://boe.es"

@app.route("/")
def main():
    resultados = []
    indice_vacio = False
    if len(os.listdir("./lucene/index")) == 0:
        indice_vacio = True
    else:
        consulta = request.args.get("consulta", None)
        if consulta is not None:
            directory = SimpleFSDirectory(Paths.get("./lucene/index"))
            searcher = IndexSearcher(DirectoryReader.open(directory))
            analyzer = SpanishAnalyzer()
            query = QueryParser("texto", analyzer).parse(consulta)
            scoreDocs = searcher.search(query, 10).scoreDocs

            for sd in scoreDocs:
                doc = searcher.doc(sd.doc)
                resultados.append({
                    "url": direccion_base + doc.get("pdf"),
                    "titulo": doc.get("titulo")
                })


    return render_template("main.html", lucene=lucene.VERSION, indice_vacio=indice_vacio, resultados=resultados)

@app.route("/obtener")
def obtener():
    return render_template("obtener.html")

@app.route("/get")
def colectar():
    fecha_inicio = request.args.get("fecha_inicio", None)
    fecha_fin = request.args.get("fecha_fin", None)

    for root, dirs, files in os.walk("./documentos"):
        for file in files:
            os.remove(os.path.join(root, file))

    fecha_inicio = datetime.strptime(fecha_inicio, "%d-%m-%Y") if fecha_inicio is not None else datetime.today()
    fecha_fin = datetime.strptime(fecha_fin, "%d-%m-%Y") if fecha_fin is not None else datetime.today()

    data = []
    boletines = 0
    while fecha_inicio <= fecha_fin:
        direccion = direccion_base + "/diario_boe/xml.php?id=BOE-S-"+fecha_inicio.strftime("%Y%m%d")
        print(direccion)
        r = requests.get(direccion)
        if r.status_code != 400:
            bs = BeautifulSoup(r.text, "lxml")
            if bs.error is None:
                xmls = bs.find_all("urlxml")
                for x in xmls:
                    ra = requests.get(direccion_base+x.text)
                    if ra.status_code != 400:
                        bsa = BeautifulSoup(ra.text, "lxml")
                        identificador = bsa.documento.metadatos.identificador.text
                        data.append(identificador)
                        boletines += 1
                        print(boletines)
                        open("./documentos/"+identificador+".xml","w").write(ra.text)
        fecha_inicio = fecha_inicio + timedelta(days=1)
    
    return render_template("colectados.html", lucene=lucene.VERSION, data=data, boletines=boletines)

@app.route("/indexar")
def indexar():
    directory = SimpleFSDirectory(Paths.get("./lucene/index"))
    analyzer = SpanishAnalyzer()
    analyzer = LimitTokenCountAnalyzer(analyzer, 10000)
    config = IndexWriterConfig(analyzer)
    writer = IndexWriter(directory, config)

    doc_names = os.listdir("./documentos")
    indexados = 0
    for dn in doc_names:
        d = open("./documentos/"+dn, "r")
        bs = BeautifulSoup(d, "lxml")
        d.close()
        doc = Document()
        doc.add(
            Field("id", bs.documento.metadatos.identificador.text, StringField.TYPE_STORED)
        )
        doc.add(
            Field("titulo", bs.documento.metadatos.titulo.text, StringField.TYPE_STORED)
        )
        doc.add(
            Field("pdf", bs.documento.metadatos.url_pdf.text, StringField.TYPE_STORED)
        )
        doc.add(
            Field("texto", bs.documento.texto.text, TextField.TYPE_STORED)
        )
        writer.addDocument(doc)
        indexados += 1
    writer.commit()
    writer.close()
    
    return render_template("indexados.html", lucene=lucene.VERSION, indexados=indexados)

# @app.route("/slides")
# def slides():
#     return render_template("slides/index.html")