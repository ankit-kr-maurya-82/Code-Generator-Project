const form = document.getElementById("promptForm");
const generateButton = document.getElementById("generateBtn");
const promptInput = document.getElementById("prompt");
const chatThread = document.getElementById("chatThread");
const emptyState = document.getElementById("emptyState");
const charCount = document.getElementById("charCount");
const historyToggle = document.getElementById("historyToggle");
const historyPanel = document.getElementById("historyPanel");
const historyList = document.getElementById("historyList");
const historyEmpty = document.getElementById("historyEmpty");
const clearHistoryButton = document.getElementById("clearHistoryBtn");
const chips = document.querySelectorAll(".chip");
const historyStorageKey = "codeGeneratorHistory";
const maxHistoryItems = 20;

const copyText = async (text) => {
    if (!text.trim() || !navigator.clipboard) {
        return;
    }

    await navigator.clipboard.writeText(text);
};

const scrollToBottom = () => {
    window.requestAnimationFrame(() => {
        chatThread.scrollTop = chatThread.scrollHeight;
    });
};

const createCodeBlock = (code, language = "code") => {
    const wrapper = document.createElement("div");
    wrapper.className = "code-copy-panel";

    const header = document.createElement("div");
    header.className = "code-copy-header";

    const label = document.createElement("span");
    label.textContent = language || "code";

    const copyButton = document.createElement("button");
    copyButton.className = "code-copy-button";
    copyButton.type = "button";
    copyButton.textContent = "Copy code";
    copyButton.addEventListener("click", async () => {
        await copyText(code);
        copyButton.textContent = "Copied";

        window.setTimeout(() => {
            copyButton.textContent = "Copy code";
        }, 1400);
    });

    const pre = document.createElement("pre");
    const codeElement = document.createElement("code");
    codeElement.textContent = code.trim();

    header.append(label, copyButton);
    pre.append(codeElement);
    wrapper.append(header, pre);

    return wrapper;
};

const sectionTitles = {
    result: "Result",
    code: "Code",
    explanation: "Explanation",
    libraries: "Required Libraries"
};

const sectionOrder = ["result", "code", "explanation", "libraries"];

const getSectionKey = (line) => {
    const match = line.match(/^\s*(?:#{1,4}\s*)?(?:\d+\.\s*)?(Result|Code|Explanation|Required Libraries|Required Library|Libraries)\s*:?\s*$/i);

    if (!match) {
        return null;
    }

    const value = match[1].toLowerCase();

    if (value === "required libraries" || value === "required library" || value === "libraries") {
        return "libraries";
    }

    return value;
};

const createSection = (title, items, key) => {
    const section = document.createElement("section");
    section.className = `response-section response-section-${key}`;

    const heading = document.createElement("h3");
    heading.textContent = title;
    section.appendChild(heading);

    if (!items.length) {
        const empty = document.createElement("div");
        empty.className = "response-section-body response-section-empty";
        empty.textContent = key === "code" ? "No code returned." : "No content returned.";
        section.appendChild(empty);
        return section;
    }

    items.forEach((item) => {
        if (item.type === "code") {
            section.appendChild(createCodeBlock(item.value, item.language));
            return;
        }

        if (!item.value.trim()) {
            return;
        }

        const body = document.createElement("div");
        body.className = "response-section-body";
        body.textContent = item.value.trim();
        section.appendChild(body);
    });

    return section;
};

const renderResult = (message, resultElement) => {
    resultElement.innerHTML = "";

    const sections = new Map();
    let currentKey = "result";
    let textBuffer = [];
    let codeLanguage = "";
    let codeBuffer = [];
    let isCode = false;

    const getItems = (key) => {
        if (!sections.has(key)) {
            sections.set(key, []);
        }

        return sections.get(key);
    };

    const flushText = () => {
        const value = textBuffer.join("\n").trim();

        if (value) {
            getItems(currentKey).push({ type: "text", value });
        }

        textBuffer = [];
    };

    message.split(/\r?\n/).forEach((line) => {
        const fenceMatch = line.match(/^\s*```([a-zA-Z0-9_+-]*)\s*$/);

        if (fenceMatch) {
            if (isCode) {
                getItems(currentKey).push({
                    type: "code",
                    value: codeBuffer.join("\n"),
                    language: codeLanguage || "code"
                });
                codeBuffer = [];
                codeLanguage = "";
                isCode = false;
                return;
            }

            flushText();
            isCode = true;
            codeLanguage = fenceMatch[1] || "code";
            currentKey = "code";
            return;
        }

        if (isCode) {
            codeBuffer.push(line);
            return;
        }

        const nextKey = getSectionKey(line);

        if (nextKey) {
            flushText();
            currentKey = nextKey;
            getItems(currentKey);
            return;
        }

        textBuffer.push(line);
    });

    if (isCode) {
        getItems("code").push({
            type: "code",
            value: codeBuffer.join("\n"),
            language: codeLanguage || "code"
        });
    }

    flushText();

    sectionOrder.forEach((key) => {
        const items = sections.get(key) || [];
        resultElement.appendChild(createSection(sectionTitles[key], items, key));
    });
};

const createUserMessage = (message) => {
    const row = document.createElement("article");
    row.className = "message-row message-row-user";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble user-bubble";
    bubble.textContent = message;

    row.appendChild(bubble);
    chatThread.appendChild(row);
    scrollToBottom();
};

const clearChatMessages = () => {
    chatThread.querySelectorAll(".message-row").forEach((row) => row.remove());
};

const createAssistantMessage = () => {
    const row = document.createElement("article");
    row.className = "message-row message-row-assistant";

    const avatar = document.createElement("div");
    avatar.className = "assistant-avatar";
    avatar.textContent = "AI";

    const bubble = document.createElement("div");
    bubble.className = "message-bubble assistant-bubble";

    const header = document.createElement("div");
    header.className = "output-header";

    const titleWrap = document.createElement("div");
    const label = document.createElement("span");
    label.className = "section-label";
    label.textContent = "AI response";

    const title = document.createElement("h2");
    title.textContent = "Generated Output";

    const actions = document.createElement("div");
    actions.className = "output-actions";

    const status = document.createElement("span");
    status.className = "response-status";
    status.textContent = "Ready";

    const copyButton = document.createElement("button");
    copyButton.className = "ghost-button";
    copyButton.type = "button";
    copyButton.disabled = true;
    copyButton.textContent = "Copy all";

    const result = document.createElement("div");
    result.className = "result is-empty";
    result.textContent = "Output will appear here...";

    const messageState = {
        text: ""
    };

    copyButton.addEventListener("click", async () => {
        const text = messageState.text.trim();

        if (!text) {
            return;
        }

        await copyText(text);
        copyButton.textContent = "Copied";

        window.setTimeout(() => {
            copyButton.textContent = "Copy all";
        }, 1400);
    });

    titleWrap.append(label, title);
    actions.append(status, copyButton);
    header.append(titleWrap, actions);
    bubble.append(header, result);
    row.append(avatar, bubble);
    chatThread.appendChild(row);
    scrollToBottom();

    return { result, status, copyButton, messageState };
};

const setAssistantResult = (message, elements, isError = false, canCopy = true) => {
    elements.messageState.text = message;
    elements.result.classList.toggle("is-error", isError);
    elements.result.classList.toggle("has-rich-output", !isError);
    elements.result.classList.toggle("is-empty", message === "Output will appear here...");
    elements.result.classList.toggle("is-loading", message === "Generating a clean answer...");
    elements.copyButton.disabled = !canCopy || isError || !message || message === "Output will appear here...";

    if (message === "Generating a clean answer...") {
        elements.status.textContent = "Generating";
    } else if (isError) {
        elements.status.textContent = "Needs attention";
    } else if (message === "Output will appear here...") {
        elements.status.textContent = "Ready";
    } else {
        elements.status.textContent = "Complete";
    }

    if (isError || message === "Output will appear here..." || message === "Generating a clean answer...") {
        elements.result.textContent = message;
        scrollToBottom();
        return;
    }

    renderResult(message, elements.result);
    scrollToBottom();
};

const updateCount = () => {
    const count = promptInput.value.length;
    charCount.textContent = `${count.toLocaleString()} ${count === 1 ? "char" : "chars"}`;
};

const readHistory = () => {
    try {
        const saved = JSON.parse(localStorage.getItem(historyStorageKey) || "[]");
        return Array.isArray(saved) ? saved : [];
    } catch (error) {
        return [];
    }
};

const writeHistory = (items) => {
    localStorage.setItem(historyStorageKey, JSON.stringify(items.slice(0, maxHistoryItems)));
};

const formatHistoryTime = (timestamp) => {
    return new Intl.DateTimeFormat(undefined, {
        month: "short",
        day: "numeric",
        hour: "numeric",
        minute: "2-digit"
    }).format(new Date(timestamp));
};

const closeHistory = () => {
    if (!historyPanel || !historyToggle) {
        return;
    }

    historyPanel.hidden = true;
    historyToggle.setAttribute("aria-expanded", "false");
};

const restoreHistoryItem = (item) => {
    clearChatMessages();
    emptyState.hidden = true;
    createUserMessage(item.prompt);

    const assistantMessage = createAssistantMessage();
    setAssistantResult(item.response, assistantMessage);
    closeHistory();
};

const renderHistory = () => {
    if (!historyList || !historyEmpty) {
        return;
    }

    const items = readHistory();
    historyList.innerHTML = "";
    historyEmpty.hidden = items.length > 0;

    items.forEach((item) => {
        const button = document.createElement("button");
        button.className = "history-item";
        button.type = "button";

        const title = document.createElement("span");
        title.className = "history-title";
        title.textContent = item.prompt;

        const time = document.createElement("span");
        time.className = "history-time";
        time.textContent = formatHistoryTime(item.createdAt);

        button.append(title, time);
        button.addEventListener("click", () => restoreHistoryItem(item));
        historyList.appendChild(button);
    });
};

const saveHistoryItem = (prompt, response) => {
    const items = readHistory();
    const nextItem = {
        id: `${Date.now()}-${Math.random().toString(36).slice(2)}`,
        prompt,
        response,
        createdAt: Date.now()
    };

    writeHistory([nextItem, ...items]);
    renderHistory();
};

const requiredElements = {
    form,
    promptInput,
    chatThread,
    emptyState,
    charCount,
    historyToggle,
    historyPanel,
    historyList,
    historyEmpty,
    clearHistoryButton
};

const missingElements = Object.entries(requiredElements)
    .filter(([, element]) => !element)
    .map(([name]) => name);

if (missingElements.length) {
    console.warn(`Code Generator UI is missing required element(s): ${missingElements.join(", ")}`);
} else {
    renderHistory();
    promptInput.addEventListener("input", updateCount);

    historyToggle.addEventListener("click", () => {
        const isOpening = historyPanel.hidden;
        historyPanel.hidden = !isOpening;
        historyToggle.setAttribute("aria-expanded", String(isOpening));
    });

    clearHistoryButton.addEventListener("click", () => {
        writeHistory([]);
        renderHistory();
    });

    chips.forEach((chip) => {
        chip.addEventListener("click", () => {
            promptInput.value = chip.dataset.prompt;
            promptInput.focus();
            updateCount();
        });
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const submitButton = form.querySelector('button[type="submit"]') || generateButton;
        const prompt = promptInput.value.trim();

        emptyState.hidden = true;

        if (!prompt) {
            const assistantMessage = createAssistantMessage();
            setAssistantResult("Please enter a prompt first.", assistantMessage, true);
            promptInput.focus();
            return;
        }

        createUserMessage(prompt);
        const assistantMessage = createAssistantMessage();
        if (submitButton) {
            submitButton.disabled = true;
        }
        setAssistantResult("Generating a clean answer...", assistantMessage, false, false);

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
                setAssistantResult(data.detail || "Something went wrong.", assistantMessage, true);
                return;
            }

            const responseText = data.response || "No output was returned.";
            setAssistantResult(responseText, assistantMessage);
            saveHistoryItem(prompt, responseText);
            promptInput.value = "";
            updateCount();
        } catch (error) {
            setAssistantResult("Could not reach the server. Please try again.", assistantMessage, true);
        } finally {
            if (submitButton) {
                submitButton.disabled = false;
            }
        }
    });

    updateCount();
}
