// popup.js
document.addEventListener('DOMContentLoaded', function() {
  const currentDate = new Date().toLocaleDateString();
  document.getElementById('currentDate').textContent = currentDate;

  // Parse JD button
  document.getElementById('parseJD').addEventListener('click', async () => {
    try {
      let [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      
      const result = await chrome.scripting.executeScript({
        target: { tabId: tab.id },
        function: parseJobDescription,
      });

      const jd = result[0].result;
      if (jd) {
        document.getElementById('jobDescription').value = jd;
        showStatus('Job description parsed successfully', 'success');
      } else {
        showStatus('Could not parse job description automatically. Please copy and paste it manually.', 'warning');
      }
    } catch (error) {
      showStatus('Error parsing job description: ' + error.message, 'error');
    }
  });

  // Save button
  document.getElementById('save').addEventListener('click', async () => {
    const jd = document.getElementById('jobDescription').value;
    if (!jd) {
      showStatus('Please enter a job description', 'error');
      return;
    }

    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const data = {
        date: currentDate,
        jobLink: tab.url,
        jobDescription: jd
      };

      const response = await fetch('http://localhost:5000/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data)
      });

      if (response.ok) {
        showStatus('Job details saved successfully', 'success');
      } else {
        throw new Error('Failed to save job details');
      }
    } catch (error) {
      showStatus('Error saving job details: ' + error.message, 'error');
    }
  });

  // Generate PDFs button
  document.getElementById('generate').addEventListener('click', async () => {
    try {
      const response = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          jobDescription: document.getElementById('jobDescription').value
        })
      });

      if (response.ok) {
        showStatus('PDFs generated successfully', 'success');
      } else {
        throw new Error('Failed to generate PDFs');
      }
    } catch (error) {
      showStatus('Error generating PDFs: ' + error.message, 'error');
    }
  });
});

// Function to parse JD from page
function parseJobDescription() {
  // Common selectors for job descriptions
  const selectors = [
    '.job-description',
    '[data-test="job-description"]',
    '.description',
    '#job-details',
    // Add more selectors based on common job sites
  ];

  for (const selector of selectors) {
    const element = document.querySelector(selector);
    if (element) {
      return element.textContent.trim();
    }
  }

  // If no specific selector works, try to find the largest text block
  const textBlocks = Array.from(document.getElementsByTagName('p'))
    .map(p => ({ element: p, length: p.textContent.length }))
    .sort((a, b) => b.length - a.length);

  if (textBlocks.length > 0) {
    return textBlocks[0].element.textContent.trim();
  }

  return null;
}

function showStatus(message, type) {
  const status = document.getElementById('status');
  status.textContent = message;
  status.className = `status ${type}`;
  setTimeout(() => {
    status.textContent = '';
    status.className = 'status';
  }, 3000);
}