// Base URL for the API Gateway
const BASE_URL = "https://ewpydj27fe.execute-api.us-east-1.amazonaws.com/dev";

// Function to search for photos based on a query
async function searchPhotos(query) {
  try {
    console.log("Starting searchPhotos function...");
    if (!query) {
      console.warn("No search query provided.");
      alert("Please enter a search query!");
      return;
    }

    // Construct the search URL
    const url = `${BASE_URL}/search?q=${encodeURIComponent(query)}`;
    console.log(`Search URL constructed: ${url}`);
    
    // Perform the GET request
    console.log("Sending GET request to the API...");
    const response = await fetch(url);
    console.log(`Received response: ${response.status} - ${response.statusText}`);

    // Check if the response is successful
    if (!response.ok) {
      console.error("Failed response from API:", response);
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    // Parse the JSON response
    console.log("Parsing response JSON...");
    const data = await response.json();
    console.log("Search results received:", data);

    // Handle search results
    displaySearchResults(data.results);
  } catch (error) {
    console.error("Error during photo search:", error);
    alert("An error occurred while searching for photos. Please try again.");
  }
}

// Function to display search results
function displaySearchResults(results) {
  console.log("Starting displaySearchResults function...");
  const resultsContainer = document.getElementById("results");
  resultsContainer.innerHTML = ""; // Clear previous results

  if (results.length === 0) {
    console.warn("No photos found for the given query.");
    resultsContainer.innerHTML = "<p>No photos found for the query.</p>";
    return;
  }

  console.log(`Displaying ${results.length} photo(s)...`);
  results.forEach(photo => {
    console.log("Processing photo:", photo);

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
    console.log("Starting uploadPhoto function...");
    if (!file) {
      console.warn("No photo selected for upload.");
      alert("Please select a photo to upload!");
      return;
    }

    // Fetch custom labels
    const customLabels = document.getElementById("customLabels").value;

    // Create a FormData object for multi-part upload
    const formData = new FormData();
    formData.append("file", file);
    formData.append("customLabels", customLabels);
    console.log("FormData prepared for upload with custom labels:", customLabels);

    // Perform the PUT request
    console.log("Sending PUT request to the API...");
    const response = await fetch(`${BASE_URL}/upload`, {
      method: "PUT",
      body: formData,
    });
    console.log(`Received response: ${response.status} - ${response.statusText}`);

    // Check if the response is successful
    if (!response.ok) {
      console.error("Failed response from API:", response);
      throw new Error(`Error: ${response.status} - ${response.statusText}`);
    }

    console.log("Photo uploaded successfully!");
    alert("Photo uploaded successfully!");
  } catch (error) {
    console.error("Error during photo upload:", error);
    alert("An error occurred while uploading the photo. Please try again.");
  }
}

// Validate DOM elements on page load
console.log("Validating DOM elements...");
const uploadForm = document.getElementById("uploadForm");
const photoInput = document.getElementById("photoInput");
const customLabelsInput = document.getElementById("customLabels");
const searchForm = document.getElementById("searchForm");
const searchQueryInput = document.getElementById("searchQuery");
const resultsContainer = document.getElementById("results");

if (!uploadForm || !photoInput || !customLabelsInput || !searchForm || !searchQueryInput || !resultsContainer) {
  console.error("One or more DOM elements could not be found.");
} else {
  console.log("All required DOM elements are present.");
}

// Event listeners for user interactions
document.getElementById("searchForm").addEventListener("submit", event => {
  event.preventDefault();
  const query = document.getElementById("searchQuery").value;
  console.log(`Search form submitted with query: ${query}`);
  searchPhotos(query);
});

document.getElementById("uploadForm").addEventListener("submit", event => {
  event.preventDefault();
  const fileInput = document.getElementById("photoInput");
  const file = fileInput.files[0];
  console.log(`Upload form submitted with file: ${file?.name}`);
  uploadPhoto(file);
});
