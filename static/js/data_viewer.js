// document.addEventListener('DOMContentLoaded', function () {
//     let selectedFiles = new Map();
//     let fileStructure = [];
//     let map = null;
//     let geojsonLayers = new Map(); // Store layers by file ID
//
//     // Initialize Leaflet map
//     function initializeMap() {
//         if (!map) {
//             map = L.map('map-container').setView([0, 0], 2);
//             L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
//                 attribution: '© OpenStreetMap contributors'
//             }).addTo(map);
//         }
//     }
//
//     // Function to center map on first feature
//     function centerMapOnFirstFeature(geojson) {
//         if (geojson.features && geojson.features.length > 0) {
//             const feature = geojson.features[0];
//             if (feature.geometry) {
//                 if (feature.geometry.type === 'Point') {
//                     const coords = feature.geometry.coordinates;
//                     map.setView([coords[1], coords[0]], 10);
//                 } else {
//                     const layer = L.geoJSON(feature);
//                     map.fitBounds(layer.getBounds());
//                 }
//             }
//         }
//     }
//
//     // Modify the View Data functionality
//     document.getElementById('view-data-btn').addEventListener('click', () => {
//         const contentDisplay = document.getElementById('content-display');
//         const mapContainer = document.getElementById('map-container');
//         const noDataMessage = document.getElementById('no-data-message');
//
//         if (selectedFiles.size === 0) {
//             mapContainer.style.display = 'none';
//             contentDisplay.style.display = 'none';
//             noDataMessage.style.display = 'block';
//             return;
//         }
//
//         // Initialize map if not already done
//         mapContainer.style.display = 'block';
//         noDataMessage.style.display = 'none';
//         contentDisplay.style.display = 'none';
//         initializeMap();
//
//         // Get the currently selected file IDs
//         const currentSelectedIds = Array.from(selectedFiles.keys());
//
//         // Remove layers for unselected files
//         geojsonLayers.forEach((layer, fileId) => {
//             if (!currentSelectedIds.includes(fileId)) {
//                 map.removeLayer(layer);
//                 geojsonLayers.delete(fileId);
//             }
//         });
//
//         // Fetch and display new files
//         fetch('/api/files/content/', {
//             method: 'POST',
//             headers: {
//                 'Content-Type': 'application/json',
//                 'X-CSRFToken': getCookie('csrftoken')
//             },
//             body: JSON.stringify({
//                 files: Array.from(selectedFiles, ([id, path]) => ({ id, path }))
//             })
//         })
//         .then(response => response.json())
//         .then(data => {
//             let isFirstFeature = true;
//
//             Object.entries(data.content).forEach(([fileId, content]) => {
//                 // Skip if layer already exists
//                 if (geojsonLayers.has(fileId)) return;
//
//                 try {
//                     const geojsonData = JSON.parse(content);
//                     const layer = L.geoJSON(geojsonData, {
//                         style: {
//                             color: '#' + Math.floor(Math.random()*16777215).toString(16),
//                             weight: 2,
//                             opacity: 0.7
//                         },
//                         onEachFeature: (feature, layer) => {
//                             if (feature.properties) {
//                                 layer.bindPopup(
//                                     `<pre>${JSON.stringify(feature.properties, null, 2)}</pre>`
//                                 );
//                             }
//                         }
//                     }).addTo(map);
//
//                     geojsonLayers.set(fileId, layer);
//
//                     if (isFirstFeature) {
//                         centerMapOnFirstFeature(geojsonData);
//                         isFirstFeature = false;
//                     }
//                 } catch (e) {
//                     console.error('Error parsing GeoJSON:', e);
//                 }
//             });
//         })
//         .catch(error => console.error('Error:', error));
//     });
//
//     // Modify file checkbox event listener to handle map layers
//     document.querySelectorAll('.file-checkbox').forEach(checkbox => {
//         checkbox.addEventListener('change', (e) => {
//             const fileId = e.target.closest('.file-item').id;
//             const filePath = e.target.closest('.file-item').dataset.path;
//
//             if (e.target.checked) {
//                 selectedFiles.set(fileId, filePath);
//             } else {
//                 selectedFiles.delete(fileId);
//                 // Remove layer from map if it exists
//                 if (map && geojsonLayers.has(fileId)) {
//                     map.removeLayer(geojsonLayers.get(fileId));
//                     geojsonLayers.delete(fileId);
//                 }
//             }
//             updateUI();
//         });
//     });
//
//     // ... rest of your existing code ...
// });