

function showSection(sectionId) {
    // Hide all sections, including the home section
    document.querySelectorAll('main section, #home-section').forEach(section => {
        section.classList.add('hidden');
    });

    // Show the selected section
    const selectedSection = document.getElementById(sectionId);
    if (selectedSection) {
        selectedSection.classList.remove('hidden');
        selectedSection.scrollIntoView({ behavior: 'smooth' });
    }
}

function showHome() {
    // Hide all sections
    document.querySelectorAll('main section').forEach(section => {
        section.classList.add('hidden');
    });

    // Show the home section
    const homeSection = document.getElementById('home-section');
    if (homeSection) {
        homeSection.classList.remove('hidden');
        homeSection.scrollIntoView({ behavior: 'smooth' });
    }
}

// Function to fetch and display stock news dynamically
function fetchGeneralStockNews() {
    const newsContentDiv = document.getElementById("news-content");

    fetch('/get_general_stock_news/')
        .then(response => {
            if (!response.ok) {
                throw new Error("Network response was not ok");
            }
            return response.json();
        })
        .then(data => {
            if (data && data.news && data.news.length > 0) {
                let newsHtml = ""; // Use a template literal to build the HTML
                data.news.forEach((news, index) => {
                    newsHtml += `
                        <div class="news-item">
                            <h3>News ${index + 1}</h3>
                            <p><strong>Published:</strong> ${new Date(news.published).toLocaleString()}</p>
                            <p><strong>Title:</strong> <a href="${news.url}" target="_blank">${news.title}</a></p>
                            <p><strong>Summary:</strong> ${news.summary}</p>
                        </div>
                    `;
                });
                newsContentDiv.innerHTML = newsHtml;
            } else {
                newsContentDiv.innerHTML = "<p>No general stock news found.</p>";
            }
        })
        .catch(error => {
            console.error("Error fetching news:", error);
            newsContentDiv.innerHTML = "<p>Error fetching news. Please try again later.</p>";
        });
}

// Call fetchGeneralStockNews initially and set it to refresh every minute
fetchGeneralStockNews();
setInterval(fetchGeneralStockNews, 60000); // Refresh every 60 seconds
