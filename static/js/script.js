let decryptedMessage = '';
var MAX_ATTEMPTS = 0;

async function checkKey() {
    try {
        const key = document.getElementById('key').value;
        const response = await fetch('/check_key', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({key: key})
        });

        if (!response.ok) {
            throw new Error('Network error');
        }

        const data = await response.json();
        
        let attempts = data.attempts;
        if(! (data.max_attempts === undefined)){
            MAX_ATTEMPTS = data.max_attempts
        }
        if(attempts === undefined){
            attempts = MAX_ATTEMPTS
        }

        document.querySelector('.attempts').textContent = 
            `Attempts: ${attempts}/${MAX_ATTEMPTS}`;
        
        if (data.success) {
            decryptedMessage = data.decrypted;
            document.querySelector('.message').textContent = data.decrypted;
            document.getElementById('copy-btn').style.display = 'inline-block';
            document.getElementById('submit-btn').disabled = true;
            document.getElementById('key').disabled = true;
        } else if (data.attempts >= MAX_ATTEMPTS) {
            document.getElementById('submit-btn').disabled = true;
            document.getElementById('key').disabled = true;
        }
    } catch (error) {
        showError('The host terminated the connection');
    }
}

async function fetchAttempts() {
    try {
        const response = await fetch('/get_attempts');
        if (!response.ok) {
            throw new Error('Ошибка сети');
        }
        const data = await response.json();
        let attempts = data.attempts;
        if(! (data.max_attempts === undefined)){
            MAX_ATTEMPTS = data.max_attempts
        }
        if(attempts === undefined){
            attempts = MAX_ATTEMPTS
        }

        document.querySelector('.attempts').textContent = 
            `Attempts: ${attempts}/${MAX_ATTEMPTS}`;
    } catch (error) {
        console.error('Error while fetching attempt count:', error);
    }
}

// Call the function on page load
window.onload = fetchAttempts;

async function copyToClipboard(textToCopy) {
    // Navigator clipboard api needs a secure context (https)
    if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(textToCopy);
    } else {
        // Use the 'out of viewport hidden text area' trick
        const textArea = document.createElement("textarea");
        textArea.value = textToCopy;
            
        // Move textarea out of the viewport so it's not visible
        textArea.style.position = "absolute";
        textArea.style.left = "-999999px";
            
        document.body.prepend(textArea);
        textArea.select();

        try {
            document.execCommand('copy');
        } catch (error) {
            console.error(error);
        } finally {
            textArea.remove();
        }
    }
}

async function copyText() {
    try {
        await copyToClipboard(decryptedMessage);
        alert('Text copied');

        // Send a signal to terminate the server
        const response = await fetch('/shutdown', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ word: decryptedMessage }) // Make sure uid is available here
        });

        if (!response.ok) {
            throw new Error('Server shutdown error');
        }
    } catch (error) {
        console.error('Ошибка:', error);
    }
}

function showError(message) {

    document.getElementById('submit-btn').disabled = true;
    document.getElementById('key').disabled = true;

    // Create an element for error message
    const errorDiv = document.createElement('div');
    errorDiv.style.position = 'fixed';
    errorDiv.style.top = '0';
    errorDiv.style.left = '0';
    errorDiv.style.right = '0';
    errorDiv.style.backgroundColor = 'rgba(200, 50, 50, 0.5)'; // Translucent red
    errorDiv.style.color = 'white';
    errorDiv.style.fontSize = '24px';
    errorDiv.style.textAlign = 'center';
    errorDiv.style.padding = '20px';
    errorDiv.innerText = message;

    // Add an element to the page
    document.body.appendChild(errorDiv);
}

// Update the error handler
window.addEventListener('error', function(event) {
    showError('');
});
