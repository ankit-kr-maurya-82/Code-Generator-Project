const button = document.getElementById("generateBtn");
const promptInput = document.getElementById("prompt");
const result = document.getElementById("result");

button.addEventListener("click", async () => {
    const prompt = promptInput.value.trim();

    if (!prompt) {
        result.textContent = "Please enter a prompt first.";
        promptInput.focus();
        return;
    }

    button.disabled = true;
    result.textContent = "Generating...";

    try {
        const response = await fetch("/generate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ prompt })
        });

        const data = await response.json();

        if (!response.ok) {
            result.textContent = data.detail || "Something went wrong.";
            return;
        }

        result.textContent = data.response;
    } catch (error) {
        result.textContent = "Could not reach the server. Please try again.";
    } finally {
        button.disabled = false;
    }
});
