function bookmark_edit() {
    // This refers to the "[edit]" link.
    // .parent refers to the enclosing <li> element.
    var item = $(this).parent();
    // Get the bookmark's actual URL from the href property.
    var url = item.find(".title").attr("href");
    // Replace the bookmark's HTML with an edit form.
    item.load(
        "/save/?ajax&url=" + encodeURIComponent(url),
        null,
        // Execute this function after load runs.
        // It will attach the bookmark_save() function below
        // to the form.
        function() {
            $("#save-form").submit(bookmark_save);
        }
    );
    // Tell the browser not to follow the edit link.
    return false;
}

// Attach the bookmark_edit function defined above to the
// event of clicking an edit link.
$(document).ready(function() {
    $("ul.bookmarks .edit").click(bookmark_edit);
});


function bookmark_save() {
    // Get the <li> element.
    var item = $(this).parent();
    // Get the updated data from the form.
    var data = {
        url  : item.find("#id_url").val(),
        title: item.find("#id_title").val(),
        tags : item.find("#id_tags").val()
    };
    // POST the data to the server.
    // Arg 1 = URL to post to
    // Arg 2 = dictionary of data to post
    // Arg 3 = function to invoke after the POST
    $.post("/save/?ajax", data, function(result) {
        // If POST succeeds...
        if (result != "failure") {  
            // insert new bookmark before the old one and...
            item.before($("li", result).get(0));  // .get(0) => extract the first list element
            // remove the old bookmark.
            item.remove();  
            // Re-attach edit function to new edit link.
            $("ul.bookmarks .edit").click(bookmark_edit);
        }
        else {
            // Display alert box.
            alert("Failed to validate bookmark before saving.");
        }
    });
    
    return false;
}

