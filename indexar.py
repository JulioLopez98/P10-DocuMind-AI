
from main import (
    cargar_documentos,
    dividir_documentos,
    preparar_base_datos,
    guardar_embeddings
)


# ============================================================
# INDEXACIÓN INICIAL DE DOCUMENTOS
# ============================================================

def indexar_documentos():
    """Prepara la base de datos y almacena los documentos vectorizados."""

    # Activa pgvector en PostgreSQL si todavía no está disponible.
    preparar_base_datos()

    # Lee los documentos PDF, Markdown y TXT.
    documentos = cargar_documentos()

    if not documentos:
        raise ValueError("No se encontraron documentos para indexar.")

    # Divide los documentos en fragmentos con sus metadatos.
    chunks = dividir_documentos(documentos)

    # Genera los embeddings y guarda los chunks en Neon.
    guardar_embeddings(chunks)

    print(f"\nIndexación completada: {len(chunks)} chunks.")


# ============================================================
# EJECUCIÓN PRINCIPAL
# ============================================================

if __name__ == "__main__":
    indexar_documentos()
