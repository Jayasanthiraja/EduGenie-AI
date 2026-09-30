const $ = (id) =>
  document.getElementById(id);


function showResult(id, text) {

  const el = $(id);

  el.classList.remove("hidden");

  el.textContent = text;
}


function setLoading(form, loading) {

  const button =
    form.querySelector(
      "button[type='submit']"
    );

  if (!button) return;


  if (loading) {

    button.dataset.original =
      button.textContent;

    button.textContent =
      "Thinking...";

    button.disabled = true;

  } else {

    button.textContent =
      button.dataset.original ||
      "Submit";

    button.disabled = false;
  }
}


function toast(message) {

  const el = $("toast");

  el.textContent = message;

  el.classList.add("show");

  setTimeout(
    () =>
      el.classList.remove("show"),
    3200
  );
}


async function api(
  url,
  options = {}
) {

  const response =
    await fetch(
      url,
      {
        headers: {
          "Content-Type":
            "application/json",

          ...(options.headers || {})
        },

        ...options
      }
    );


  let data;

  try {

    data =
      await response.json();

  } catch {

    data = {};

  }


  if (!response.ok) {

    throw new Error(
      data.detail ||
      "Request failed."
    );

  }


  return data;
}


async function loadHealth() {

  try {

    const data =
      await api(
        "/api/health"
      );


    const badge =
      $("statusBadge");


    badge.textContent =
      data.gemini_configured
        ? `AI ready · ${data.model}`
        : "Add Gemini API key";


    badge.style.color =
      data.gemini_configured
        ? "#15803d"
        : "#b45309";


    badge.style.background =
      data.gemini_configured
        ? "#f0fdf4"
        : "#fffbeb";


  } catch {

    $("statusBadge").textContent =
      "Backend unavailable";

  }
}



$("qaForm")
  .addEventListener(
    "submit",
    async (event) => {

      event.preventDefault();

      const form =
        event.currentTarget;

      setLoading(
        form,
        true
      );


      try {

        const question =
          $("question")
            .value
            .trim();


        const data =
          await api(
            `/api/qa?question=${encodeURIComponent(question)}`
          );


        showResult(
          "qaResult",
          data.answer
        );


      } catch (error) {

        toast(
          error.message
        );


      } finally {

        setLoading(
          form,
          false
        );

      }

    }
  );



$("explainForm")
  .addEventListener(
    "submit",
    async (event) => {

      event.preventDefault();

      const form =
        event.currentTarget;

      setLoading(
        form,
        true
      );


      try {

        const data =
          await api(
            "/api/explain",
            {
              method: "POST",

              body:
                JSON.stringify({
                  topic:
                    $("topic")
                      .value
                      .trim()
                })
            }
          );


        showResult(
          "explainResult",
          data.explanation
        );


      } catch (error) {

        toast(
          error.message
        );


      } finally {

        setLoading(
          form,
          false
        );

      }

    }
  );



$("summaryForm")
  .addEventListener(
    "submit",
    async (event) => {

      event.preventDefault();

      const form =
        event.currentTarget;

      setLoading(
        form,
        true
      );


      try {

        const data =
          await api(
            "/api/summarize",
            {
              method: "POST",

              body:
                JSON.stringify({
                  text:
                    $("summaryText")
                      .value
                      .trim()
                })
            }
          );


        showResult(
          "summaryResult",
          data.summary
        );


      } catch (error) {

        toast(
          error.message
        );


      } finally {

        setLoading(
          form,
          false
        );

      }

    }
  );



function renderQuiz(items) {

  const root =
    $("quizResult");


  root.innerHTML = "";

  root.classList.remove(
    "hidden"
  );


  items.forEach(
    (item, index) => {

      const wrapper =
        document.createElement(
          "div"
        );

      wrapper.className =
        "quiz-question";


      const title =
        document.createElement(
          "h3"
        );

      title.textContent =
        `Q${index + 1}. ${item.question}`;


      wrapper.appendChild(
        title
      );


      const name =
        `q-${index}`;


      item.options.forEach(
        (option) => {

          const label =
            document.createElement(
              "label"
            );

          label.className =
            "option";


          label.innerHTML =
            `<input type="radio" name="${name}" value="">
             <span></span>`;


          label
            .querySelector("input")
            .dataset.answer =
            option;


          label
            .querySelector("span")
            .textContent =
            option;


          wrapper.appendChild(
            label
          );

        }
      );


      const check =
        document.createElement(
          "button"
        );


      check.className =
        "check-btn";


      check.textContent =
        "Check Answer";


      const feedback =
        document.createElement(
          "div"
        );


      feedback.className =
        "quiz-feedback";


      check.addEventListener(
        "click",
        () => {

          const selected =
            wrapper.querySelector(
              `input[name="${name}"]:checked`
            );


          wrapper
            .querySelectorAll(
              ".option"
            )
            .forEach(
              (opt) =>
                opt.classList.remove(
                  "correct",
                  "wrong"
                )
            );


          if (!selected) {

            feedback.textContent =
              "Select an answer first.";

            return;
          }


          const chosen =
            selected.dataset.answer;


          if (
            chosen ===
            item.answer
          ) {

            selected
              .closest(".option")
              .classList.add(
                "correct"
              );


            feedback.textContent =
              "✓ Correct!";

          } else {

            selected
              .closest(".option")
              .classList.add(
                "wrong"
              );


            feedback.textContent =
              `✗ Incorrect. Correct answer: ${item.answer}`;
          }

        }
      );


      wrapper.appendChild(
        check
      );

      wrapper.appendChild(
        feedback
      );


      root.appendChild(
        wrapper
      );

    }
  );

}



$("quizForm")
  .addEventListener(
    "submit",
    async (event) => {

      event.preventDefault();

      const form =
        event.currentTarget;

      setLoading(
        form,
        true
      );


      try {

        const data =
          await api(
            "/api/quiz",
            {
              method: "POST",

              body:
                JSON.stringify({
                  text:
                    $("quizText")
                      .value
                      .trim(),

                  count:
                    Number(
                      $("quizCount")
                        .value
                    )
                })
            }
          );


        renderQuiz(
          data.quiz
        );


      } catch (error) {

        toast(
          error.message
        );


      } finally {

        setLoading(
          form,
          false
        );

      }

    }
  );



$("recommendForm")
  .addEventListener(
    "submit",
    async (event) => {

      event.preventDefault();

      const form =
        event.currentTarget;

      setLoading(
        form,
        true
      );


      try {

        const data =
          await api(
            "/api/recommendations",
            {
              method: "POST",

              body:
                JSON.stringify({
                  topic:
                    $("recommendTopic")
                      .value
                      .trim()
                })
            }
          );


        showResult(
          "recommendResult",
          data.recommendations
        );


      } catch (error) {

        toast(
          error.message
        );


      } finally {

        setLoading(
          form,
          false
        );

      }

    }
  );


loadHealth();