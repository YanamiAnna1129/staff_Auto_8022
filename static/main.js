$(document).ready(function() {
    $(".main h1").hover(
        function() {
            $(this).addClass("glass");
        },
        function() {
            $(this).removeClass("glass");
        }
    );
});