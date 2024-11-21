const uploadForm = document.getElementById('upload-form');
const fileList = document.getElementById('file-list');
const fileNameSelect = document.getElementById('file-name');

uploadForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const formData = new FormData(uploadForm);
    const response = await fetch('/upload', {
        method: 'POST',
        body: formData
    });

    const data = await response.json();
    alert(data.message);
    fetchFiles(); // Actualiza la lista de archivos después de cargar uno nuevo
});

// Mostrar archivos cargados
async function fetchFiles() {
    const response = await fetch('/files');
    const files = await response.json();

    fileList.innerHTML = '';
    fileNameSelect.innerHTML = '<option value="" disabled selected>Selecciona un archivo</option>';
    files.forEach(file => {
        const li = document.createElement('li');
        li.textContent = file;
        fileList.appendChild(li);

        const option = document.createElement('option');
        option.value = file;
        option.textContent = file;
        fileNameSelect.appendChild(option);
    });
}

// Realizar pregunta sobre el archivo
const askForm = document.getElementById('ask-form');
askForm.addEventListener('submit', async (event) => {
    event.preventDefault();

    const fileName = document.getElementById('file-name').value;
    const query = document.getElementById('query-input').value;

    const response = await fetch('/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ file_name: fileName, query })
    });

    const data = await response.json();
    alert(data.response);
});

// Inicializar la lista de archivos
fetchFiles();