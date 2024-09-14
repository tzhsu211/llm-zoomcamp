document.addEventListener('DOMContentLoaded', function() {
    const questionForm = document.getElementById('question-form-element');
    const feedbackForm = document.getElementById('feedback-form-element');
    const askAnotherButton = document.getElementById('ask-another');

    questionForm.addEventListener('submit', function(event) {
        event.preventDefault(); // 防止表單的默認提交行為

        const question = document.getElementById('question').value;
        const vegan = document.getElementById('vegan').checked;

        // 執行 AJAX 請求
        fetch('/ask', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                question: question,
                vegan: vegan
            }),
        })
        .then(response => response.json())
        .then(data => {
            console.log('Success:', data);
            // 可以根據返回數據顯示結果
            showFeedback();
        })
        .catch((error) => {
            console.error('Error:', error);
        });
    });

    askAnotherButton.addEventListener('click', function() {
        showQuestion();
    });
});

function showFeedback() {
    document.getElementById('question-form').style.display = 'none';
    document.getElementById('feedback-form').style.display = 'block';
}

function showQuestion() {
    document.getElementById('feedback-form').style.display = 'none';
    document.getElementById('question-form').style.display = 'block';
}
