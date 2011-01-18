<script>
$(document).ready(function() {
	$('#admin-bar li.right.search a').mouseenter(function() {
		$('#admin-bar li.right.search .sub').css({'display':'block','right':'20px','left':'auto'});
		var enterText = $(this).html();
		$(this).text('Close Search');
	});
	$('#admin-bar li.right.search a').click(function() {
		$('#admin-bar li.right.search .sub').css('display','none');
		var exitText = $(this).html();
		$(this).text('Search');
	});
});
</script>