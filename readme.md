# Introducción
En esta práctica se ha creado un servicio de búsqueda de boletines dentro del BOE. Para ello, se ha empleado [PyLucene](https://lucene.apache.org/pylucene/index.html) que es un wrapper de la biblioteca Lucen, creada en Java, para hacer uso de la misma desde Python.

# Colección de datos
La Agencia Estatal Boletín Oficial del Estado tiene a disposición de los usuarios dos tipos de documentos de todos los boletines: [uno en PDF](https://boe.es/boe/dias/2020/03/02/pdfs/BOE-A-2020-2947.pdf) para visualizar correctamente el contenido haciéndolo usable por la mayoría de usuarios y [otro en XML](https://boe.es/diario_boe/xml.php?id=BOE-A-2020-2947) para poder hacer procesos automáticos. Este último tipo de fichero es necesario para tener una plataforma de [Datos abiertos](https://www.boe.es/datosabiertos/) y es en el que se basa esta práctica.

El servicio creado no necesita tener documentos (los boletines en XML) previamente descargados sino que, a través de la interfaz, se pueden descargar los documentos de forma automática para, posteriormente, indexarlos en el buscador. Para descargar los documentos entre unas fechas indicadas se accede al [sumario](https://www.boe.es/datosabiertos/documentos/SumariosBOE_v_1_0.pdf) de cada uno de los días comprendidos entre las fechas, para buscar en él todos los documentos y poderlos descargar.

Estos documentos del BOE tiene multitud de metadatos y datos asociados. En esta práctica sólamente se ha hecho uso de:

* Identificador: para enlazar con el documento original.
* Título: para mostrar el documento en la lista de documentos recuperados.
* Texto: este es el contenido que se va a indexar.

# Servicio BOE Searcher
Se ha creado un contenedor para incluir todas las liberías que necesita el servicio así como para aislarlo para su buen funcionamiento. Se ha empleado Flask como framework para la creación del servicio haciendo que su interfaz sea web.

Para [instalar PyLucene](https://lucene.apache.org/pylucene/install.html) hay que instalar un JDK y la librería Ant de Apache, además de Python y las librerías que se han necesitado como flask, gunicorn (servidor de la aplicación), requests (para descargar los documentos) y bs4 (para extraer datos de los documentos XML). Estos requisitos, así como el proceso de instalación está automatizado en la creación de la imagen para el contenedor.

Entrando en materia, la [aplicación](./app.py) se constituye de tres funciones importantes:

* *main*: es la vista principal de la aplicación. En ella se comprueba si existe un índice creado para la búsqueda y realiza la misma.
* *colectar*: dicha función realiza la descarga automática de documentos (boletines) comprendidos entre las fechas que se han seleccionado.
* *indexar*: en esta función se crea el índice de Lucene para poder realizar la búsqueda. 

En lo concerniente a Lucene, se usa el analizador de español debido a que los documentos están es este idioma. Este analizador ya realiza la eliminación de palabras vacías y la lematización del diccionario español. 

Al ser esta una colección de documentos con un vocabulario general no procede a realizar una eliminación de palabras concretas como puede pasar en otros ámbitos. Es por este motivo que se deja al analizador con los parámetros por defecto.


# Manual de usuario
Para poder hacer uso de este servicio hay que tener docker o podman instalado. De esta forma es posible la ejecución del contenedor.

La configuración del contenedor se encuentra en el archivo [docker-compose.yml](./docker-compose.yml). En él se puede encontrar el puerto al que se debe conectar, a través de un navegador, para hacer uso del servicio. Además se encuentran los volúmenes que se usan como el volumen para guardar los documentos o el índice de Lucene.

Para levantar el servicio, en este directorio basta con usar `docker-compose up`. Esto crea la imagen y el contenedor con los volúmenes añadidos y la publicación del puerto para acceder al contenedor.

Con el servicio activo, se puede acceder a la dirección [http://localhost:5000/](http://localhost:5000/) donde se podrá ver la página principal de la aplicación que es una página de búsqueda pero, al no haber un índice creado se muestra un mensaje advirtiendo de ello.

Para generar el índice, primero hay que descargar los documentos. Para ello, en la aplicación hay una sección llamada *Obtener datos* donde se le tiene que especificar las fechas donde se quiere obtener los distintos boletines. Al darle al botón *Obtener documentos* una vez seleccionadas las fechas, el servicio buscará y descargará los boletines. Este proceso requiere que el usuario espere a la aplicación durante un tiempo prudencial elevado. En los logs del servicio se puede ver el proceso de captación de los datos (número de documentos obtenidos).

Una vez que se han obtenido los documentos, el siguiente paso es generar el índice. Para ello la aplicación dispone de una sección llamada *Crear índices* donde se indexarán los archivos anteriormente descargados.

Por último, desde la página principal de la aplicación se pueden generar las búsquedas en los documentos.