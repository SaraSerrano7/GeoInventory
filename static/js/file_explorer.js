document.addEventListener('DOMContentLoaded', function () {
    let selectedFiles = new Set();
    let fileStructure = [];

    // Fetch file structure from Django backend
    function fetchFileStructure() {
        fetch('/api/files/structure/')
            .then(response => response.json())
            .then(data => {
                fileStructure = data;
                console.log(fileStructure)
                renderFileTree();
            })
            .catch(error => console.error('Error:', error));
    }

    // Render file tree
    function renderFileTree() {
        const treeContainer = document.getElementById('file-tree');
        treeContainer.innerHTML = generateTreeHTML(fileStructure);

        // Add event listeners after rendering
        addTreeEventListeners();
    }

    function generateTreeHTML(items, level = 0) {
        let html = '<div class="tree-level" style="margin-left: ' + (level * 20) + 'px;">';

        items.forEach(item => {
            if (item.type === 'folder') {
                html += `
                    <div class="folder-item" data-path="${item.path}">
                        <i class="fas fa-chevron-right folder-toggle"></i>
                        <i class="fas fa-folder folder-icon"></i>
                        <span>${item.name}</span>
                    </div>
                    <div class="folder-content" style="display: none;">
                        ${item.children ? generateTreeHTML(item.children, level + 1) : ''}
                    </div>
                `;
            } else {
                if(Array.isArray(item)) {
                    item = item[0]
                }

                html += `
                    <div id="${item.id}" class="file-item ${selectedFiles.has(item.path) ? 'highlighted' : ''}" data-path="${item.path}">
                        <input type="checkbox" class="file-checkbox"
                            ${selectedFiles.has(item.path) ? 'checked' : ''}>
                        <i class="fas fa-file file-icon"></i>
                        <span>${item.name}</span>
                    </div>
                `;
            }
        });

        html += '</div>';
        return html;
    }

    function addTreeEventListeners() {
        // Folder toggle
        document.querySelectorAll('.folder-toggle').forEach(toggle => {
            toggle.addEventListener('click', (e) => {
                e.stopPropagation();
                const folderItem = e.target.closest('.folder-item');
                const folderContent = folderItem.nextElementSibling;
                const isExpanded = folderContent.style.display !== 'none';

                folderContent.style.display = isExpanded ? 'none' : 'block';
                e.target.classList.toggle('fa-chevron-down');
                e.target.classList.toggle('fa-chevron-right');
            });
        });

        // File selection
        document.querySelectorAll('.file-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                const filePath = e.target.closest('.file-item').dataset.path;
                const fileId = e.target.closest('.file-item').id;

                console.log(e.target.closest('.file-item').id);

                if (e.target.checked) {
                    selectedFiles.add({
                        'id':fileId,
                        'path': filePath
                    });
                } else {
                    selectedFiles.delete({
                        'id':fileId,
                        'path': filePath
                    });
                }

                updateUI();
            });
        });
    }

    function updateUI() {
        const actionButtons = document.getElementById('action-buttons');
        const selectedCount = document.getElementById('selected-count');

        if (selectedFiles.size > 0) {
            actionButtons.style.display = 'block';
            selectedCount.style.display = 'inline';
            selectedCount.textContent = `${selectedFiles.size} selected`;
        } else {
            actionButtons.style.display = 'none';
            selectedCount.style.display = 'none';
        }
    }

    // View Data functionality
    document.getElementById('view-data-btn').addEventListener('click', () => {

        console.log(selectedFiles)
        fetch('/api/files/content/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                files: Array.from(selectedFiles)
            })
        })
            .then(response => response.json())
            .then(data => {
                document.getElementById('no-data-message').style.display = 'none';
                const contentDisplay = document.getElementById('content-display');
                contentDisplay.style.display = 'block';
                contentDisplay.innerHTML = `<pre>${data.content}</pre>`;
            })
            .catch(error => console.error('Error:', error));
    });

    // // Analysis functionality
    // const analysisModal = document.getElementById('analysis-modal');
    // const closeButtons = document.querySelectorAll('.close-modal');

    // document.getElementById('analyze-data-btn').addEventListener('click', () => {
    //     analysisModal.style.display = 'block';
    // });
    //
    // closeButtons.forEach(button => {
    //     button.addEventListener('click', () => {
    //         analysisModal.style.display = 'none';
    //     });
    // });
    //
    // document.getElementById('perform-analysis-btn').addEventListener('click', () => {
    //     const analysisType = document.getElementById('analysis-type').value;
    //
    //     if (!analysisType) return;
    //
    //     fetch('/api/files/analyze/', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json',
    //             'X-CSRFToken': getCookie('csrftoken')
    //         },
    //         body: JSON.stringify({
    //             files: Array.from(selectedFiles),
    //             analysisType: analysisType
    //         })
    //     })
    //         .then(response => response.json())
    //         .then(data => {
    //             // Display results
    //             const resultsDiv = document.getElementById('analysis-results');
    //             resultsDiv.style.display = 'block';
    //             resultsDiv.innerHTML = `
    //             <h3>Analysis Results</h3>
    //             <pre>${data.results}</pre>
    //         `;
    //
    //             // Highlight matching files
    //             document.querySelectorAll('.file-item').forEach(item => {
    //                 item.classList.remove('highlighted');
    //                 if (data.matchingFiles.includes(item.dataset.path)) {
    //                     item.classList.add('highlighted');
    //                 }
    //             });
    //
    //             analysisModal.style.display = 'none';
    //         })
    //         .catch(error => console.error('Error:', error));
    // });

    // Helper function to get CSRF token
    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    // Initialize
    fetchFileStructure();
});
