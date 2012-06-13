function search_submit() {

    // Get the query string from the text field in the search form.
    var query = $("#id_query").val();

    // Get the search results from the search view and insert them
    // into the #search-results div.
    $("#search-results").load(
        // This URL invokes the search page view and passes it
        // the GET variables 'ajax' and 'query'.
        "/search/?ajax&query=" + encodeURIComponent(query)
    );

    // Tell the browser not to submit the form after calling our handler.
    return false;
}

$(document).ready(function() {
    $("#search-form").submit(search_submit);
});
