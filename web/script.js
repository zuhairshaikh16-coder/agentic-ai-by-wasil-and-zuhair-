/*
============================================================
script.js
============================================================

This file connects the HTML website to the FastAPI backend.

Flow:

    User types message
            ↓
       JavaScript
            ↓
       POST /chat
            ↓
         FastAPI
            ↓
        agent.py
            ↓
      OpenRouter + tools
            ↓
       Final response
            ↓
        JavaScript
            ↓
          HTML
============================================================
*/


// ============================================================
// ELEMENTS
// ============================================================

const messageInput =
    document.getElementById(
        "messageInput"
    );


const sendButton =
    document.getElementById(
        "sendButton"
    );


const chatMessages =
    document.getElementById(
        "chatMessages"
    );


const welcomeScreen =
    document.getElementById(
        "welcomeScreen"
    );


const newChatButton =
    document.getElementById(
        "newChatButton"
    );


// ============================================================
// SESSION
// ============================================================

/*
A session ID identifies the current conversation.

We store it in localStorage so refreshing the page
doesn't immediately create a new conversation.
*/

let sessionId =
    localStorage.getItem(
        "agent_session_id"
    );


if (!sessionId) {

    sessionId =
        crypto.randomUUID();

    localStorage.setItem(
        "agent_session_id",
        sessionId
    );

}


// ============================================================
// ADD MESSAGE TO UI
// ============================================================

function addMessage(
    text,
    sender
) {

    const message =
        document.createElement(
            "div"
        );


    message.className =
        `message ${sender}`;


    const content =
        document.createElement(
            "div"
        );


    content.className =
        "message-content";


    /*
    textContent is intentionally used instead
    of innerHTML.

    This prevents a user message or AI response
    from injecting arbitrary HTML into the page.
    */

    content.textContent =
        text;


    message.appendChild(
        content
    );


    chatMessages.appendChild(
        message
    );


    scrollToBottom();

}


// ============================================================
// TYPING INDICATOR
// ============================================================

function showTyping() {

    const message =
        document.createElement(
            "div"
        );


    message.id =
        "typingIndicator";


    message.className =
        "message assistant";


    message.innerHTML = `

        <div class="message-content typing">

            <span></span>
            <span></span>
            <span></span>

        </div>

    `;


    chatMessages.appendChild(
        message
    );


    scrollToBottom();

}


function hideTyping() {

    const typing =
        document.getElementById(
            "typingIndicator"
        );


    if (typing) {

        typing.remove();

    }

}


// ============================================================
// SCROLL
// ============================================================

function scrollToBottom() {

    chatMessages.scrollTop =
        chatMessages.scrollHeight;

}


// ============================================================
// SEND MESSAGE
// ============================================================

async function sendMessage() {

    const message =
        messageInput.value.trim();


    // Don't send empty messages

    if (!message) {

        return;

    }


    // Hide welcome screen

    if (welcomeScreen) {

        welcomeScreen.remove();

    }


    // Show user message

    addMessage(
        message,
        "user"
    );


    // Clear input

    messageInput.value = "";

    autoResize();


    // Disable send button

    sendButton.disabled = true;


    // Show typing

    showTyping();


    try {


        // ====================================================
        // CALL FASTAPI
        // ====================================================

        const response =
            await fetch(
                "/chat",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            session_id:
                                sessionId,

                            message:
                                message

                        })

                }
            );


        // ====================================================
        // PARSE RESPONSE
        // ====================================================

        const data =
            await response.json();


        // Remove typing indicator

        hideTyping();


        // ====================================================
        // HANDLE SERVER ERROR
        // ====================================================

        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Server returned an error."
            );

        }


        // ====================================================
        // SHOW AI RESPONSE
        // ====================================================

        addMessage(
            data.response,
            "assistant"
        );


    }

    catch (error) {

        console.error(
            "Chat error:",
            error
        );


        hideTyping();


        addMessage(
            "Sorry, something went wrong while communicating with the AI agent.",
            "assistant"
        );

    }


    // Enable send button again

    sendButton.disabled = false;

    messageInput.focus();

}


// ============================================================
// SEND BUTTON
// ============================================================

sendButton.addEventListener(
    "click",
    sendMessage
);


// ============================================================
// ENTER KEY
// ============================================================

messageInput.addEventListener(
    "keydown",
    function(event) {

        /*
        Enter sends the message.

        Shift + Enter creates a new line.
        */

        if (
            event.key === "Enter" &&
            !event.shiftKey
        ) {

            event.preventDefault();

            sendMessage();

        }

    }
);


// ============================================================
// AUTO RESIZE TEXTAREA
// ============================================================

function autoResize() {

    messageInput.style.height =
        "auto";


    messageInput.style.height =
        Math.min(
            messageInput.scrollHeight,
            150
        ) + "px";

}


messageInput.addEventListener(
    "input",
    autoResize
);


// ============================================================
// SUGGESTION BUTTONS
// ============================================================

document
    .querySelectorAll(
        ".suggestion"
    )
    .forEach(
        button => {

            button.addEventListener(
                "click",
                function() {

                    const message =
                        this.dataset.message;


                    messageInput.value =
                        message;


                    autoResize();


                    sendMessage();

                }
            );

        }
    );


// ============================================================
// NEW CHAT
// ============================================================

newChatButton.addEventListener(
    "click",
    async function() {


        try {

            // Tell backend to forget old agent

            await fetch(
                "/clear",
                {

                    method: "POST",

                    headers: {

                        "Content-Type":
                            "application/json"

                    },

                    body:
                        JSON.stringify({

                            session_id:
                                sessionId

                        })

                }
            );

        }

        catch (error) {

            console.error(
                "Clear chat error:",
                error
            );

        }


        // ====================================================
        // CREATE NEW SESSION
        // ====================================================

        sessionId =
            crypto.randomUUID();


        localStorage.setItem(
            "agent_session_id",
            sessionId
        );


        // ====================================================
        // RESET CHAT
        // ====================================================

        chatMessages.innerHTML = `

            <div
                id="welcomeScreen"
                class="welcome"
            >

                <div class="welcome-icon">
                    🤖
                </div>

                <h2>
                    How can I help you?
                </h2>

                <p>
                    I'm an agentic AI that can
                    reason, use tools, and work
                    toward your request.
                </p>

            </div>

        `;

    }
);
