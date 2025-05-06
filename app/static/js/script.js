document.addEventListener('DOMContentLoaded', function() {
    const searchForm = document.getElementById('searchForm');
    const movieNameInput = document.getElementById('movieName');
    const searchResults = document.getElementById('searchResults');
    const noResults = document.getElementById('noResults');
    const resultsTable = document.getElementById('resultsTable');
    const downloads = document.getElementById('downloads');
    const downloadsTable = document.getElementById('downloadsTable');
    
    // Track active downloads
    const activeDownloads = {};
    
    searchForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const movieName = movieNameInput.value.trim();
        
        if (movieName) {
            searchMovies(movieName);
        }
    });
    
    function searchMovies(movieName) {
        // Show loading indicator
        searchResults.classList.add('d-none');
        noResults.classList.add('d-none');
        resultsTable.innerHTML = '<tr><td colspan="6" class="text-center">Searching...</td></tr>';
        searchResults.classList.remove('d-none');
        
        // Send search request
        const formData = new FormData();
        formData.append('movie_name', movieName);
        
        fetch('/search', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.results && data.results.length > 0) {
                displaySearchResults(data.results);
            } else {
                searchResults.classList.add('d-none');
                noResults.classList.remove('d-none');
            }
        })
        .catch(error => {
            console.error('Error:', error);
            searchResults.classList.add('d-none');
            noResults.textContent = 'An error occurred while searching. Please try again.';
            noResults.classList.remove('d-none');
        });
    }
    
    function displaySearchResults(results) {
        resultsTable.innerHTML = '';
        
        results.forEach((movie, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${movie.title}</td>
                <td>${movie.year}</td>
                <td>${movie.quality}</td>
                <td>${movie.type}</td>
                <td>
                    <button class="btn btn-sm btn-primary download-btn" 
                    data-url="${movie.link}" 
                    data-title="${movie.title}" 
                    data-quality="${movie.quality}">
                        Download
                    </button>
                </td>
            `;
            resultsTable.appendChild(row);
        });
        
        searchResults.classList.remove('d-none');
        
        // Add event listeners to download buttons
        document.querySelectorAll('.download-btn').forEach(btn => {
            btn.addEventListener('click', function() {
                const url = this.getAttribute('data-url');
                const title = this.getAttribute('data-title');
                const quality = this.getAttribute('data-quality');
                startDownload(url, title, quality);
            });
        });
    }
    
    function startDownload(url, title, quality) {
        const formData = new FormData();
        formData.append('url', url);
        formData.append('title', title);
        formData.append('quality', quality);
        
        fetch('/download', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => {
            if (data.download_id) {
                // Add to active downloads
                activeDownloads[data.download_id] = {
                    title: title,
                    status: data.status,
                    progress: 0
                };
                
                // Add to downloads table
                updateDownloadsTable();
                
                // Start polling for status
                pollDownloadStatus(data.download_id);
            }
        })
        .catch(error => {
            console.error('Error starting download:', error);
        });
    }
    
    function updateDownloadsTable() {
        // Show downloads section if not visible
        downloads.classList.remove('d-none');
        
        // Update table
        downloadsTable.innerHTML = '';
        
        Object.entries(activeDownloads).forEach(([id, download]) => {
            const row = document.createElement('tr');
            row.id = `download-${id}`;
            
            let statusText = '';
            let statusClass = '';
            
            switch(download.status) {
                case 'fetching':
                    statusText = 'Finding stream...';
                    statusClass = 'status-fetching';
                    break;
                case 'fetching_mp4':
                    statusText = 'Finding MP4 link...';
                    statusClass = 'status-fetching_mp4';
                    break;
                case 'downloading':
                    statusText = 'Downloading...';
                    statusClass = 'status-downloading';
                    break;
                case 'completed':
                    statusText = 'Completed';
                    statusClass = 'status-completed';
                    break;
                case 'error':
                    statusText = download.error || 'Error';
                    statusClass = 'status-error';
                    break;
                default:
                    statusText = download.status;
            }
            
            row.innerHTML = `
                <td>${download.title}</td>
                <td class="${statusClass}">${statusText}</td>
                <td>
                    <div class="progress">
                        <div class="progress-bar ${download.status === 'completed' ? 'bg-success' : ''}" 
                             role="progressbar" 
                             style="width: ${download.progress}%" 
                             aria-valuenow="${download.progress}" 
                             aria-valuemin="0" 
                             aria-valuemax="100">
                            ${download.progress}%
                        </div>
                    </div>
                </td>
            `;
            
            downloadsTable.appendChild(row);
        });
    }
    
    function pollDownloadStatus(downloadId) {
        if (!activeDownloads[downloadId]) return;
        
        fetch(`/download-status/${downloadId}`)
            .then(response => response.json())
            .then(data => {
                // Update download info
                activeDownloads[downloadId] = {
                    title: data.title,
                    status: data.status,
                    progress: data.progress || 0,
                    error: data.error
                };
                
                updateDownloadsTable();
                
                // Continue polling if not complete/error
                if (data.status !== 'completed' && data.status !== 'error') {
                    setTimeout(() => pollDownloadStatus(downloadId), 1000);
                }
            })
            .catch(error => {
                console.error('Error polling status:', error);
                setTimeout(() => pollDownloadStatus(downloadId), 2000);
            });
    }
});