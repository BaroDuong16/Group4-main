const dropZone = document.getElementById('drop-zone');
const fileInput = document.getElementById('file-input');
const fileList = document.getElementById('file-list');
let filesArray = [];
const validExtensions = ['.xlsx', '.xls'];

dropZone.addEventListener('click', () => fileInput.click());

dropZone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropZone.classList.add('dragover');
});

dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

dropZone.addEventListener('drop', (e) => {
    e.preventDefault();
    handleFileDrop(e.dataTransfer.files);
});

fileInput.addEventListener('change', () => handleFileDrop(fileInput.files));

function handleFileDrop(files) {
    for (const file of files) {
        const ext = file.name.split('.').pop().toLowerCase();
        if (!validExtensions.includes(`.${ext}`)) {
            alert('Invalid file type! Please upload Excel files only.');
            continue;
        }
        if (!filesArray.some(existing => existing.name === file.name)) {
            filesArray.push(file);
        }
    }
    updateFileList();
}

function updateFileList() {
    fileList.innerHTML = filesArray.map((file, index) => `
        <li>
            ${file.name}
            <button class="remove-button" onclick="removeFile(${index})">×</button>
        </li>
    `).join('');
    updateFileInput();
}

function removeFile(index) {
    filesArray.splice(index, 1);
    updateFileList();
}

function updateFileInput() {
    const dataTransfer = new DataTransfer();
    filesArray.forEach(file => dataTransfer.items.add(file));
    fileInput.files = dataTransfer.files;
}
