  var items = [];
  var items2 = {};

$( document ).ready(function() {
  var $overlay = $('<div id="overlay"></div>');
  var $large_card = $("#large_card")
  // //An image to overlay
  $overlay.append($large_card);
  //Add overlay
  $("body").append($overlay);
  //Capture the click event on a link to an image
  $(".small_image").click(function(event){
    event.preventDefault();
    $overlay.show()
    var path = $(this).find("img").attr("src");
    var id = $(this).find("img").attr("id")
    //request json metadata file
    $.ajax ({
      url: '../metadata/'+id+'.json',
      dataType: 'json',
      cache: false,
      success: function(data) {
        $.each( data, function( key, val ) {
          items.push(key, val);
        });

        for (var i = 0, length = items.length; i < length; i += 2) {
          items2[items[i]] = items[i+1];
        var upload_date = new Date(items2["timestamp"]*1000)

        }
        //update dom elements
        $("#large_user").html("Uploaded by <a href=../"+ items2["username"]+">"+items2["username"]+"</a>");
        $("#large_image").attr("src", path);
        $("#card_title").text(items2["filename"].slice(items2["filename"].indexOf('.')+1));
        $("#uploaded_date").text("Uploaded on " + upload_date);
        $("#large_tag").html("<a href=../tag/"+items2["tag"].slice(1)+">"+items2["tag"]+"</a>");
        $("#large_user").html("Uploaded by <a href=../"+ items2["username"]+">"+items2["username"]+"</a>");

        if (items2["comments"]) {
          for (i=0;i<items2["comments"].length;i+=1) {
            $("#comments").append("<h3>"+items2["comments"][i]["comment_user"]+"</h3>"+"<p>"+items2["comments"][i]["comment"]+"</p><hr>")
        }
      }
    }
  });


//large image buttons to add filters and close overlay
  $("#close-overlay").click(function(event){
    location.reload();
  });
  $("#sepia").click(function(event){
    $("#large_image").css("-webkit-filter", "sepia(100%)")
  });
  $("#grayscale").click(function(event){
    $("#large_image").css("-webkit-filter", "grayscale(100%)")
  });
    $("#invert").click(function(event){
    $("#large_image").css("-webkit-filter", "invert(100%)")
  });
    $("#clear").click(function(event){
    $("#large_image").css("-webkit-filter", "none")
  });

  //add new comments to large image
  $("#comment_form").submit(function(evt) {
  evt.preventDefault();
  var form = $(this)
  form.append('<input type="hidden" name="file_id" value='+id+' /> ');
  var post_url = form.attr('action');
  var post_data = form.serialize();
  //add spinner
    $.ajax({
        type: 'POST',
        url: post_url,
        data: post_data,
        success: function(msg) {
          $(form).load();
        }
      });
    window.location.reload(true);
    });
  
  });

});

