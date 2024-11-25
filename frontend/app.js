// Base URL for the API Gateway
const BASE_URL = "https://your-api-gateway-url/v1";

// Function to search for photos based on a query
async function searchPhotos(query) {
  try {
    if (!query) {
      alert("Please enter a search query!");
      return;
    }

    // Construct the search URL
    const url = `${BASE_URL}/search?q=${encodeURIComponent(query)}`;
    
    // Perform the GET request
    const response = await fetch(url);
    
    // Check if the response is successful
    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    // Parse the JSON response
    const data = await response.json();

    // Handle search results
    displaySearchResults(data.results);
  } catch (error) {
    console.error("Error during photo search:", error);
    alert("An error occurred while searching for photos. Please try again.");
  }
}

// Function to display search results
function displaySearchResults(results) {
  const resultsContainer = document.getElementById("results");
  resultsContainer.innerHTML = ""; // Clear previous results

  if (results.length === 0) {
    resultsContainer.innerHTML = "<p>No photos found for the query.</p>";
    return;
  }

  results.forEach(photo => {
    const photoElement = document.createElement("div");
    photoElement.className = "photo";

    const img = document.createElement("img");
    img.src = photo.url;
    img.alt = "Photo";
    img.className = "photo-img";

    const labels = document.createElement("p");
    labels.innerText = `Labels: ${photo.labels.join(", ")}`;

    photoElement.appendChild(img);
    photoElement.appendChild(labels);
    resultsContainer.appendChild(photoElement);
  });
}

// Function to upload a photo
async function uploadPhoto(file) {
  try {
    if (!file) {
      alert("Please select a photo to upload!");
      return;
    }

    // Create a FormData object for multi-part upload
    const formData = new FormData();
    formData.append("file", file);

    // Perform the PUT request
    const response = await fetch(`${BASE_URL}/upload`, {
      method: "PUT",
      body: formData,
    });

    // Check if the response is successful
    if (!response.ok) {
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    // Notify the user of success
    alert("Photo uploaded successfully!");
  } catch (error) {
    console.error("Error during photo upload:", error);
    alert("An error occurred while uploading the photo. Please try again.");
  }
}

// Event listeners for user interactions
document.getElementById("search-form").addEventListener("submit", event => {
  event.preventDefault();
  const query = document.getElementById("search-input").value;
  searchPhotos(query);
});

document.getElementById("upload-form").addEventListener("submit", event => {
  event.preventDefault();
  const fileInput = document.getElementById("file-input");
  const file = fileInput.files[0];
  uploadPhoto(file);
});
