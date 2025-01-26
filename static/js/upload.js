async function fetchUserProjects() {
    try {
        const response = await fetch('/api/user_projects/', {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch projects');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching projects:', error);
        return [];
    }
}

async function updateFileTeams(fileIndex, projectName) {
    try {
        const response = await fetch(`/api/user_teams/${projectName}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });

        const teams = await response.json();

        const teamSelect = document.querySelector(`select[id="teams-${fileIndex}"]`);

        if (!teamSelect) {
            console.error('Select element not found');
            return;
        }

        teamSelect.innerHTML = '<option value="">Select team</option>';

        teams.teams.forEach(team => {
            const option = document.createElement('option');
            option.value = team.name;
            option.text = team.name;
            teamSelect.appendChild(option);
        });

    } catch (error) {
        console.error('Error:', error);
    }
}

async function updateFileCategory(fileIndex) {
    try {
        const response = await fetch(`/api/categories/`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });

        const categories = await response.json();
        console.log('categories', categories)

        const categorySelect = document.querySelector(`select[id="categories-${fileIndex}"]`);

        if (!categorySelect) {
            console.error('Select element not found');
            return;
        }

        categorySelect.innerHTML = '<option value="">Select category</option>';

        categories.categories.forEach(cateogry => {
            const option = document.createElement('option');
            option.value = cateogry.label;
            option.text = cateogry.label;
            categorySelect.appendChild(option);
        });

    } catch (error) {
        console.error('Error:', error);
    }
}

function openUploadModal(event) {
    event.preventDefault();
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
        children: {},
        isEmpty: true
    }
};

async function fetchProjectFolders(projectName) {
    try {
        const response = await fetch(`/api/project_folders/${projectName || ''}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch folders');
        }

        const folders = await response.json();
        return folders;
    } catch (error) {
        console.error('Error fetching folders:', error);
        return [];
    }
}

// Function to merge backend folders with current structure
function mergeFolderStructures(existingFolders, fileStructure) {
    existingFolders.forEach(folder => {
        const pathParts = folder.path.split('/').filter(p => p);
        let current = fileStructure.root;
        let currentPath = '';

        pathParts.forEach(part => {
            currentPath = currentPath ? `${currentPath}/${part}` : part;
            if (!current.children[part]) {
                current.children[part] = {
                    name: part,
                    type: 'folder',
                    children: {},
                    isEmpty: folder.is_empty,
                    isExisting: true // Flag to identify folders from backend
                };
            }
            current = current.children[part];
        });
    });
}

function createFolder(path, fileIndex) {

    const fileData = selectedFiles[fileIndex];

    const pathParts = path.split('/');
    let currentFolder = fileData.folderStructure.root;
    // Navegar a la ubicación deseada
    for (const part of pathParts) {
        if (!currentFolder.children[part]) {
            // no existe la carpeta
            if (currentFolder.name === part) {
                continue
            } else {
                currentFolder.children[part] = {
                    name: part,
                    type: 'folder',
                    children: {},
                    isEmpty: true
                }; // Crear nueva carpeta si no existe
            }

        }
        currentFolder = currentFolder.children[part];
    }

    // Aquí puedes llamar a displayFiles() o renderizar la estructura actualizada
    displayFiles();
}


function handleFileSelect(event) {
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

async function displayFiles() {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';

    // Fetch user's projects
    const userProjects = await fetchUserProjects();
    // const userTeams = await fetchUserTeams();

    selectedFiles.forEach((fileData, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const currentProject = fileData.projects[0] || 'Project Root';

        if (currentProject === 'Project Root') {
            fileData.location = 'Project Root'
        }

        // Create project options HTML
        const projectOptions = userProjects['projects'].map(project =>
            `<option value="${project.name}" ${fileData.projects.includes(project.name) ? 'selected' : ''}>
                ${project.name}
            </option>`
        ).join('');

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
                <div class="status-container" ${!fileData.status ? 'style="display: none;"' : ''}>
                    <span class="status-label">Status:</span>
                    ${getStatusIcon(fileData.status)}
                </div>
                <button onclick="removeFile('${fileData.id}')" class="remove-file-btn">
                    <i class="fas fa-trash"></i>
                </button>
            </div>
            
            <div class="select-group">
                <label>Project</label>
                <select onchange="updateFileProject(${index}, this.value)">
                    <option value="">Select project</option>
                    ${projectOptions}
                </select>                
            </div>
            
            <div class="select-group">
                <label>Location</label>
                <div class="folder-tree">
                   ${generateFolderTree(fileData, '', index)}
                    
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
                <select id="teams-${index}" onchange="addTag(${index}, 'teams', this.value)">
                    <option value="">Select team</option>
                </select>
                <div class="tag-container" id="teams-${index}">
                    ${fileData.teams.map(tag => createTag(tag, index, 'teams')).join('')}
                </div>
            </div>

            <div class="select-group">
                <label>Categories</label>
                <select id="categories-${index}" onchange="addTag(${index}, 'categories', this.value)">
                    <option value="">Select category</option>
                    
                </select>
                <div class="tag-container" id="categories-${index}">
                    ${fileData.categories.map(tag => createTag(tag, index, 'categories')).join('')}
                </div>
            </div>
        `;
        fileList.appendChild(fileItem);

        if(currentProject !== 'Project Root') {
            updateFileTeams(index, currentProject)
            updateFileCategory(index)
        }


    });
}

// function generateFolderTree(folder, path, fileIndex, currentProject) {

function generateFolderTree(fileData, path, fileIndex) {

     if (!fileData.folderStructure) {
        fileData.folderStructure = {
            root: {
                name: 'Project Root',
                type: 'folder',
                children: {},
                isEmpty: true
            }
        };
    }

    const folder = fileData.folderStructure.root;
    const currentProject = fileData.projects[0] || 'Project Root';

    let tree = '';
    // Para la carpeta raíz
    if (path === '') {
        const rootName = currentProject === 'Project Root' ? 'Project Root' : currentProject;

        tree = `
            <div class="folder-item active" onclick="updateLocation(${fileIndex}, '${rootName}')">
                <i class="fas fa-folder-open"></i>
                <span>${rootName}</span>
            </div>
        `;
    } else {
        // Para las subcarpetas
        const folderName = path.split('/').pop();

        if (folderName !== currentProject) {
            tree = `
                <div class="folder-item" onclick="updateLocation(${fileIndex}, '${path}')">
                    <i class="fas fa-folder"></i>
                    <span>${folderName}</span>
                    ${folder.children[folderName]?.isEmpty ? `
                        <button onclick="deleteFolder('${path}', ${fileIndex})" 
                                class="delete-folder-btn" 
                                title="Delete folder">
                            <i class="fas fa-trash"></i>
                        </button>
                    ` : ''}
                </div>
            `;
        }
    }

    if (currentProject === 'Project Root') {
        return tree
    }
    // Subcarpetas
    if (folder && folder.children) {
        const subfolders = Object.entries(folder.children)
            .filter(([name]) => name !== currentProject) // Excluir el proyecto actual del árbol
            .sort(([a], [b]) => a.localeCompare(b)); // Ordenar alfabéticamente

        if (subfolders.length > 0) {
            tree += '<div class="subfolder-container">';
            for (const [name, folderContent] of subfolders) {
                const newPath = path ? `${path}/${name}` : name;
                // tree += generateFolderTree(content, newPath, fileIndex, currentProject);
                tree += generateFolderTree(
                    {
                        ...fileData,
                        folderStructure: {
                            root: folderContent
                        }
                    },
                    newPath,
                    fileIndex
                );

            }
            tree += '</div>';
        }
    }

    return tree;
}

function updateFileName(fileIndex, newName) {
    selectedFiles[fileIndex].fileName = newName;
}

async function updateFileProject(fileIndex, projectName) {
    const fileData = selectedFiles[fileIndex];
    const oldProject = fileData.projects[0];

    if (projectName) {
        // Update this file's project
        fileData.projects = [projectName];

        const existingFolders = await fetchProjectFolders(projectName);
        // folderStructure = {
        //     root: {
        //         name: projectName,
        //         type: 'folder',
        //         children: {},
        //         isEmpty: true
        //     }
        // };

        fileData.folderStructure = {
            root: {
                name: projectName,
                type: 'folder',
                children: {},
                isEmpty: true
            }
        };

        mergeFolderStructures(existingFolders, fileData.folderStructure);


        // Update location to new project root
        if (fileData.location === 'Project Root' || fileData.location === oldProject) {
            fileData.location = projectName;
        } else if (oldProject && fileData.location.startsWith(oldProject + '/')) {
            // Update paths for files in subfolders
            fileData.location = projectName + fileData.location.substring(oldProject.length);
        }


        // if (oldProject && folderStructure.root.children[oldProject]) {
        //     // Elimina la carpeta solo si no es el proyecto actual
        //     if (oldProject !== projectName) {
        //         delete folderStructure.root.children[oldProject];
        //     }
        // }

        // TODO creo que esto sobra
        // await updateFileTeams(fileIndex, projectName);


    } else {
        // Reset to default
        fileData.projects = [];
        fileData.folderStructure = {
            root: {
                name: 'Project Root',
                type: 'folder',
                children: {},
                isEmpty: true
            }
        };

        if (fileData.location === oldProject) {
            fileData.location = 'Project Root';
        } else if (fileData.location.startsWith(oldProject + '/')) {
            fileData.location = 'Project Root' + fileData.location.substring(oldProject.length);
        } else {
            fileData.location = 'Project Root'
        }

        // // Clean up any project-named folders
        // if (oldProject && oldProject !== 'Project Root' && folderStructure.root.children[oldProject]) {
        //     delete folderStructure.root.children[oldProject];
        // }
    }

    await displayFiles();
}

function deleteFolder(path, fileIndex) {
    event.stopPropagation(); // Prevent folder selection when clicking delete
    const fileData = selectedFiles[fileIndex];


    // Check if folder is empty
    const folder = getFolderByPath(fileData.folderStructure.root, path);
    if (folder && Object.keys(folder.children).length === 0) {
        // Check if any files are using this location
        const filesInFolder = selectedFiles.some(file =>
            file.location === path || file.location.startsWith(path + '/'));

        if (!filesInFolder) {
            deleteFolderFromStructure(fileData, path);
            displayFiles();
        } else {
            alert('Cannot delete folder: it contains files');
        }
    } else {
        alert('Cannot delete folder: it contains subfolders');
    }
}

function getFolderByPath(folder, path) {

    let current = folder;
    const parts = path.split('/');

    for (const part of parts) {
        if (!current.children[part]) return null;
        current = current.children[part];
    }
    return current;
}

function deleteFolderFromStructure(fileData, path) {
    const parts = path.split('/');
    const folderName = parts.pop();
    let current = fileData.folderStructure.root;

    for (const part of parts) {
        current = current.children[part];
    }

    delete current.children[folderName];
}


function showNewFolderDialog(fileIndex) {
    const folderName = prompt('Enter new folder name:');
    if (folderName && folderName.trim()) {
        const currentLocation = selectedFiles[fileIndex].location;
        const newPath = currentLocation === 'Project Root'
            ? folderName
            : `${currentLocation}/${folderName}`;

        createFolder(newPath, fileIndex);
        selectedFiles[fileIndex].location = newPath;
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
    if (!value || selectedFiles[fileIndex][type].includes(value)) return;

    selectedFiles[fileIndex][type].push(value);
    displayFiles();
}

function removeTag(fileIndex, type, tag) {
    selectedFiles[fileIndex][type] = selectedFiles[fileIndex][type].filter(t => t !== tag);
    displayFiles();
}


function getStatusIcon(status) {
    const icons = {
        'loading': '<i class="fas fa-clock status-icon"></i>',
        'success': '<i class="fas fa-check status-icon" style="color: green;"></i>',
        'error': '<i class="fas fa-times status-icon" style="color: red;"></i>'
    };
    return icons[status] || '';
}


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
    let hasFailures = false;
    let uploadResults = [];  // Store upload results

    for (let i = 0; i < selectedFiles.length; i++) {
        selectedFiles[i].status = 'loading';
        // displayFiles();

        const formData = new FormData();
        formData.append('file', selectedFiles[i].file);
        formData.append('fileName', selectedFiles[i].fileName);
        formData.append('projects', JSON.stringify(selectedFiles[i].projects));
        formData.append('location', selectedFiles[i].location);
        formData.append('teams', JSON.stringify(selectedFiles[i].teams));
        formData.append('categories', JSON.stringify(selectedFiles[i].categories));

        try {
            const response = await fetch('/api/upload/', {
                method: 'POST',
                body: formData,
                headers: {
                    'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
                }
            });

            const result = await response.json();

            if (response.ok && result.status === 'success') {
                selectedFiles[i].status = 'success';
                selectedFiles[i].fileId = result.fileId;
            } else {
                selectedFiles[i].status = 'error';
                selectedFiles[i].errorMessage = result.message || 'Upload failed';
                hasFailures = true;
            }
        } catch (error) {
            selectedFiles[i].status = 'error';
            selectedFiles[i].errorMessage = 'Network error';
            hasFailures = true;
        }

        uploadResults.push({...selectedFiles[i]});  // Store the result
    }

    // Replace selectedFiles with the results to avoid duplication
    selectedFiles = uploadResults;

    const allFailed = selectedFiles.every(file => file.status === 'error');

    if (allFailed) {
        showWarningModal('All uploads failed. Would you like to retry?');
        document.getElementById('uploadButton').style.display = 'block';
        document.getElementById('continueButton').style.display = 'none';
    } else if (hasFailures) {
        showWarningModal('Some uploads failed. You can continue or retry failed uploads.');
        document.getElementById('continueButton').style.display = 'block';
        document.getElementById('retryFailedButton').style.display = 'block';
    } else {
        document.getElementById('continueButton').style.display = 'block';
    }

    displayFiles();
}

// Function to show warning modal
// TODO: no aparece
function showWarningModal(message) {
    const warningModal = document.createElement('div');
    warningModal.className = 'warning-modal';
    warningModal.innerHTML = `
        <div class="warning-content">
            <i class="fas fa-exclamation-triangle"></i>
            <p>${message}</p>
            <div class="warning-actions">
                <button onclick="hideWarningModal()" class="btn btn-secondary">Close</button>
            </div>
        </div>
    `;
    document.body.appendChild(warningModal);
}

// Function to hide warning modal
function hideWarningModal() {
    const warningModal = document.querySelector('.warning-modal');
    if (warningModal) {
        warningModal.remove();
    }
}

