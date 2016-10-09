
//client side file extension and file size validation
function validate_files() {
  var input = document.getElementById('file');
  for (var i=0; i<input.files.length; i++) {
    var ext = input.files[i].name.substring(input.files[i].name.lastIndexOf('.')+1).toLowerCase()
    if (!((ext == 'jpg') || (ext == 'jpeg') || (ext == 'png') || (ext == 'tiff') || (ext == 'gif')))   {
      $("#msg").text("File Type(s) NOT Supported");
      document.getElementById("file").value ="";
      return false;
    }
    var s = input.files[i].size;
    if (s > 5 * 1024 * 1024) {
      $("#msg").text("File Too Large");
      document.getElementById("file").value ="";
      return false;
    }
  }
};


// when adding new comments to large image, 
// both username and comment text must be entered for submit button to be active
$('#comment_username, #write_comment').bind('keyup', function () {
  if (allFilled()) $('#submit_comment').removeAttr('disabled')
});
function allFilled() {
  var filled = true;
  $('body input').each(function() {
    if($(this).val() == '') filled = false;
  });
  return filled;
}

