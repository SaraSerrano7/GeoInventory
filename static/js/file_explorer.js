document.addEventListener('DOMContentLoaded', function () {
    let selectedFiles = new Map();
    let fileStructure = [];
    let map = null;
    let geojsonLayers = new Map();
    let fileColors = new Map();

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
                if (Array.isArray(item)) {
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
                let fileId = e.target.closest('.file-item').id;
                const filePath = e.target.closest('.file-item').dataset.path;

                if (e.target.checked) {
                    selectedFiles.set(fileId, filePath);
                } else {
                    selectedFiles.delete(fileId);
                    // Remove layer from map if it exists
                    fileId = parseInt(fileId);
                    console.log('deleting', fileId, geojsonLayers)
                    console.log(geojsonLayers.has(fileId))
                    if (map && geojsonLayers.has(fileId)) {
                        console.log('removing', geojsonLayers.get(fileId))
                        map.removeLayer(geojsonLayers.get(fileId));
                        geojsonLayers.delete(fileId);
                        const fileItem = document.getElementById(fileId);
                        fileItem.style.backgroundColor = ""
                    }
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
            // const contentDisplay = document.getElementById('content-display');
            // contentDisplay.style.display = 'block';
            const map = document.getElementById('map-container');
            map.style.display = 'none';
            const noDataMessage = document.getElementById('no-data-message');
            noDataMessage.style.display = 'block';
        }
    }

    // View Data functionality
    document.getElementById('view-data-btn').addEventListener('click', () => {

        const contentDisplay = document.getElementById('content-display');
        const mapContainer = document.getElementById('map-container');
        const noDataMessage = document.getElementById('no-data-message');

        if (selectedFiles.size === 0) {
            mapContainer.style.display = 'none';
            contentDisplay.style.display = 'none';
            noDataMessage.style.display = 'block';
            return;
        }

        // Initialize map if not already done
        mapContainer.style.display = 'block';
        noDataMessage.style.display = 'none';
        contentDisplay.style.display = 'none';
        initializeMap();

        // Get the currently selected file IDs
        const currentSelectedIds = Array.from(selectedFiles.keys());

        // Remove layers for unselected files
        console.log(geojsonLayers);
        console.log(currentSelectedIds);
        geojsonLayers.forEach((layer, fileId) => {
            if (!currentSelectedIds.includes(fileId)) {
                map.removeLayer(layer);
                geojsonLayers.delete(fileId);
                const fileItem = document.getElementById(parseInt(content['file_id']));
                if (fileItem) {
                    fileItem.style.backgroundColor = '';
                }
            }
        });


        fetch('/api/files/content/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken')
            },
            body: JSON.stringify({
                files: Array.from(selectedFiles, ([id, path]) => ({id, path}))
            })
        })
            .then(response => response.json())
            .then(data => {

                let isFirstFeature = true;

                // document.getElementById('no-data-message').style.display = 'none';
                // const contentDisplay = document.getElementById('content-display');
                // contentDisplay.style.display = 'block';

                var files_data = data.content
                files_data.forEach(file => {
                    console.log('received', file)
                    // contentDisplay.innerHTML += `<pre>${data.content}</pre>`;
                })

                Object.entries(data.content).forEach(([fileId, content]) => {
                    // Skip if layer already exists
                    if (geojsonLayers.has(fileId)) return;

                    try {
                        console.log(content['file_content'])
                        const geojsonData = content['file_content']

                        const fileColor = generateRandomColor();
                        fileColors.set(fileId, fileColor);

                        const layer = L.geoJSON(geojsonData, {
                            style: {
                                color: fileColor,
                                weight: 2,
                                opacity: 0.7,
                                fillColor: fileColor,
                                fillOpacity: 0.3
                            },
                            pointToLayer: (feature, latlng) => {
                                return L.circleMarker(latlng, {
                                    radius: 8,
                                    fillColor: fileColor,
                                    color: "#000",
                                    weight: 1,
                                    opacity: 1,
                                    fillOpacity: 0.8
                                });
                            },
                            onEachFeature: (feature, layer) => {
                                if (feature.properties) {
                                    layer.bindPopup(
                                        createPropertiesPopup(feature.properties)
                                    );
                                }
                            }
                        }).addTo(map);


                        console.log('before add', geojsonLayers);
                        geojsonLayers.set(content['file_id'], layer);
                        console.log('after add', geojsonLayers);

                        console.log(parseInt(content['file_id']))
                        const fileItem = document.getElementById(parseInt(content['file_id']));
                        console.log('showing file:', fileItem);
                        if (fileItem) {
                            console.log('changing color', fileColor + '20')
                            console.log('current color', fileItem.style.backgroundColor)
                            fileItem.style.backgroundColor = fileColor.replace('hsl', 'hsla').replace(')', ', 0.125)');

                            console.log('current color', fileItem.style.backgroundColor)
                        }

                        if (isFirstFeature) {
                            centerMapOnFirstFeature(geojsonData);
                            isFirstFeature = false;
                        }
                    } catch (e) {
                        console.error('Error parsing GeoJSON:', e);
                    }
                });


            })
            .catch(error => console.error('Error:', error));
    });


    function initializeMap() {
        if (!map) {

            map = L.map('map-container').setView([0, 0], 2);


            const tileLayers = {
                'OpenStreetMap': L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
                    attribution: '© OpenStreetMap contributors'
                }),
                'Orthophoto': L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
                    attribution: 'Tiles © Esri — Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community'
                })
            };

            // Add the default OpenStreetMap layer
            tileLayers['OpenStreetMap'].addTo(map);

            // Add layer control
            L.control.layers(tileLayers).addTo(map);

            const customIcon = L.divIcon({
                className: 'custom-marker',
                html: `
                    <div style="
                        width: 30px;
                        height: 30px;
                        background-color: #007bff;
                        border-radius: 50%;
                        border: 3px solid white;
                        box-shadow: 0 0 10px rgba(0,0,0,0.3);
                    "></div>
                `,
                iconSize: [30, 30],
                iconAnchor: [15, 15]
            });
        }
    }

    function centerMapOnFirstFeature(geojson) {
        if (geojson.features && geojson.features.length > 0) {
            const feature = geojson.features[0];
            if (feature.geometry) {
                if (feature.geometry.type === 'Point') {
                    const coords = feature.geometry.coordinates;
                    map.setView([coords[1], coords[0]], 10);
                } else {
                    const layer = L.geoJSON(feature);
                    map.fitBounds(layer.getBounds());
                }
            }
        } else {
            if (geojson['geometry']) {
                if (geojson['geometry'].type === 'Point') {
                    const coords = geojson['geometry'].coordinates;
                    map.setView([coords[1], coords[0]], 10);
                } else {
                    const layer = L.geoJSON(geojson);
                    map.fitBounds(layer.getBounds());
                }
            }
        }
    }

    function generateRandomColor() {
        const hue = Math.floor(Math.random() * 360);
        return `hsl(${hue}, 70%, 50%)`;
    }

    function createPropertiesPopup(properties) {
        if (!properties || Object.keys(properties).length === 0) {
            return '<div class="geojson-properties"><p>No properties available</p></div>';
        }

        let popupContent = '<div class="geojson-properties">';
        popupContent += '<h3>Feature Properties</h3>';

        Object.entries(properties).forEach(([key, value]) => {
            popupContent += `
                <div class="property-item">
                    <span class="property-name">${key}</span>
                    <span class="property-value">${
                value === null ? 'null' :
                    value === undefined ? 'undefined' :
                        value.toString()
            }</span>
                </div>
            `;
        });

        popupContent += '</div>';
        return popupContent;
    }


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
