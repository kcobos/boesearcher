# BOEsearcher
<!-- .slide: data-background="img/main.jpg" data-background-position="top" data-background-opacity="0.6" -->
Carlos Cobos



## ¿Qué he usado?
<!-- .slide: data-background="img/main.jpg" data-background-position="top" data-background-opacity="0.6" -->

* Lucene 8.1.1 <!-- .element: class="fragment" data-fragment-index="1" -->
* Python 3.8 <!-- .element: class="fragment" data-fragment-index="2" -->
* Docker <!-- .element: class="fragment" data-fragment-index="3" -->
* Request <!-- .element: class="fragment" data-fragment-index="4" -->
* Beautiful Soup <!-- .element: class="fragment" data-fragment-index="5" -->
* Flask <!-- .element: class="fragment" data-fragment-index="6" -->



## ¿Qué documentos?
<!-- .slide: data-background="img/get.jpg" data-background-position="top" data-background-opacity="0.6" -->
# BOE <!-- .element: class="fragment" data-fragment-index="1" -->


### Obtención automática de datos
<!-- .slide: data-background="img/summary.jpg" data-background-position="top" data-background-opacity="0.6" -->
```python
while fecha_inicio <= fecha_fin:
    direccion = "https://boe.es/diario_boe/xml.php?id=BOE-S-" + fecha_inicio.strftime("%Y%m%d")
    r = requests.get(direccion)
    bs = BeautifulSoup(r.text, "lxml")
    if bs.error is None:
        xmls = bs.find_all("urlxml")
        for x in xmls:
            ra = requests.get("https://boe.es/"+x.text)
            bsa = BeautifulSoup(ra.text, "lxml")
            identificador = bsa.documento.metadatos.identificador.text
            open("./documentos/"+identificador+".xml","w").write(ra.text)
    fecha_inicio = fecha_inicio + timedelta(days=1)
```



## Creación del índice
<!-- .slide: data-background="img/index.jpg" data-background-position="top" data-background-opacity="0.6" -->
```python
directory = SimpleFSDirectory(Paths.get("./lucene/index"))
analyzer = SpanishAnalyzer()
analyzer = LimitTokenCountAnalyzer(analyzer, 10000)
config = IndexWriterConfig(analyzer)
writer = IndexWriter(directory, config)

for dn in os.listdir("./documentos"):
    d = open("./documentos/"+dn, "r")
    bs = BeautifulSoup(d, "lxml")
    doc = Document()
    doc.add(Field("titulo", bs.documento.metadatos.titulo.text))
    doc.add(Field("pdf", bs.documento.metadatos.url_pdf.text))
    doc.add(Field("texto", bs.documento.texto.text))
    writer.addDocument(doc)
writer.commit()
writer.close()
```


## Búsqueda
<!-- .slide: data-background="img/search.jpg" data-background-position="top" data-background-opacity="0.6" -->
```python
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
```



## ¿Por qué docker?
<!-- .slide: data-background="img/docker.png" data-background-position="top" data-background-opacity="0.6" -->



# Ejemplo de uso
<!-- .slide: data-background="img/no_index.jpg" data-background-position="top" data-background-opacity="0.6" -->