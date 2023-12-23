const reactions = document.getElementsByClassName('reactions');
for (let item of reactions) {
    const [likeButton, rating, dislikeButton] = item.children;
    likeButton.addEventListener('click', () => {
        const formData = new FormData();
        if (likeButton.parentElement.classList.contains('question-reactions')) {
            formData.append('content_type', 'question')
        } else if (likeButton.parentElement.classList.contains('answer-reactions')) {
            formData.append('content_type', 'answer')
        }
        formData.append('id', likeButton.dataset.id)
        formData.append('reaction_type', 'Like')

        const request = new Request('/reaction', {
            method: "POST",
            body: formData
        });

        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                rating.innerHTML = data.counter
            });
        
        likeButton.classList.toggle('toggled-reaction')
        if (dislikeButton.classList.contains('toggled-reaction')) {
            dislikeButton.classList.remove('toggled-reaction')
        }
    })

    dislikeButton.addEventListener('click', () => {
        const formData = new FormData();
        if (likeButton.parentElement.classList.contains('question-reactions')) {
            formData.append('content_type', 'question')
        } else if (likeButton.parentElement.classList.contains('answer-reactions')) {
            formData.append('content_type', 'answer')
        }
        formData.append('id', dislikeButton.dataset.id)
        formData.append('reaction_type', 'Dislike')

        const request = new Request('/reaction', {
            method: "POST",
            body: formData
        });

        fetch(request)
            .then((response) => response.json())
            .then((data) => {
                rating.innerHTML = data.counter
            });
        
        dislikeButton.classList.toggle('toggled-reaction')
        if (likeButton.classList.contains('toggled-reaction')) {
            likeButton.classList.remove('toggled-reaction')
        }
    })
}

const is_correct_checkboxes = document.getElementsByClassName('is_correct');
for (checkbox of is_correct_checkboxes) {
    checkbox.addEventListener('change', (event) => {
        const current_checkbox = event.target;
        const formData = new FormData();
        formData.append('id', current_checkbox.dataset.id)

        const request = new Request('/correctanswer', {
            method: "POST",
            body: formData
        });

        fetch(request)
            .then((response) => response.json())
            .then((data) => {})
    })
}