# 📚 DocuMind AI

### Asistente inteligente de documentación empresarial con RAG, Ollama y PostgreSQL

**DocuMind AI** es un asistente conversacional que permite consultar documentación interna de una empresa mediante lenguaje natural. En lugar de buscar manualmente entre archivos PDF, Markdown y TXT, el usuario formula una pregunta y recibe una respuesta elaborada a partir de los fragmentos recuperados, con referencias a las fuentes utilizadas.

El proyecto se ha desarrollado como práctica del **Máster AI Engineer de ThePower Education** y utiliza **NovaTech Solutions**, una empresa ficticia, como escenario de demostración.

> **Alcance:** prototipo educativo ejecutado localmente. Los documentos incluidos son ficticios; no contiene información empresarial real. No es un sistema de producción ni implementa autenticación, permisos por usuario o aislamiento entre organizaciones.

---

## 📑 Índice

1. [Objetivo del proyecto](#-objetivo-del-proyecto)
2. [Funcionalidades](#-funcionalidades)
3. [Arquitectura y funcionamiento](#-arquitectura-y-funcionamiento)
4. [Tecnologías utilizadas](#-tecnologías-utilizadas)
5. [Estructura del proyecto](#-estructura-del-proyecto)
6. [Requisitos previos](#-requisitos-previos)
7. [Instalación paso a paso](#-instalación-paso-a-paso)
8. [Configuración de PostgreSQL y Ollama](#-configuración-de-postgresql-y-ollama)
9. [Indexación inicial de documentos](#-indexación-inicial-de-documentos)
10. [Ejecutar la aplicación](#-ejecutar-la-aplicación)
11. [Ejemplos de uso](#-ejemplos-de-uso)
12. [Memoria conversacional y fuentes](#-memoria-conversacional-y-fuentes)
13. [Evaluación funcional](#-evaluación-funcional)
14. [Limitaciones y posibles mejoras](#-limitaciones-y-posibles-mejoras)
15. [Solución de problemas frecuentes](#-solución-de-problemas-frecuentes)
16. [Seguridad y buenas prácticas](#-seguridad-y-buenas-prácticas)

---

## 🎯 Objetivo del proyecto

En muchas organizaciones, las políticas internas, los procedimientos y las instrucciones se encuentran repartidos en documentos de distintos formatos. Localizar una respuesta concreta puede requerir abrir varios archivos y revisar su contenido manualmente.

**DocuMind AI** explora cómo aplicar una arquitectura **RAG (Retrieval-Augmented Generation)** para:

- Centralizar las consultas sobre documentación interna.
- Recuperar los fragmentos más relevantes mediante búsqueda semántica.
- Generar respuestas fundamentadas en los documentos disponibles.
- Mostrar las fuentes que respaldan la respuesta.
- Mantener el contexto de una conversación para comprender preguntas de seguimiento.
- Reconocer cuándo la información solicitada no está disponible.

El objetivo no es entrenar un modelo desde cero, sino **combinar un modelo de lenguaje local con una base de datos vectorial y una interfaz de chat**.

## ✨ Funcionalidades

| Funcionalidad | Descripción |
|---|---|
| Consulta en lenguaje natural | Preguntas sobre la documentación de NovaTech Solutions. |
| Recuperación semántica | Búsqueda de fragmentos relevantes mediante embeddings y pgvector. |
| Respuestas basadas en documentos | El modelo recibe los fragmentos recuperados como contexto. |
| Referencias a fuentes | Citas numeradas en la respuesta y listado de archivos de origen; en PDF, también puede indicarse la página. |
| Memoria conversacional | Reformulación de preguntas de seguimiento usando el historial de la sesión. |
| Control de información desconocida | Instrucciones para indicar que no se encuentra la información, en vez de inventarla. |
| Interfaz web | Chat interactivo desarrollado con Streamlit. |
| Nueva conversación | Reinicio del historial y los mensajes visibles desde la interfaz. |
| Modelos locales | Generación de respuestas y embeddings mediante Ollama. |

> Las referencias y la fidelidad de las respuestas dependen del contenido recuperado y del comportamiento del modelo. Las citas se deben verificar en aplicaciones de mayor criticidad.

## 🧠 Arquitectura y funcionamiento

```text
                    DOCUMENTACIÓN DE NOVATECH
                       PDF · Markdown · TXT
                                │
                                ▼
                     Carga de documentos
                                │
                                ▼
                  División en fragmentos (chunks)
                                │
                                ▼
                 Ollama: nomic-embed-text
                      Embeddings de 768 dim.
                                │
                                ▼
                 PostgreSQL (Neon) + pgvector
                       Almacén vectorial
                                ▲
                                │
Usuario ──► Streamlit ──► Reformulación de la consulta
                                │
                                ▼
                      Búsqueda semántica
                         Top 3 fragmentos
                                │
                                ▼
                  Contexto + pregunta original
                                │
                                ▼
                     Ollama: llama3.1:8b
                                │
                                ▼
                   Respuesta + fuentes citadas
                                │
                                ▼
                         Chat Streamlit
```

### Fase A. Preparación e indexación

1. Se leen los archivos incluidos en `documentos/`.
2. Los textos se dividen mediante `RecursiveCharacterTextSplitter`, con fragmentos de **500 caracteres** y un solapamiento de **100 caracteres**.
3. El modelo `nomic-embed-text`, ejecutado con Ollama, convierte los fragmentos en vectores de **768 dimensiones**.
4. Los fragmentos, embeddings y metadatos se almacenan en PostgreSQL mediante `PGVector` y la extensión `pgvector`.
5. La colección utilizada por la aplicación se llama `documind-documentos`.

La indexación se realiza **una vez para una base de datos nueva**, antes de empezar a utilizar el chat.

### Fase B. Consulta y respuesta

1. El usuario escribe una pregunta en Streamlit.
2. Si existe historial, el modelo intenta convertir la pregunta en una consulta independiente. Por ejemplo, «¿Y cuándo puedo pedirlas?» puede reformularse como «¿Cuándo puedo solicitar las vacaciones?».
3. Se recuperan los **3 fragmentos más similares** a la consulta reformulada.
4. Se construye un contexto con fragmentos numerados y su procedencia.
5. `llama3.1:8b` recibe la pregunta original y ese contexto, con instrucciones para responder únicamente con la información disponible.
6. La aplicación presenta la respuesta y las fuentes identificadas.
7. La pregunta y la respuesta se añaden al historial de la sesión.

**Importante:** la búsqueda semántica no garantiza por sí sola que los fragmentos recuperados contengan la respuesta correcta. La calidad del resultado depende tanto de la recuperación como de la generación.

## 🛠️ Tecnologías utilizadas

| Tecnología | Función |
|---|---|
| **Python** | Lógica principal del proyecto. |
| **LangChain** | Carga y fragmentación de documentos, prompts e integración de componentes. |
| **Ollama** | Ejecución local de los modelos de lenguaje y embeddings. |
| **Llama 3.1 (`llama3.1:8b`)** | Generación de respuestas y reformulación de preguntas. |
| **nomic-embed-text** | Creación de embeddings semánticos. |
| **PostgreSQL** | Persistencia de documentos y vectores. |
| **pgvector** | Operaciones de búsqueda vectorial en PostgreSQL. |
| **Neon** | Servicio de PostgreSQL utilizado en el desarrollo. |
| **Streamlit** | Interfaz web conversacional. |
| **PyMuPDF / TextLoader** | Lectura de documentos PDF y de texto. |
| **python-dotenv** | Carga de configuración desde `.env`. |

El proyecto utiliza servicios de base de datos externos si se configura Neon, pero **la inferencia de los modelos se realiza localmente mediante Ollama**.

## 📁 Estructura del proyecto

```text
DocuMind-AI/
│
├── documentos/
│   ├── politica_rrhh.pdf
│   ├── equipos_informaticos.md
│   ├── seguridad_informatica.md
│   └── normativa_interna.txt
│
├── app.py                # Interfaz conversacional con Streamlit
├── main.py               # Motor RAG, recuperación y memoria
├── indexar.py            # Indexación inicial de documentos
├── requirements.txt      # Dependencias de Python
├── .env.example          # Plantilla de configuración
├── .gitignore            # Exclusiones de Git
└── README.md             # Documentación del proyecto
```

Archivos locales que **no deben publicarse**:

```text
.env                     # Credenciales reales de PostgreSQL
.venv/                   # Entorno virtual de Python
__pycache__/             # Archivos temporales de Python
```

### Responsabilidad de los archivos principales

- **`main.py`**: contiene las funciones para cargar y dividir documentos, preparar la base de datos, conectar con el almacén vectorial, recuperar fragmentos, reformular consultas y generar respuestas con referencias.
- **`indexar.py`**: ejecuta el proceso de carga, fragmentación y almacenamiento vectorial para una base de datos inicialmente vacía.
- **`app.py`**: implementa la interfaz, muestra el historial y las fuentes, y gestiona el reinicio de la conversación.
- **`documentos/`**: contiene los archivos ficticios empleados en las pruebas del asistente.

## 💻 Requisitos previos

Antes de comenzar, necesitas:

- **Python** instalado (el proyecto se ha trabajado con un entorno Python 3.10; se recomienda usar una versión compatible con `requirements.txt`).
- **Git**, para clonar el repositorio.
- **Ollama** instalado y en ejecución.
- Una base de datos **PostgreSQL con la extensión `vector` disponible**. Puedes utilizar Neon o una instancia propia compatible.
- Conexión a Internet para instalar las dependencias, descargar los modelos y, si utilizas Neon, acceder a la base de datos.
- Recursos suficientes para ejecutar localmente `llama3.1:8b`; el rendimiento depende del hardware disponible.

## 🚀 Instalación paso a paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/TU_USUARIO/DocuMind-AI.git
cd DocuMind-AI
```

> Sustituye `TU_USUARIO` por el propietario real del repositorio. La URL se actualizará al publicarlo.

### 2. Crear y activar un entorno virtual

**Windows (PowerShell):**

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux / macOS:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Instalar las dependencias

```bash
python -m pip install -r requirements.txt
```

Si aparecen problemas de compatibilidad, comprueba la versión de Python y las versiones de las librerías especificadas en el archivo.

## ⚙️ Configuración de PostgreSQL y Ollama

### 4. Preparar PostgreSQL

1. Crea una base de datos PostgreSQL nueva en [Neon](https://neon.tech/) o utiliza una instancia compatible propia.
2. Obtén la cadena de conexión de la base de datos.
3. Comprueba que tu usuario tenga permisos para crear o utilizar la extensión `vector` y las tablas necesarias.
4. El script de indexación llama a la función de preparación de base de datos antes de guardar los documentos.

**No reutilices las credenciales de otra persona ni incluyas una contraseña real en el repositorio.**

### 5. Configurar las variables de entorno

Copia `.env.example` y renómbralo a `.env`.

**Windows (PowerShell):**

```powershell
Copy-Item .env.example .env
```

**Linux / macOS:**

```bash
cp .env.example .env
```

Edita el nuevo archivo `.env` e introduce tu propia conexión:

```dotenv
DATABASE_URL=postgresql://USUARIO:CONTRASENA@HOST/NOMBRE_BD?sslmode=require
```

Utiliza **la cadena real proporcionada por tu proveedor**, con los parámetros de conexión que correspondan. Si la contraseña contiene caracteres especiales, debe estar correctamente codificada para su uso en una URL.

> La aplicación utiliza internamente una conexión compatible con SQLAlchemy/psycopg para el almacén vectorial. Mantén en `.env` el formato que espera el proyecto y no cambies arbitrariamente el prefijo de la URL.

### 6. Instalar Ollama y descargar los modelos

Instala Ollama desde su [sitio oficial](https://ollama.com/). Asegúrate de que el servicio esté en ejecución.

En una terminal, descarga los modelos necesarios:

```bash
ollama pull llama3.1:8b
ollama pull nomic-embed-text
```

Comprueba que están disponibles:

```bash
ollama list
```

El proyecto está configurado para utilizar exactamente esos nombres de modelo. Si los cambias, tendrás que actualizar también la configuración de `main.py`.

## 🗂️ Indexación inicial de documentos

Con PostgreSQL configurado y Ollama en funcionamiento, ejecuta:

```bash
python indexar.py
```

El script realiza estas operaciones:

1. Prepara la base de datos para almacenar vectores.
2. Carga los documentos de `documentos/`.
3. Divide el contenido en fragmentos.
4. Genera los embeddings mediante Ollama.
5. Almacena los fragmentos y sus metadatos en PostgreSQL.

En el conjunto documental utilizado durante el desarrollo se generaron **25 fragmentos**, aunque esa cantidad puede variar si se modifican los documentos o la configuración del divisor.

> ⚠️ **Ejecuta `indexar.py` solo para la indexación inicial de una base de datos vacía.** La implementación actual no comprueba automáticamente si un fragmento ya existe. Ejecutarlo de nuevo sobre la misma colección puede generar documentos duplicados. Tampoco es necesario volver a indexar cada vez que se abre Streamlit.

Si cambias los documentos y quieres reconstruir el índice, utiliza una base/colección nueva o realiza una limpieza controlada de los datos anteriores antes de reindexar.

## 💬 Ejecutar la aplicación

Una vez terminada la indexación:

```bash
python -m streamlit run app.py
```

Streamlit mostrará una dirección local, normalmente:

**http://localhost:8501**

Abre esa dirección en el navegador. Encontrarás:

- **Barra lateral** con el nombre de DocuMind AI, la documentación disponible y las tecnologías empleadas.
- **Chat principal** para escribir preguntas sobre la documentación.
- **Fuentes citadas**, desplegables cuando la respuesta incluye referencias identificadas.
- **Botón «Nueva conversación»** para borrar el historial visible y la memoria de la sesión.

Para detener la aplicación, utiliza `Ctrl + C` en la terminal donde se ejecuta Streamlit.

### Uso posterior

Después de la primera instalación, el flujo habitual es:

1. Tener PostgreSQL accesible.
2. Iniciar Ollama si no está funcionando.
3. Activar el entorno virtual.
4. Ejecutar `python -m streamlit run app.py`.

**No necesitas ejecutar `indexar.py` en cada inicio.**

## ❓ Ejemplos de uso

La documentación ficticia de NovaTech Solutions cubre recursos humanos, equipos informáticos, seguridad y normativa interna.

**Consultas sobre recursos humanos:**

- «¿Cuántos días de vacaciones tienen los empleados?»
- «¿Cómo se solicitan las vacaciones?»
- «¿Con cuánta antelación debo pedirlas?»

**Consultas sobre equipos y seguridad:**

- «¿Cómo puedo solicitar material informático?»
- «¿Qué normas de seguridad informática debo seguir?»

**Consultas sobre normativa interna:**

- «¿Cómo se reservan las salas de reuniones?»

**Preguntas de seguimiento:**

```text
Usuario: ¿Cuántos días de vacaciones tienen los empleados?
Usuario: ¿Y cuándo puedo solicitarlas?
```

En la segunda pregunta, el sistema intenta interpretar que «las» hace referencia a las vacaciones mencionadas anteriormente.

**Información que no figura en los documentos:**

```text
Usuario: ¿Cuál es mi médico de cabecera?
Asistente: No lo sé. No encuentro esa información en los documentos.
```

Las respuestas reales dependen de los documentos indexados y de los fragmentos recuperados. El asistente no dispone de información personal del usuario salvo la que este escriba en el chat.

## 🧩 Memoria conversacional y fuentes

### Memoria de sesión

El proyecto utiliza mensajes de `HumanMessage` y `AIMessage` para conservar el contexto de la conversación en curso. Este historial ayuda a reformular preguntas incompletas o que incluyen referencias a mensajes anteriores.

- La memoria se mantiene en la sesión activa de Streamlit.
- **Nueva conversación** elimina tanto los mensajes visibles como el historial utilizado para la reformulación.
- No se implementa una base de datos de conversaciones ni un sistema de cuentas.
- La memoria no debe confundirse con los documentos indexados en PostgreSQL: son componentes diferentes.

### Citas y trazabilidad

Los fragmentos recuperados se identifican con números (`[1]`, `[2]`, `[3]`). El modelo recibe instrucciones para citar únicamente los fragmentos que respaldan su respuesta. La aplicación traduce las citas identificadas a nombres de archivo y, cuando corresponde, páginas de PDF.

Esta estrategia mejora la trazabilidad, pero **no constituye una verificación automática de cada afirmación**. En un uso profesional sería recomendable añadir validaciones adicionales de fidelidad y relevancia.

## 🧪 Evaluación funcional

Durante el desarrollo se realizaron pruebas manuales desde el chat para comprobar:

| Área | Qué se verificó |
|---|---|
| Recuperación | Respuestas a preguntas sobre los documentos disponibles. |
| Referencias | Presencia de fuentes relacionadas con la respuesta. |
| Memoria | Interpretación de preguntas de seguimiento. |
| Cambio de tema | Capacidad de responder una pregunta independiente sin arrastrar indebidamente el contexto anterior. |
| Ausencia de información | Respuesta de desconocimiento cuando los documentos no contienen el dato solicitado. |
| Interfaz | Visualización de mensajes, fuentes y reinicio de conversación. |

Se completó una batería manual de **10 consultas** con resultado satisfactorio en el entorno de desarrollo.

**Alcance de la evaluación:** es una validación funcional manual, no un benchmark automatizado. No se han establecido métricas formales de precisión de recuperación, *faithfulness*, latencia ni rendimiento a escala.

## 🔭 Limitaciones y posibles mejoras

Este proyecto es una primera versión funcional y deliberadamente acotada. Algunas mejoras futuras serían:

1. **Indexación idempotente:** evitar duplicados al procesar documentos varias veces.
2. **Actualización documental:** detectar archivos nuevos, modificados o eliminados.
3. **Evaluación automatizada:** incorporar un conjunto de preguntas con respuestas de referencia y métricas de recuperación y fidelidad.
4. **Filtros y umbrales de relevancia:** reducir respuestas basadas en fragmentos poco relacionados.
5. **Gestión de usuarios y permisos:** restringir el acceso a documentos según el perfil autorizado.
6. **Persistencia de conversaciones:** permitir recuperar chats anteriores.
7. **Observabilidad:** medir tiempos, errores, consultas y calidad de las respuestas.
8. **Mejoras de despliegue:** empaquetar servicios y simplificar la instalación en distintos sistemas.

## 🛠️ Solución de problemas frecuentes

### «No se puede conectar a PostgreSQL»

- Comprueba que `DATABASE_URL` existe en `.env`.
- Revisa usuario, contraseña, host, nombre de la base y parámetros SSL.
- Verifica que la base de datos esté disponible y acepte conexiones desde tu red.
- Comprueba que el usuario tenga los permisos necesarios.

### «La extensión vector no existe» o error de pgvector

- Utiliza una instancia de PostgreSQL compatible con `pgvector`.
- Comprueba que la extensión pueda habilitarse con los permisos de tu usuario.
- Revisa los errores de `preparar_base_datos()` antes de continuar.

### «Ollama no responde» o «model not found»

- Comprueba que Ollama esté instalado y ejecutándose.
- Ejecuta `ollama list` para verificar los modelos disponibles.
- Si falta alguno, descárgalo con `ollama pull llama3.1:8b` o `ollama pull nomic-embed-text`.
- Si la respuesta tarda, revisa el consumo de memoria y los recursos del equipo.

### «No encuentra información que sí aparece en un documento»

- Confirma que el documento estaba en `documentos/` cuando se indexó.
- Verifica que la indexación se completó sin errores.
- Ten en cuenta que se recuperan únicamente los tres fragmentos más similares.
- Prueba una pregunta más concreta y revisa si el contenido está dividido entre varios fragmentos.

### «Las respuestas aparecen duplicadas o la búsqueda empeora»

- Comprueba si ejecutaste `indexar.py` más de una vez sobre la misma colección.
- La versión actual no elimina automáticamente duplicados.
- Evita borrar tablas o colecciones sin comprobar primero qué datos contienen.

### «streamlit no se reconoce como comando»

Ejecuta Streamlit mediante el intérprete del entorno virtual:

```bash
python -m streamlit run app.py
```

Si sigue fallando, verifica que instalaste las dependencias con el entorno virtual activado.

## 🔐 Seguridad y buenas prácticas

- **Nunca publiques `.env`** ni credenciales reales de PostgreSQL.
- Utiliza `.env.example` únicamente como plantilla, con valores ficticios.
- Mantén `.venv/` y los archivos temporales fuera de Git.
- Usa una base de datos de prueba o un usuario con permisos limitados cuando sea posible.
- No cargues documentos confidenciales en una instalación sin autenticación y controles de acceso adecuados.
- Ten presente que, aunque los modelos se ejecuten localmente, **los fragmentos y embeddings se envían a PostgreSQL/Neon** cuando se utiliza una base de datos alojada en la nube.
- Revisa las respuestas y las fuentes antes de utilizarlas para decisiones sensibles.

---

### 📌 Sobre el proyecto

**DocuMind AI** demuestra un flujo RAG de extremo a extremo: **ingesta documental → fragmentación → embeddings → almacenamiento vectorial → recuperación semántica → generación contextual → interfaz conversacional**.

Proyecto desarrollado con fines educativos dentro del **Máster AI Engineer de ThePower Education**. El nombre **NovaTech Solutions** y sus documentos se utilizan como caso de estudio ficticio.
