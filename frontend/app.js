const API_URL = "http://127.0.0.1:8000/ask";


const form = document.getElementById("ask-form");
const questionInput = document.getElementById("question");
const askButton = document.getElementById("ask-button");

const loading = document.getElementById("loading");
const errorBox = document.getElementById("error");

const answerSection = document.getElementById("answer-section");
const answerBox = document.getElementById("answer");

const sourcesSection = document.getElementById("sources-section");
const sourcesBox = document.getElementById("sources");


form.addEventListener("submit", async function (event) {

    event.preventDefault();

    const question = questionInput.value.trim();

    clearError();

    if (!question) {

        showError("Please enter a question.");

        return;
    }


    setLoading(true);


    try {

        const response = await fetch(
            API_URL,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: question
                })
            }
        );


        const data = await response.json();


        if (!response.ok) {

            throw new Error(
                data.detail ||
                "Unable to process the question."
            );
        }


        displayAnswer(data);

    }
    catch (error) {

        console.error(error);

        showError(
            "Unable to connect to the HR Policy API. "
            + "Make sure the FastAPI server is running."
        );

    }
    finally {

        setLoading(false);

    }

});


function setLoading(isLoading) {

    askButton.disabled = isLoading;

    loading.classList.toggle(
        "hidden",
        !isLoading
    );

}


function clearError() {

    errorBox.textContent = "";

    errorBox.classList.add("hidden");

}


function showError(message) {

    errorBox.textContent = message;

    errorBox.classList.remove("hidden");

}


function displayAnswer(data) {

    answerSection.classList.remove("hidden");

    answerBox.textContent = data.answer || "No answer returned.";


    sourcesBox.innerHTML = "";


    if (
        Array.isArray(data.sources) &&
        data.sources.length > 0
    ) {

        sourcesSection.classList.remove("hidden");


        data.sources.forEach(function (source) {

            const item = document.createElement("div");

            item.className = "source-item";


            const fileName = document.createElement("div");

            fileName.className = "source-file";

            fileName.textContent =
                source.source || "Unknown source";


            const details = document.createElement("div");

            details.className = "source-details";

            details.textContent =
                `Page: ${source.page ?? "N/A"} | ` +
                `Chunk: ${source.chunk_index ?? "N/A"} | ` +
                `FAISS Score: ${formatScore(source.score)} | ` +
                `Rerank Score: ${formatScore(source.rerank_score)}`;


            item.appendChild(fileName);

            item.appendChild(details);

            sourcesBox.appendChild(item);

        });

    }
    else {

        sourcesSection.classList.add("hidden");

    }

}


function formatScore(value) {

    if (typeof value !== "number") {

        return "N/A";
    }

    return value.toFixed(4);

}