function updateStorageValues() {
    chrome.storage.local.get(["lastUrl", "lastResult", "result"], data => {
        const urlEl = document.getElementById("url");
        const resEl = document.getElementById("result");

        // ---- URL ----
        urlEl.textContent = data.lastUrl
            ? `Last URL: ${data.lastUrl}`
            : "No URL checked yet.";

        // ---- RESULT ----
        // Try in order: data.lastResult, data.result
        let raw = data.lastResult ?? data.result;
        // If it’s an object like { result: "legitimate" }, unwrap it:
        let status = (raw && typeof raw === "object" && "result" in raw)
            ? raw.result
            : raw;

        console.log("Phishing status:", status);

        // ---- UPDATE UI ----
        if (status === "phishing") {
            resEl.textContent = "Phishing Detected";
            resEl.classList.add("phishing");
            resEl.classList.remove("legitimate");
        } else if (status === "legitimate") {
            resEl.textContent = "Legitimate Site";
            resEl.classList.add("legitimate");
            resEl.classList.remove("phishing");
        } else {
            resEl.textContent = "Unknown result";
            resEl.classList.remove("phishing", "legitimate");
        }
    });
}

// Poll every 2 seconds, and also run once immediately
setInterval(updateStorageValues, 500);
updateStorageValues();
