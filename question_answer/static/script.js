document.addEventListener('DOMContentLoaded', function() {
    // Get the form element
    var form = document.querySelector('form');

    // Add an event listener to the form submit event
    form.addEventListener('submit', function(event) {
        // Prevent the default form submission behavior
        event.preventDefault();

        // Hide the form
        form.style.display = 'none';

        // Show the results section
        var resultsSection = document.querySelector('section');
        resultsSection.style.display = 'block';
    });
});
