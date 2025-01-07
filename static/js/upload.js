// let selectedFiles = [];

// function openUploadModal(event) {
//     event.preventDefault();
//     document.getElementById('uploadModal').style.display = 'flex';
// }

function openUploadModal(event) {
    event.preventDefault();
    console.log("Opening modal"); // Debug log
    const modal = document.getElementById('uploadModal');
    modal.style.display = 'flex';
    selectedFiles = []; // Reset files when opening modal
    document.getElementById('fileList').innerHTML = ''; // Clear file list
    document.getElementById('uploadButton').style.display = 'none';
}

// Replace the current file input event listener with these functions
let selectedFiles = [];

function handleFileSelect(event) {
    console.log("Files selected:", event.target.files); // Debug log
    const files = Array.from(event.target.files);

    selectedFiles = selectedFiles.concat(files.map(file => ({
        file: file,
        projects: [],
        teams: [],
        categories: []
    })));

    displayFiles();
    document.getElementById('uploadButton').style.display = 'block';
}

function displayFiles() {
    console.log("Displaying files:", selectedFiles); // Debug log
    const fileList = document.getElementById('fileList');

    fileList.innerHTML = '';  // Clear current list

    selectedFiles.forEach((fileData, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        fileItem.innerHTML = `
            <div class="file-header">
                <i class="fas fa-file"></i>
                <span>${fileData.file.name}</span>
                ${fileData.status ? getStatusIcon(fileData.status) : ''}
            </div>
            
            <div class="select-group">
                <label>Projects</label>
                <select onchange="addTag(${index}, 'projects', this.value)">
                    <option value="">Select project</option>
                    {% for project in projects %}
                        <option value="{{ project.name }}">{{ project.name }}</option>
                    {% endfor %}
                </select>
                <div class="tag-container" id="projects-${index}">
                    ${fileData.projects.map(tag => createTag(tag, index, 'projects')).join('')}
                </div>
            </div>

            <div class="select-group">
                <label>Teams</label>
                <select onchange="addTag(${index}, 'teams', this.value)">
                    <option value="">Select team</option>
                    {% for team in teams %}
                        <option value="{{ team.name }}">{{ team.name }}</option>
                    {% endfor %}
                </select>
                <div class="tag-container" id="teams-${index}">
                    ${fileData.teams.map(tag => createTag(tag, index, 'teams')).join('')}
                </div>
            </div>

            <div class="select-group">
                <label>Categories</label>
                <select onchange="addTag(${index}, 'categories', this.value)">
                    <option value="">Select category</option>
                    {% for category in categories %}
                        <option value="{{ category.name }}">{{ category.name }}</option>
                    {% endfor %}
                </select>
                <div class="tag-container" id="categories-${index}">
                    ${fileData.categories.map(tag => createTag(tag, index, 'categories')).join('')}
                </div>
            </div>
        `;

        fileList.appendChild(fileItem);
    });
}

function createTag(tag, fileIndex, type) {
    return `
        <span class="tag">
            ${tag}
            <button onclick="removeTag(${fileIndex}, '${type}', '${tag}')">&times;</button>
        </span>
    `;
}

function addTag(fileIndex, type, value) {
    console.log("Adding tag:", fileIndex, type, value); // Debug log
    if (!value || selectedFiles[fileIndex][type].includes(value)) return;

    selectedFiles[fileIndex][type].push(value);
    displayFiles();
}

function removeTag(fileIndex, type, tag) {
    console.log("Removing tag:", fileIndex, type, tag); // Debug log
    selectedFiles[fileIndex][type] = selectedFiles[fileIndex][type].filter(t => t !== tag);
    displayFiles();
}

document.getElementById('fileInput').addEventListener('change', function (e) {
    const files = Array.from(e.target.files);
    selectedFiles = selectedFiles.concat(files.map(file => ({
        file: file,
        projects: [],
        teams: [],
        categories: []
    })));
    renderFiles();
    document.getElementById('uploadButton').style.display = 'block';
});

function renderFiles() {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = selectedFiles.map((fileData, index) => `
            <div class="file-item">
                <div class="file-header">
                    <i class="fas fa-file"></i>
                    <span>${fileData.file.name}</span>
                    ${fileData.status ? getStatusIcon(fileData.status) : ''}
                </div>

                <div class="select-group">
                    <label>Projects</label>
                    <select onchange="addTag(${index}, 'projects', this.value)">
                        <option value="">Select project</option>
                        {% for project in projects %}
                            <option value="{{ project.name }}">{{ project.name }}</option>
                        {% endfor %}
                    </select>
                    <div class="tag-container">
                        ${fileData.projects.map(tag => createTag(tag, index, 'projects')).join('')}
                    </div>
                </div>

                <div class="select-group">
                    <label>Teams</label>
                    <select onchange="addTag(${index}, 'teams', this.value)">
                        <option value="">Select team</option>
                        {% for team in teams %}
                            <option value="{{ team.name }}">{{ team.name }}</option>
                        {% endfor %}
                    </select>
                    <div class="tag-container">
                        ${fileData.teams.map(tag => createTag(tag, index, 'teams')).join('')}
                    </div>
                </div>

                <div class="select-group">
                    <label>Categories</label>
                    <select onchange="addTag(${index}, 'categories', this.value)">
                        <option value="">Select category</option>
                        {% for category in categories %}
                            <option value="{{ category.name }}">{{ category.name }}</option>
                        {% endfor %}
                    </select>
                    <div class="tag-container">
                        ${fileData.categories.map(tag => createTag(tag, index, 'categories')).join('')}
                    </div>
                </div>
            </div>
        `).join('');
}
//
// function createTag(tag, fileIndex, type) {
//     return `
//             <span class="tag">
//                 ${tag}
//                 <button onclick="removeTag(${fileIndex}, '${type}', '${tag}')">&times;</button>
//             </span>
//         `;
// }

function getStatusIcon(status) {
    const icons = {
        'loading': '<i class="fas fa-clock status-icon"></i>',
        'success': '<i class="fas fa-check status-icon" style="color: green;"></i>',
        'error': '<i class="fas fa-times status-icon" style="color: red;"></i>'
    };
    return icons[status] || '';
}

// function addTag(fileIndex, type, value) {
//     if (!value || selectedFiles[fileIndex][type].includes(value)) return;
//     selectedFiles[fileIndex][type].push(value);
//     renderFiles();
// }
//
// function removeTag(fileIndex, type, tag) {
//     selectedFiles[fileIndex][type] = selectedFiles[fileIndex][type].filter(t => t !== tag);
//     renderFiles();
// }

function showCancelConfirmation() {
    document.getElementById('confirmationOverlay').style.display = 'block';
    document.getElementById('cancelConfirmation').style.display = 'block';
}

function hideCancelConfirmation() {
    document.getElementById('confirmationOverlay').style.display = 'none';
    document.getElementById('cancelConfirmation').style.display = 'none';
}

function showUploadConfirmation() {
    document.getElementById('confirmationOverlay').style.display = 'block';
    document.getElementById('uploadConfirmation').style.display = 'block';
}

function hideUploadConfirmation() {
    document.getElementById('confirmationOverlay').style.display = 'none';
    document.getElementById('uploadConfirmation').style.display = 'none';
}

function confirmUpload() {
    showUploadConfirmation();
}

async function startUpload() {
    hideUploadConfirmation();
    document.getElementById('uploadButton').style.display = 'none';

    for (let i = 0; i < selectedFiles.length; i++) {
        selectedFiles[i].status = 'loading';
        renderFiles();

        const formData = new FormData();
        formData.append('file', selectedFiles[i].file);
        formData.append('projects', JSON.stringify(selectedFiles[i].projects));
        formData.append('teams', JSON.stringify(selectedFiles[i].teams));
        formData.append('categories', JSON.stringify(selectedFiles[i].categories));

        try {
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': '{{ csrf_token }}'
                }
            });

            if (response.ok) {
                selectedFiles[i].status = 'success';
            } else {
                selectedFiles[i].status = 'error';
            }
        } catch (error) {
            selectedFiles[i].status = 'error';
        }

        renderFiles();
    }

    const allCompleted = selectedFiles.every(file =>
        file.status === 'success' || file.status === 'error'
    );

    if (allCompleted) {
        document.getElementById('continueButton').style.display = 'block';
    }
}
