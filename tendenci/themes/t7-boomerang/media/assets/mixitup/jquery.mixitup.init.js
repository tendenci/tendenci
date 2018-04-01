function imgLoaded(img){	
	$(img).parent().addClass('loaded');
};

// ON DOCUMENT READY:

$(function(){
	
	// INSTANTIATE MIXITUP
	
	$('#Parks').mixitup({
		layoutMode: 'list', // Start in list mode (display: block) by default
		listClass: 'list', // Container class for when in list mode
		gridClass: 'grid', // Container class for when in grid mode
		effects: ['fade','blur'], // List of effects 
		listEffects: ['fade','rotateX'] // List of effects ONLY for list mode
	});
	
	// HANDLE LAYOUT CHANGES
	
	// Bind layout buttons to toList and toGrid methods:
	
	$('#ToList').on('click',function(){
		$('.button').removeClass('active');
		$(this).addClass('active');
		$('#Parks').mixitup('toList');
	});

	$('#ToGrid').on('click',function(){
		$('.button').removeClass('active');
		$(this).addClass('active');
		$('#Parks').mixitup('toGrid');
	});
	
	// HANDLE MULTI-DIMENSIONAL CHECKBOX FILTERING
	
	/* 	
	*	The desired behaviour of multi-dimensional filtering can differ greatly 
	*	from project to project. MixItUp's built in filter button handlers are best
	*	suited to simple filter operations, so we will need to build our own handlers
	*	for this demo to achieve the precise behaviour we need.
	*/
	
	var $filters = $('#Filters').find('li'),
		dimensions = {
			region: 'all', // Create string for first dimension
			recreation: 'all' // Create string for second dimension
		};
		
	// Bind checkbox click handlers:
	
	$filters.on('click',function(){
		var $t = $(this),
			dimension = $t.attr('data-dimension'),
			filter = $t.attr('data-filter'),
			filterString = dimensions[dimension];
			
		if(filter == 'all'){
			// If "all"
			if(!$t.hasClass('active')){
				// if unchecked, check "all" and uncheck all other active filters
				$t.addClass('active').siblings().removeClass('active');
				// Replace entire string with "all"
				filterString = 'all';	
			} else {
				// Uncheck
				$t.removeClass('active');
				// Emtpy string
				filterString = '';
			}
		} else {
			// Else, uncheck "all"
			$t.siblings('[data-filter="all"]').removeClass('active');
			// Remove "all" from string
			filterString = filterString.replace('all','');
			if(!$t.hasClass('active')){
				// Check checkbox
				$t.addClass('active');
				// Append filter to string
				filterString = filterString == '' ? filter : filterString+' '+filter;
			} else {
				// Uncheck
				$t.removeClass('active');
				// Remove filter and preceeding space from string with RegEx
				var re = new RegExp('(\\s|^)'+filter);
				filterString = filterString.replace(re,'');
			};
		};
		
		// Set demension with filterString
		dimensions[dimension] = filterString;
		
		// We now have two strings containing the filter arguments for each dimension:	
		console.info('dimension 1: '+dimensions.region);
		console.info('dimension 2: '+dimensions.recreation);
		
		/*
		*	We then send these strings to MixItUp using the filter method. We can send as
		*	many dimensions to MixitUp as we need using an array as the second argument
		*	of the "filter" method. Each dimension must be a space seperated string.
		*
		*	In this case, MixItUp will show elements using OR logic within each dimension and
		*	AND logic between dimensions. At least one dimension must pass for the element to show.
		*/
		
		$('#Parks').mixitup('filter',[dimensions.region, dimensions.recreation])			
	});

});