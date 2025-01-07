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

let folderStructure = {
    'Project Root': {
        type: 'folder',
        children: {}
    }
};

function createFolder(path) {
    let current = folderStructure;
    const parts = path.split('/').filter(p => p);
    let currentPath = '';

    for (const part of parts) {
        currentPath = currentPath ? `${currentPath}/${part}` : part;
        let pointer = current['Project Root'];
        const pathParts = currentPath.split('/');

        for (let i = 0; i < pathParts.length - 1; i++) {
            pointer = pointer.children[pathParts[i]];
        }

        if (!pointer.children[part]) {
            pointer.children[part] = {
                type: 'folder',
                children: {}
            };
        }
    }
    console.log('Updated folder structure:', JSON.stringify(folderStructure, null, 2));
}

function handleFileSelect(event) {
    console.log("Files selected:", event.target.files); // Debug log
    const files = Array.from(event.target.files);

    selectedFiles = selectedFiles.concat(files.map(file => ({
        file: file,
        projects: [],
        location: 'Project Root', // Default location
        teams: [],
        categories: [],
        id: Math.random().toString(36).substr(2, 9) // Unique ID for each file

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
                <button onclick="removeFile('${fileData.id}')" class="remove-file-btn">
                    <i class="fas fa-trash"></i>
                </button>
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
                <label>Location</label>
                <div class="folder-tree">
                    ${generateFolderTree(folderStructure['Project Root'], '', index)}
                </div>
                <div class="location-controls">
                    <button onclick="showNewFolderDialog(${index})" class="btn btn-secondary">
                        <i class="fas fa-folder-plus"></i> New Folder Here
                    </button>
                </div>
                <div class="location-display">
                    <i class="fas fa-folder"></i>
                    <span>${fileData.location}</span>
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

function generateFolderTree(folder, path, fileIndex) {
    let tree = `
        <div class="folder-item ${path === '' ? 'active' : ''}" 
             onclick="updateLocation(${fileIndex}, '${path || 'Project Root'}')">
            <i class="fas ${path === '' ? 'fa-folder-open' : 'fa-folder'}"></i>
            <span>${path === '' ? 'Project Root' : path.split('/').pop()}</span>
        </div>
    `;

    const sortedFolders = Object.entries(folder.children).sort(([a], [b]) => a.localeCompare(b));

    if (sortedFolders.length > 0) {
        tree += '<div class="subfolder-container">';
        for (const [name, content] of sortedFolders) {
            const newPath = path ? `${path}/${name}` : name;
            if (content.type === 'folder') {
                tree += generateFolderTree(content, newPath, fileIndex);
            }
        }
        tree += '</div>';
    }

    return tree;
}

function generateFolderOptions(folder, path, indent = '') {
    let options = '';
    for (const [name, content] of Object.entries(folder.children)) {
        const fullPath = path ? `${path}/${name}` : name;
        options += `<option value="${fullPath}">${indent}${name}</option>`;
        if (content.type === 'folder') {
            options += generateFolderOptions(content, fullPath, indent + '└─ ');
        }
    }
    return options;
}


function showNewFolderDialog(fileIndex) {
    const folderName = prompt('Enter new folder name:');
    if (folderName && folderName.trim()) {
        const currentLocation = selectedFiles[fileIndex].location;
        const newPath = currentLocation === 'Project Root'
            ? folderName
            : `${currentLocation}/${folderName}`;

        createFolder(newPath);
        selectedFiles[fileIndex].location = newPath;
        displayFiles();
    }
}

function updateLocation(fileIndex, newLocation) {
    selectedFiles[fileIndex].location = newLocation;
    displayFiles();
}

function removeFile(fileId) {
    selectedFiles = selectedFiles.filter(file => file.id !== fileId);
    if (selectedFiles.length === 0) {
        document.getElementById('uploadButton').style.display = 'none';
    }
    displayFiles();
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
        formData.append('location', selectedFiles[i].location);
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
