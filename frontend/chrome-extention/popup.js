document.addEventListener('DOMContentLoaded', function () {
  const currentDate = new Date().toLocaleDateString();
  document.getElementById('currentDate').textContent = currentDate;

  // Fetch and display stats when the popup loads
  fetchStats();

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

  document.getElementById('save').addEventListener('click', async () => {
    const jd = document.getElementById('jobDescription').value;
    const companyName = document.getElementById('companyName').value;
  
    if (!jd || !companyName) {
      showStatus('Please enter a job description and company name', 'error');
      return;
    }
  
    try {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const data = {
        date: new Date().toISOString().split('T')[0], // Use ISO format (YYYY-MM-DD)
        jobLink: tab.url,
        jobDescription: jd,
        companyName: companyName,
      };
  
      const response = await fetch('http://localhost:5000/save', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
      });
  
      if (response.ok) {
        showStatus('Job details saved successfully', 'success');
        fetchStats(); // Refresh stats after saving
      } else {
        const errorData = await response.json();
        throw new Error(errorData.message || 'Failed to save job details');
      }
    } catch (error) {
      showStatus('Error saving job details: ' + error.message, 'error');
    }
  });

 
  document.getElementById('generate').addEventListener('click', async () => {
    try {
      const companyName = document.getElementById('companyName').value;
      const jd = document.getElementById('jobDescription').value;
      
      if (!companyName || !jd) {
        showStatus('Company name and job description are required', 'error');
        return;
      }
  
      const response = await fetch('http://localhost:5000/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          companyName: companyName,
          jobDescription: jd
        })
      });
  
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = response.headers.get('Content-Disposition').split('filename=')[1];
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
        showStatus('Application package downloaded', 'success');
      } else {
        throw new Error('Failed to generate package');
      }
    } catch (error) {
      showStatus('Error generating package: ' + error.message, 'error');
    }
  });
});

async function fetchStats() {
  try {
    const response = await fetch('http://localhost:5000/stats');
    if (!response.ok) {
      throw new Error('Failed to fetch stats');
    }
    const data = await response.json();
    document.getElementById('totalJobs').textContent = data.total_jobs;
    document.getElementById('jobsToday').textContent = data.jobs_today;
  } catch (error) {
    console.error('Error fetching stats:', error);
    showStatus('Error fetching stats: ' + error.message, 'error');
  }
}

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
    .map((p) => ({ element: p, length: p.textContent.length }))
    .sort((a, b) => b.length - a.length);

  if (textBlocks.length > 0) {
    return textBlocks[0].element.textContent.trim();
  }

  return null;
}

// Function to show status messages
function showStatus(message, type) {
  const status = document.getElementById('status');
  status.textContent = message;
  status.className = `status ${type}`;
  setTimeout(() => {
    status.textContent = '';
    status.className = 'status';
  }, 3000);
}