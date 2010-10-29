$(document).ready(function() {
	var slugit = new Slugify({
		input_element : 'input#id_title',
		slug_element : 'input#id_slug',
		submit_element : 'input[type="submit"]',
		help: false,
		limit : 150
	});
});
