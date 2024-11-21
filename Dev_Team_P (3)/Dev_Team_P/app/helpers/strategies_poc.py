import abc
from abc import abstractmethod
from typing import Type
import re
import PyPDF2
import docx
from typing import Optional

class FileManager(abc.ABC):
    @abstractmethod
    def __init__(self, path):
        self.path = path

    #Metodo abstracto para leer el contenido de un archivo
    @abstractmethod
    def read(self):
        pass

# Limpia el texto eliminando saltos de línea innecesarios y espacios redundantes
def clean_text(text: str) -> str:
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)  # Reemplaza saltos de línea simples por un espacio
    text = re.sub(r'\n+', '\n', text)  # Reemplaza múltiples saltos de línea consecutivos por uno solo
    text = re.sub(r'[ \t]+', ' ', text)  # Quita múltiples espacios y tabulaciones
    return text

class PDFFileManager(FileManager):
    def __init__(self, path):
        super().__init__(path)

    # Lee el contenido de un archivo PDF y lo devuelve como texto limpio
    def read(self) -> Optional[str]:
        try:
            with open(self.path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ''
                for page in range(len(reader.pages)):
                    text += reader.pages[page].extract_text()

                cleaned_text = clean_text(text)  # Limpia el texto extraído
                return cleaned_text

        except FileNotFoundError:
            return f"File not found: {self.path}"
        except Exception as e:
            return f"An error occurred while reading the PDF: {e}"

class WordFileManager(FileManager):
    def __init__(self, path):
        super().__init__(path)

    # Lee el contenido de un archivo de Word y devuelve el texto
    def read(self) -> Optional[str]:
        try:
            doc = docx.Document(self.path)
            text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
            return text
        except FileNotFoundError:
            return f"File not found: {self.path}"
        except Exception as e:
            return f"An error occurred while reading the Word file: {e}"

class TextFileManager(FileManager):
    def __init__(self, path):
        super().__init__(path)

    # Lee el contenido de un archivo de texto plano
    def read(self):
        try:
            with open(self.path, 'r', encoding='utf-8') as file:
                return file.read()
        except FileNotFoundError:
            return f"File not found: {self.path}"
        except Exception as e:
            return f"An error occurred while reading the text file: {e}"

# Estrategias disponibles para manejar diferentes tipos de archivos
strategies: dict[str, Type[FileManager]] = {
    "pdf": PDFFileManager,
    "docx": WordFileManager,
    "txt": TextFileManager
}

class FileReader:
    def __init__(self, path: str):
        # Determina la extensión del archivo y selecciona la estrategia apropiada
        extension = path.split('.')[-1]
        if extension not in strategies:
            raise ValueError(f"Unsupported file type: {extension}")
        self.manager = strategies[extension](path)

    # Llama al metodo 'read' de la clase correspondiente para leer el archivo
    def read_file(self):
        return self.manager.read()



