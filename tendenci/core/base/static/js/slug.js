/* 
Slugify - Glen Zangirolami
usage: 
var slugit = new Slugify({
	input_element : 'string',
	slug_element : 'string',
	submit_element : 'string',
	limit : integer
});
*/
function Slugify(params) {
	var self = this;
	
	// set up the options
	self.limit = (params.limit == undefined ? 100: params.limit);
	self.help = (params.help == undefined ? true: params.help);

	// put all the elements in an object
	self.elements = {};
	self.elements.input = $(params.input_element);
	self.elements.slug = $(params.slug_element);
	self.elements.submit = $(params.submit_element);
	if (self.help) {
		self.elements.help = (params.help_element == undefined ? '': $(params.help_element));
	}
	
	// set up all the local variables
	self.slug = '';
	
	// set up the events
	self.events();
}

/* function to add the blur, keyup, and click events */
Slugify.prototype.events = function() {
	var self = this;

	$(self.elements.input).blur(function() {
		if (self.elements.slug.val().length == 0)
			self.render_slug();
			if (self.help)
				self.render_help();
	});

	// the keyup is debatable - personally I didn't like it
	//$(self.elements.input).keyup(function(){							  
	//		self.render_slug();
	//});

	$(self.elements.slug).blur(function(){
		self.render_slug_from_slug();
		if (self.help)
			self.render_help();
	});

	$(self.elements.submit).click(function(){
		if (self.elements.slug.val().length == 0) {
			slug = parse_slug(self.elements.input.val());
			self.elements.slug.val(slug);
		}
	});	
}

Slugify.prototype.parse_slug = function() {
	var self = this;
	var value = self.elements.input.val();
	
	value = value.replace(/[^\s\w\/]+/ig,'');
	value = value.replace(/[\s]+/ig,'-');
	value = value.toLowerCase()
	
	if (value.substr(value.length-1,value.length) == '-') value = value.substr(0,value.length-1);
	if (value.length > self.limit)
	{
		value = value.substr(0,self.limit);
		if (value.substr(self.limit-1,self.limit) == '-') value = value.substr(0,self.limit-1);
	}
	self.slug = value;
}

Slugify.prototype.parse_slug_from_slug = function() {
	var self = this;
	var value = self.elements.slug.val();
	
	value = value.replace(/[^\s\w\-\/]+/ig,'');
	value = value.replace(/[\s]+/ig,'-');
	value = value.toLowerCase()
	if (value.substr(value.length-1,value.length) == '-') value = value.substr(0,value.length-1);
	if (value.length > self.limit)
	{
		value = value.substr(0,self.limit);
		if (value.substr(self.limit-1,self.limit) == '-') value = value.substr(0,self.limit-1);
	}
	self.slug =  value;
}

Slugify.prototype.render_help = function() {
	var self = this;
	var help_text = '';
	var splits = self.elements.help.html().split('/');
	splits[splits.length-1] = self.slug;
	help_text = splits.join('/');
	self.elements.help.html(help_text);
}

Slugify.prototype.render_slug_from_slug = function() {
	var self = this;
	
	self.parse_slug_from_slug();
	self.elements.slug.val(self.slug);
}

Slugify.prototype.render_slug = function() {
	var self = this;
	
	self.parse_slug();
	self.elements.slug.val(self.slug);
}