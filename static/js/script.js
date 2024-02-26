function showLoadingMessage() {
    document.getElementById('loadingMessage').style.display = 'flex';
}

document.addEventListener('DOMContentLoaded', function() {
    document.querySelector('form').addEventListener('submit', function(e) {
        showLoadingMessage();
    });
});
