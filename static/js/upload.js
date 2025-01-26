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

async function fetchUserTeams(projectName) {
    try {
        const response = await fetch('/api/user_teams/${projectName}', {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch teams');
        }

        return await response.json();
    } catch (error) {
        console.error('Error fetching teams:', error);
        return [];
    }
}

// async function updateFileTeams(fileIndex, projectName) {
//     try {
//         const response = await fetch(`/api/user_teams/${projectName}`, {
//             method: 'GET',
//             headers: {
//                 'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
//             }
//         });
//         console.log('response', response)
//         if (!response.ok) {
//             throw new Error('Failed to fetch teams');
//         }
//
//         const teams = await response.json();
//
//         console.log(`teams-${fileIndex}`)
//         const findteamSelect = document.getElementById(`teams-${fileIndex}`)
//         console.log(findteamSelect)
//
//         const teamSelect = document.getElementById(`teams-${fileIndex}`).querySelector('select');
//         const teamSelect2 = document.getElementById(`teams-${fileIndex} select`)
//
//         console.log('teamSelect', teamSelect)
//         console.log('teamSelect2', teamSelect)
//         console.log('fileIndex', fileIndex)
//
//         console.log(Array.isArray(teams))
//         console.log(Array.isArray(teams.teams))
//
//         // findteamSelect.innerHTML = ''
//         findteamSelect.innerHTML = '<option value="">Select team</option>'; // Reset options
//         console.log('teams', teams)
//         console.log('teams', teams.teams)
//         teams.teams.forEach(team => {
//             console.log('team:', team)
//             console.log('team name', team.name)
//             const option = document.createElement('option');
//             console.log('option', option)
//             option.value = team.name;
//             option.textContent = team.name;
//             option.text = team.name;
//             console.log('option', option)
//             findteamSelect.appendChild(option);
//             console.log('Updated options innerhtml:', findteamSelect.innerHTML);
//             console.log('Updated options', findteamSelect);
//         });
//
//
//
//     } catch (error) {
//         console.error('Error fetching teams for project:', error);
//     }
//
//
//     await displayFiles();
// }

async function updateFileTeams(fileIndex, projectName) {
    try {
        const response = await fetch(`/api/user_teams/${projectName}`, {
            method: 'GET',
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });

        const teams = await response.json();

        // Debug logs
        console.log('Looking for element:', `teams-${fileIndex}`);
        const teamSelect = document.querySelector(`select[id="teams-${fileIndex}"]`);
        console.log('Found select element:', teamSelect);

        if (!teamSelect) {
            console.error('Select element not found');
            return;
        }

        teamSelect.innerHTML = '<option value="">Select team</option>';

        console.log(teams)
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
function mergeFolderStructures(existingFolders) {
    existingFolders.forEach(folder => {
        const pathParts = folder.path.split('/').filter(p => p);
        let current = folderStructure.root;
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

function createFolder(path) {

    console.log('path', path)
    const pathParts = path.split('/');
    console.log('pathParts', pathParts)
    let currentFolder = folderStructure.root;
    console.log('folderStructure.root', folderStructure.root)
    console.log('currentFolder', currentFolder)
    // Navegar a la ubicación deseada
    for (const part of pathParts) {
        console.log('part', part)
        console.log('currentFolder', currentFolder)
        if (!currentFolder.children[part]) {
            // no existe la carpeta
            if (currentFolder.name === part) {
                continue
            } else {
                console.log('if', !currentFolder.children[part], currentFolder.children[part])
                currentFolder.children[part] = {children: {}, isEmpty: true}; // Crear nueva carpeta si no existe
                console.log('currentFolder', currentFolder)
            }

        }
        currentFolder = currentFolder.children[part];
    }

    console.log('nueva carpeta', folderStructure)

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
    console.log('displaying files')
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';

    // Fetch user's projects
    const userProjects = await fetchUserProjects();
    // const userTeams = await fetchUserTeams();

    selectedFiles.forEach((fileData, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-item';

        const currentProject = fileData.projects[0] || 'Project Root';
        console.log('now', currentProject)

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
                    ${generateFolderTree(folderStructure.root, '', index, currentProject)}
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

        if(currentProject !== 'Project Root') {
            updateFileTeams(index, currentProject)
        }


    });
}

// function generateFolderTree(folder, path, fileIndex, currentProject) {
//     // Determine root folder name based on project selection
//     console.log('folder', folder)
//     console.log('path', path)
//     console.log('fileIndex', fileIndex)
//     console.log('currentProject', currentProject)
//
//     const rootName = currentProject === 'Project Root' ? 'Project Root' : currentProject;
//
//     console.log('rootName', rootName)
//
//     let tree = '';
//
//     // Only show root folder if we're at the top level
//     if (path === '') {
//         tree = `
//             <div class="folder-item active" onclick="updateLocation(${fileIndex}, '${rootName}')">
//                 <i class="fas fa-folder-open"></i>
//                 <span>${rootName}</span>
//             </div>
//         `;
//         console.log('new tree', tree)
//     } else {
//         // For subfolders, don't show if it's the same as the project name
//         const folderName = path.split('/').pop();
//         if (folderName !== currentProject) {
//             tree = `
//                 <div class="folder-item" onclick="updateLocation(${fileIndex}, '${path}')">
//                     <i class="fas fa-folder"></i>
//                     <span>${folderName}</span>
//                     <button onclick="deleteFolder('${path}', ${fileIndex})" class="delete-folder-btn" title="Delete folder">
//                         <i class="fas fa-trash"></i>
//                     </button>
//                 </div>
//             `;
//         }
//         console.log('new folder name', folderName)
//         console.log('new tree', tree)
//     }
//
//     // Show subfolders only if they're not the same as the project name
//     const sortedFolders = Object.entries(folder.children)
//         .filter(([name]) => name !== currentProject)
//         .sort(([a], [b]) => a.localeCompare(b));
//
//     console.log('sorted folders', sortedFolders)
//
//     if (sortedFolders.length > 0) {
//         tree += '<div class="subfolder-container">';
//         for (const [name, content] of sortedFolders) {
//             const newPath = path ? `${path}/${name}` : name;
//             tree += generateFolderTree(content, newPath, fileIndex, currentProject);
//         }
//         tree += '</div>';
//     }
//
//     console.log('new final tree', tree)
//
//     return tree;
// }

function generateFolderTree(folder, path, fileIndex, currentProject) {
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
                    ${folder.isEmpty ? `
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

    // Subcarpetas
    if (folder && folder.children) {
        const subfolders = Object.entries(folder.children)
            .filter(([name]) => name !== currentProject) // Excluir el proyecto actual del árbol
            .sort(([a], [b]) => a.localeCompare(b)); // Ordenar alfabéticamente

        if (subfolders.length > 0) {
            tree += '<div class="subfolder-container">';
            for (const [name, content] of subfolders) {
                const newPath = path ? `${path}/${name}` : name;
                tree += generateFolderTree(content, newPath, fileIndex, currentProject);
            }
            tree += '</div>';
        }
    }

    return tree;
}

function updateFileName(fileIndex, newName) {
    selectedFiles[fileIndex].fileName = newName;
}

// function updateFileProject(fileIndex, projectName) {
//     const fileData = selectedFiles[fileIndex];
//     const oldProject = fileData.projects[0];
//
//     if (projectName) {
//         // Update this file's project
//         fileData.projects = [projectName];
//
//         // Update location to new project root
//         if (fileData.location === 'Project Root' || fileData.location === oldProject) {
//             fileData.location = projectName;
//         } else if (oldProject && fileData.location.startsWith(oldProject + '/')) {
//             fileData.location = projectName + fileData.location.substring(oldProject.length);
//         }
//     } else {
//         // Reset to default
//         fileData.projects = [];
//         if (fileData.location === oldProject) {
//             fileData.location = 'Project Root';
//         }
//     }
//
//     displayFiles();
// }

async function updateFileProject(fileIndex, projectName) {
    const fileData = selectedFiles[fileIndex];
    const oldProject = fileData.projects[0];
    console.log('project name', projectName)


    if (projectName) {
        // Update this file's project
        fileData.projects = [projectName];

        const existingFolders = await fetchProjectFolders(projectName);
        console.log('existingFolders', existingFolders)
        folderStructure = {
            root: {
                name: projectName,
                type: 'folder',
                children: {},
                isEmpty: true
            }
        };
        mergeFolderStructures(existingFolders);


        // Update location to new project root
        if (fileData.location === 'Project Root' || fileData.location === oldProject) {
            fileData.location = projectName;
        } else if (oldProject && fileData.location.startsWith(oldProject + '/')) {
            // Update paths for files in subfolders
            fileData.location = projectName + fileData.location.substring(oldProject.length);
        }

        // // Clear any old project folders from the structure
        // if (oldProject && oldProject !== 'Project Root' && folderStructure.root.children[oldProject]) {
        //     delete folderStructure.root.children[oldProject];
        // }
        if (oldProject && folderStructure.root.children[oldProject]) {
            // Elimina la carpeta solo si no es el proyecto actual
            if (oldProject !== projectName) {
                delete folderStructure.root.children[oldProject];
            }
        }

        // const userTeams = await fetchUserTeams(projectName);
        // updateTeamsDropdown(fileIndex, userTeams);
        await updateFileTeams(fileIndex, projectName);


    } else {
        console.log('file project', projectName)
        // Reset to default
        fileData.projects = [];
        folderStructure = {
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

        console.log('new location', fileData.location)

        // Clean up any project-named folders
        if (oldProject && oldProject !== 'Project Root' && folderStructure.root.children[oldProject]) {
            delete folderStructure.root.children[oldProject];
        }
    }

    await displayFiles();
}

function updateTeamsDropdown(fileIndex, teams) {
    const selectElement = document.getElementById(`teams-select-${fileIndex}`);
    selectElement.innerHTML = '<option value="">Select team</option>';

    teams.forEach(team => {
        const option = document.createElement('option');
        option.value = team.name;
        option.textContent = team.name;
        selectElement.appendChild(option);
    });
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


function showNewFolderDialog(fileIndex) {
    const folderName = prompt('Enter new folder name:');
    if (folderName && folderName.trim()) {
        const currentLocation = selectedFiles[fileIndex].location;
        const newPath = currentLocation === 'Project Root'
            ? folderName
            : `${currentLocation}/${folderName}`;

        createFolder(newPath);
        selectedFiles[fileIndex].location = newPath;

        console.log(selectedFiles)

        // displayFiles();
    }
}

function updateLocation(fileIndex, newLocation) {
    console.log('fileIndex', fileIndex)
    console.log('newLocation', newLocation)
    console.log('selectedFiles', selectedFiles)

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
                    <label>Project</label>
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

// New function to handle retrying uploads
function retryUpload() {
    // Reset status for failed uploads
    selectedFiles = selectedFiles.map(file => ({
        ...file,
        status: file.status === 'error' ? null : file.status,
        errorMessage: file.status === 'error' ? null : file.errorMessage
    }));

    document.getElementById('continueButton').style.display = 'none';
    document.getElementById('uploadButton').style.display = 'block';
    document.getElementById('retryFailedButton').style.display = 'none';
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

