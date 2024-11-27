// Initialize the API Gateway client
const apigClient = apigClientFactory.newClient({
    apiKey: "lg7EhEXNLK5FGLg0mXw8W2nP0sbIp6bTa2GrX0Zo", 
  });  

// Function to search for photos based on a query
async function searchPhotos(query) {
  try {
    if (!query) {
      console.warn("No search query provided.");
      alert("Please enter a search query!");
      return;
    }

    const params = { q: query };
    console.log("Params being sent:", params);
    const additionalParams = {};
    const response = await apigClient.searchGet(params, null, additionalParams);

    console.log("Search results received:", response);

    // Parse the body if it's a string
    let responseBody = response.data.body;
    if (typeof responseBody === "string") {
      responseBody = JSON.parse(responseBody); // Parse the JSON string
    }

    console.log("Parsed response body:", responseBody);

    // Check if results exist
    if (responseBody.results && responseBody.results.length > 0) {
      displaySearchResults(responseBody.results); // Call the display function
    } else {
      console.warn("No results found in API response:", responseBody);
      alert("No photos found for the given query.");
    }
  } catch (error) {
    console.error("Error during photo search:", error);
    alert("An error occurred while searching for photos. Please try again.");
  }
}

function displaySearchResults(results) {
  const resultsContainer = document.getElementById("results");

  // Clear any previous results
  resultsContainer.innerHTML = "";

  // Check if results are valid
  if (!results || results.length === 0) {
    console.warn("No photos found for the given query.");
    resultsContainer.innerHTML = "<p>No photos found for the given query.</p>";
    return;
  }

  // Loop through results and display each photo
  results.forEach(result => {
    if (result.url) {
      // Create an image element
      const img = document.createElement("img");
      img.src = result.url; // Use the pre-signed URL for the image
      img.alt = "Search Result";
      img.style.margin = "10px";
      img.style.maxWidth = "200px";
      img.style.maxHeight = "200px";

      // Create a label container
      const labelContainer = document.createElement("div");
      labelContainer.innerText = `Labels: ${result.labels.join(", ")}`;
      labelContainer.style.fontSize = "14px";

      // Create a wrapper for the image and labels
      const wrapper = document.createElement("div");
      wrapper.style.border = "1px solid #ccc";
      wrapper.style.padding = "10px";
      wrapper.style.marginBottom = "10px";
      wrapper.appendChild(img);
      wrapper.appendChild(labelContainer);

      // Append the wrapper to the results container
      resultsContainer.appendChild(wrapper);
    } else {
      console.warn("Result does not contain a valid URL:", result);
    }
  });
}

// Function to upload a photo
async function uploadPhoto(file) {
  try {
    if (!file) {
      console.warn("No photo selected for upload.");
      alert("Please select a photo to upload!");
      return;
    }

    // Fetch custom labels
    const customLabels = document.getElementById("customLabels").value;

    // Prepare request headers and body
    const additionalParams = {
      headers: {
        "Content-Type": "multipart/form-data",
        "x-amz-meta-customLabels": customLabels,
      },
    };

    const formData = new FormData();
    formData.append("file", file);

    const response = await apigClient.uploadPut({}, formData, additionalParams);

    console.log("Photo uploaded successfully:", response.data);
    alert("Photo uploaded successfully!");
  } catch (error) {
    console.error("Error during photo upload:", error);
    alert("An error occurred while uploading the photo. Please try again.");
  }
}

// Validate DOM elements on page load
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


