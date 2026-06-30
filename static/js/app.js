const form = document.getElementById("promptForm");
const button = document.getElementById("generateBtn");
const promptInput = document.getElementById("prompt");
const result = document.getElementById("result");
const charCount = document.getElementById("charCount");
const copyButton = document.getElementById("copyBtn");
const chips = document.querySelectorAll(".chip");

const setResult = (message, isError = false, canCopy = true) => {
    result.textContent = message;
    result.classList.toggle("is-error", isError);
    copyButton.disabled = !canCopy || isError || !message || message === "Output will appear here...";
};

const updateCount = () => {
    const count = promptInput.value.length;
    charCount.textContent = `${count.toLocaleString()} ${count === 1 ? "char" : "chars"}`;
};

promptInput.addEventListener("input", updateCount);

chips.forEach((chip) => {
    chip.addEventListener("click", () => {
        promptInput.value = chip.dataset.prompt;
        promptInput.focus();
        updateCount();
    });
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const prompt = promptInput.value.trim();

    if (!prompt) {
        setResult("Please enter a prompt first.", true);
        promptInput.focus();
        return;
    }

    button.disabled = true;
    copyButton.disabled = true;
    setResult("Generating a clean answer...", false, false);

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
            setResult(data.detail || "Something went wrong.", true);
            return;
        }

        setResult(data.response || "No output was returned.");
    } catch (error) {
        setResult("Could not reach the server. Please try again.", true);
    } finally {
        button.disabled = false;
    }
});

copyButton.addEventListener("click", async () => {
    const text = result.textContent.trim();

    if (!text) {
        return;
    }

    if (navigator.clipboard) {
        await navigator.clipboard.writeText(text);
    }

    copyButton.textContent = "Copied";

    window.setTimeout(() => {
        copyButton.textContent = "Copy";
    }, 1400);
});

updateCount();
