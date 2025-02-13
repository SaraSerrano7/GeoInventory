// Add this to your existing JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // ... (keep your existing initialization code) ...

    // Add Select All button
    // const fileTree = document.getElementById('file-tree');
    // const selectAllBtn = document.createElement('button');
    // selectAllBtn.className = 'select-all-btn';
    // selectAllBtn.textContent = 'Select All';
    // fileTree.parentNode.insertBefore(selectAllBtn, fileTree);
    //
    // let allSelected = false;
    // selectAllBtn.addEventListener('click', () => {
    //     const checkboxes = document.querySelectorAll('.file-checkbox');
    //     allSelected = !allSelected;
    //
    //     checkboxes.forEach(checkbox => {
    //         checkbox.checked = allSelected;
    //         const fileItem = checkbox.closest('.file-item');
    //         const fileId = fileItem.id;
    //         const filePath = fileItem.dataset.path;
    //
    //         if (allSelected) {
    //             selectedFiles.set(fileId, filePath);
    //         } else {
    //             selectedFiles.delete(fileId);
    //             if (map && geojsonLayers.has(fileId)) {
    //                 map.removeLayer(geojsonLayers.get(fileId));
    //                 geojsonLayers.delete(fileId);
    //             }
    //         }
    //     });
    //
    //     selectAllBtn.textContent = allSelected ? 'Unselect All' : 'Select All';
    //     updateUI();
    // });
    //
    // // Analysis Modal
    // const analysisModal = document.createElement('div');
    // analysisModal.className = 'analysis-modal';
    // analysisModal.innerHTML = `
    //     <div class="analysis-modal-content">
    //         <span class="close-modal">&times;</span>
    //         <h2>Choose Analysis</h2>
    //         <div class="analysis-options">
    //             <select id="analysis-type">
    //                 <option value="area">Find content by area</option>
    //             </select>
    //         </div>
    //         <div class="modal-buttons">
    //             <button id="cancel-analysis" class="btn btn-secondary">Cancel</button>
    //             <button id="apply-analysis" class="btn btn-primary">Apply</button>
    //         </div>
    //     </div>
    // `;
    // document.body.appendChild(analysisModal);
    //
    // // Analysis functionality
    // let drawingPoints = [];
    // let drawingLayer = null;
    // let polygonLayer = null;
    // let resultLayer = null;
    //
    // document.getElementById('analyze-data-btn').addEventListener('click', () => {
    //     analysisModal.style.display = 'block';
    // });
    //
    // document.querySelector('.close-modal').addEventListener('click', () => {
    //     analysisModal.style.display = 'none';
    // });
    //
    // document.getElementById('cancel-analysis').addEventListener('click', () => {
    //     analysisModal.style.display = 'none';
    // });
    //
    // document.getElementById('apply-analysis').addEventListener('click', () => {
    //     analysisModal.style.display = 'none';
    //     initializeDrawing();
    // });
    //
    // function initializeDrawing() {
    //     const mapContainer = document.getElementById('map-container');
    //     mapContainer.style.display = 'block';
    //     document.getElementById('no-data-message').style.display = 'none';
    //
    //     if (!map) {
    //         initializeMap();
    //     }
    //
    //     // Clear existing points and layers
    //     drawingPoints = [];
    //     if (drawingLayer) map.removeLayer(drawingLayer);
    //     if (polygonLayer) map.removeLayer(polygonLayer);
    //     if (resultLayer) map.removeLayer(resultLayer);
    //
    //     // Add drawing controls
    //     const drawControls = document.createElement('div');
    //     drawControls.className = 'draw-controls';
    //     drawControls.innerHTML = `
    //         <div>Click on the map to draw the area</div>
    //         <button id="clear-points" class="btn btn-secondary">Clear Points</button>
    //         <button id="start-analysis" class="btn btn-primary" style="display: none;">Start Analysis</button>
    //     `;
    //     mapContainer.appendChild(drawControls);
    //
    //     // Drawing functionality
    //     map.on('click', onMapClick);
    //
    //     document.getElementById('clear-points').addEventListener('click', () => {
    //         clearDrawing();
    //     });
    //
    //     document.getElementById('start-analysis').addEventListener('click', () => {
    //         performAnalysis();
    //     });
    // }
    //
    // function onMapClick(e) {
    //     const point = [e.latlng.lat, e.latlng.lng];
    //     drawingPoints.push(point);
    //     updateDrawing();
    // }
    //
    // function updateDrawing() {
    //     if (drawingLayer) map.removeLayer(drawingLayer);
    //
    //     drawingLayer = L.featureGroup().addTo(map);
    //
    //     // Draw points
    //     drawingPoints.forEach((point, index) => {
    //         L.circleMarker([point[0], point[1]], {
    //             radius: 5,
    //             color: '#ff4444',
    //             fillColor: '#ff4444',
    //             fillOpacity: 1
    //         }).addTo(drawingLayer);
    //     });
    //
    //     // Draw lines between points
    //     if (drawingPoints.length > 1) {
    //         L.polyline(drawingPoints, {
    //             color: '#ff4444',
    //             weight: 2
    //         }).addTo(drawingLayer);
    //     }
    //
    //     // Show/hide start analysis button
    //     document.getElementById('start-analysis').style.display =
    //         drawingPoints.length >= 3 ? 'block' : 'none';
    // }
    //
    // function clearDrawing() {
    //     drawingPoints = [];
    //     if (drawingLayer) map.removeLayer(drawingLayer);
    //     document.getElementById('start-analysis').style.display = 'none';
    // }
    //
    // function performAnalysis() {
    //     // Send analysis request to backend
    //     fetch('/api/analyze/area/', {
    //         method: 'POST',
    //         headers: {
    //             'Content-Type': 'application/json',
    //             'X-CSRFToken': getCookie('csrftoken')
    //         },
    //         body: JSON.stringify({
    //             points: drawingPoints,
    //             fileIds: Array.from(selectedFiles.keys())
    //         })
    //     })
    //     .then(response => response.json())
    //     .then(data => {
    //         if (data.features && data.fileIds) {
    //             displayResults(data);
    //         }
    //     })
    //     .catch(error => console.error('Error:', error));
    // }
    //
    // function displayResults(data) {
    //     // Clear previous results
    //     if (resultLayer) map.removeLayer(resultLayer);
    //
    //     // Display results on map
    //     resultLayer = L.geoJSON(data.features, {
    //         style: {
    //             color: '#00ff00',
    //             weight: 2,
    //             opacity: 0.7,
    //             fillColor: '#00ff00',
    //             fillOpacity: 0.3
    //         }
    //     }).addTo(map);
    //
    //     // Highlight matching files
    //     document.querySelectorAll('.file-item').forEach(item => {
    //         item.style.backgroundColor = '';
    //         if (data.fileIds.includes(parseInt(item.id))) {
    //             item.style.backgroundColor = 'rgba(0, 255, 0, 0.2)';
    //         }
    //     });
    //
    //     // Add finish button
    //     const finishBtn = document.createElement('button');
    //     finishBtn.className = 'btn btn-primary';
    //     finishBtn.textContent = 'Finish Analysis';
    //     finishBtn.onclick = finishAnalysis;
    //     document.querySelector('.draw-controls').appendChild(finishBtn);
    // }
    //
    // function finishAnalysis() {
    //     // Clear map
    //     if (drawingLayer) map.removeLayer(drawingLayer);
    //     if (polygonLayer) map.removeLayer(polygonLayer);
    //     if (resultLayer) map.removeLayer(resultLayer);
    //
    //     // Hide map
    //     document.getElementById('map-container').style.display = 'none';
    //     document.getElementById('no-data-message').style.display = 'block';
    //
    //     // Reset file highlighting
    //     document.querySelectorAll('.file-item').forEach(item => {
    //         item.style.backgroundColor = '';
    //     });
    //
    //     // Remove drawing controls
    //     document.querySelector('.draw-controls').remove();
    // }
});