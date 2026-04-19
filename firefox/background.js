let activeTabId = null;
let currentController = null;
let currentUrl = null;
const API_BASE_URL = "__API_BASE_URL__";

function buildApiUrl(path) {
    return `${API_BASE_URL.replace(/\/$/, "")}${path}`;
}

/**
 * When the user changes tabs, set that as activeTabId, then fetch its URL.
 */
chrome.tabs.onActivated.addListener((activeInfo) => {
    // Abort the previous request if still in progress
    if (currentController) {
        currentController.abort();
    }
    currentController = null;
    currentUrl = null;

    // Update the activeTabId
    activeTabId = activeInfo.tabId;

    // Get the active tab's info, including its current URL
    chrome.tabs.get(activeInfo.tabId, (tab) => {
        if (tab && tab.url) {
            // Start fresh
            currentController = new AbortController();
            currentUrl = tab.url;
            checkUrlInBackground(tab.url, currentController.signal);
        }
    });
});

/**
 * When a tab is updated (navigates to a new URL, page reload, etc.):
 * Only act if it is the active tab, and we actually have a new URL.
 */
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    // If no new URL, do nothing
    if (!changeInfo.url) return;

    // Only process if the updated tab is the current active tab
    if (tabId !== activeTabId) return;

    // We have a new URL for the active tab; abort old request & start new
    if (currentController) {
        currentController.abort();
    }

    currentController = new AbortController();
    currentUrl = changeInfo.url;
    checkUrlInBackground(changeInfo.url, currentController.signal);
});

async function checkUrlInBackground(targetUrl, abortSignal) {
    try {
        const response = await fetch(buildApiUrl("/receive_url"), {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ url: targetUrl }),
            signal: abortSignal
        });

        if (!response.ok) {
            throw new Error("Network response was not ok: " + response.statusText);
        }

        const result = await response.json();
        const status = result.result;

        // Only store the result if it's still the correct/active URL
        if (targetUrl === currentUrl) {
            if (chrome.storage?.local?.set) {
                chrome.storage.local.set(
                    { lastUrl: targetUrl, lastResult: status },
                    () => {
                        console.log("Stored updated phishing check result:", targetUrl, status);
                    }
                );
            }
        } else {
            console.log("Ignoring outdated result for:", targetUrl);
        }
    } catch (error) {
        if (error.name === "AbortError") {
            console.log("Aborted request for:", targetUrl);
        } else {
            console.error("Error checking URL in background:", error);
        }
    }
}
