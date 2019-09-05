$(document).ready(function() {
    $('#admin-bar li.right.search a').on("mouseenter", function() {
        $('#admin-bar li.right.search .sub').css({'display':'block','right':'20px','left':'auto'});
        var enterText = $(this).html();
        $(this).text('Close Search');
    });
    $('#admin-bar li.right.search a').on("click", function() {
        $('#admin-bar li.right.search .sub').css('display','none');
        var exitText = $(this).html();
        $(this).text('Search');
    });
    $('.edit-setting-link').on("click", function() {
       if ($('#admin-overlay').length == 0) {
           $('body').append('<div id="admin-overlay"></div>');}
       $('#admin-overlay').fadeIn(150);
       $(this).parent().parent().next().fadeIn(225);
    });
    $('#admin-overlay, .setting-header a').on("click",function() {
       $('.admin-edit-setting').fadeOut(225);
       $('#admin-overlay').fadeOut(150);
    });
});
