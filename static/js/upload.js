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
    root: {
        name: 'Project Root',
        type: 'folder',
        children: {}
    }
};

function createFolder(path) {
    let current = folderStructure.root;
    const parts = path.split('/').filter(p => p);
    let currentPath = '';

    for (const part of parts) {
        if (part === current.name) continue; // Skip if it's the root name

        currentPath = currentPath ? `${currentPath}/${part}` : part;

        if (!current.children[part]) {
            current.children[part] = {
                name: part,
                type: 'folder',
                children: {}
            };
        }
        current = current.children[part];
    }
    console.log('Updated folder structure:', JSON.stringify(folderStructure, null, 2));
}


function handleFileSelect(event) {
    console.log("Files selected:", event.target.files);
    const files = Array.from(event.target.files);

    selectedFiles = selectedFiles.concat(files.map(file => ({
        file: file,
        fileName: file.name,
        projects: [],
        teams: [],
        categories: [],
        location: folderStructure.root.name, // Use current root name
        id: Math.random().toString(36).substr(2, 9)
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

        const rootName = fileData.projects.length > 0 ? fileData.projects[0] : 'Project Root';


        fileItem.innerHTML = `
            <div class="file-header">
                <i class="fas fa-file"></i>
                <div class="file-name-input">
                    <input type="text" 
                           value="${fileData.fileName}"
                           onchange="updateFileName(${index}, this.value)"
                           class="file-name-field"
                           title="Original filename: ${fileData.file.name}">
                </div>
                <button onclick="removeFile('${fileData.id}')" class="remove-file-btn">
                    <i class="fas fa-trash"></i>
                </button>
                ${fileData.status ? getStatusIcon(fileData.status) : ''}
            </div>
            
            <div class="select-group">
                <label>Projects</label>
<!--                <select onchange="updateFileProject(${index}, this.value)">-->
                    <select>
                    <option value="">Select project</option>
                    {% for project in projects %}
                        <option value="{{ project.name }}" ${fileData.projects.includes("{{ project.name }}") ? 'selected' : ''}>
                            {{ project.name }}
                        </option>
                    {% endfor %}
                </select>                
            </div>
            
            <div class="select-group">
                <label>Location</label>
                <div class="folder-tree">
                    ${generateFolderTree(folderStructure.root, '', index)}
                </div>
                <div class="location-controls">
                    <button onclick="showNewFolderDialog(${index})" class="btn btn-secondary">
                        <i class="fas fa-folder-plus"></i> New Folder Here
                    </button>
                </div>
                <div class="location-display">
                    <span class="location-label">Selected location:</span>
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
             onclick="updateLocation(${fileIndex}, '${path || folder.name}')">
            <i class="fas ${path === '' ? 'fa-folder-open' : 'fa-folder'}"></i>
            <span>${path === '' ? folder.name : path.split('/').pop()}</span>
            ${path !== '' ? `
                <button onclick="deleteFolder('${path}', ${fileIndex})" class="delete-folder-btn" title="Delete folder">
                    <i class="fas fa-trash"></i>
                </button>
            ` : ''}
        </div>
    `;

    const sortedFolders = Object.entries(folder.children).sort(([a], [b]) => a.localeCompare(b));

    if (sortedFolders.length > 0) {
        tree += '<div class="subfolder-container">';
        for (const [name, content] of sortedFolders) {
            const newPath = path ? `${path}/${name}` : name;
            tree += generateFolderTree(content, newPath, fileIndex);
        }
        tree += '</div>';
    }

    return tree;
}

function updateFileName(fileIndex, newName) {
    selectedFiles[fileIndex].fileName = newName;
}

function updateFileProject(fileIndex, projectName) {
    const oldProject = selectedFiles[fileIndex].projects[0];

    if (projectName) {
        selectedFiles[fileIndex].projects = [projectName];
        // Update root folder name
        folderStructure.root.name = projectName;

        // Update locations for all files that were in the old root
        selectedFiles.forEach(file => {
            if (file.location === oldProject || file.location === 'Project Root') {
                file.location = projectName;
            } else if (oldProject && file.location.startsWith(oldProject + '/')) {
                // Update paths that started with the old project name
                file.location = projectName + file.location.substring(oldProject.length);
            }
        });
    } else {
        selectedFiles[fileIndex].projects = [];
        // Reset root folder name
        folderStructure.root.name = 'Project Root';

        // Update locations for all files that were in the project
        selectedFiles.forEach(file => {
            if (file.location === oldProject) {
                file.location = 'Project Root';
            }
        });
    }

    displayFiles();
}

function deleteFolder(path, fileIndex) {
    event.stopPropagation(); // Prevent folder selection when clicking delete

    // Check if folder is empty
    const folder = getFolderByPath(path);
    if (folder && Object.keys(folder.children).length === 0) {
        // Check if any files are using this location
        const filesInFolder = selectedFiles.some(file =>
            file.location === path || file.location.startsWith(path + '/'));

        if (!filesInFolder) {
            deleteFolderFromStructure(path);
            displayFiles();
        } else {
            alert('Cannot delete folder: it contains files');
        }
    } else {
        alert('Cannot delete folder: it contains subfolders');
    }
}

function getFolderByPath(path) {

    let current = folderStructure.root;
    console.log(current)
    const parts = path.split('/');

    for (const part of parts) {
        if (!current.children[part]) return null;
        current = current.children[part];
    }
    return current;
}

function deleteFolderFromStructure(path) {
    const parts = path.split('/');
    const folderName = parts.pop();
    let current = folderStructure.root;

    for (const part of parts) {
        current = current.children[part];
    }

    delete current.children[folderName];
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
