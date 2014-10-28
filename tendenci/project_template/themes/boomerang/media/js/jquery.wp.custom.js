$(document).ready(function() {
	// Active Theme: Select the theme you want to activate on the entire website
	$("body").addClass("wp-theme-1");
	
	// This sets the lw class on the .wrapper div. You can add this class manually on each page
	$(".wrapper").addClass("lw");
	
	//This function enables sticky navbar functionality. To make it work uncomment the next line
	//enableStickyNav();
	
	function enableStickyNav(){
		$(".navbar").sticky({ 
			topSpacing: 0 ,
			className: "navbar-fixed"
		});	
	}
	//Carousels
	$('.carousel').carousel({
		interval: 5000,
		pause	: 'hover'
	});
	// Sortable list
	$('#ulSorList').mixitup();
	// Fancybox
	$(".theater").fancybox();
	// Fancybox	
	$(".ext-source").fancybox({
		'transitionIn'		: 'none',
		'transitionOut'		: 'none',
		'autoScale'     	: false,
		'type'				: 'iframe',
		'width'				: '50%',
		'height'			: '60%',
		'scrolling'   		: 'no'
	});
	// Masonry
	var container = document.querySelector('#masonryWr');
	var msnry = new Masonry( container, {
	  itemSelector: '.item'
	});
	// Scroll to top
	$().UItoTop({ easingType: 'easeOutQuart' });
	// Inview animations
	$.fn.waypoint.defaults = {
		context: window,
		continuous: true,
		enabled: true,
		horizontal: false,
		offset: 300,
		triggerOnce: false
	}	
	$('.animate-in-view, .pie-chart').waypoint(function(direction) {
		var barColor;
		// Easy Pie Chart
		$(".pie-chart").easyPieChart({
			size:150,
			easing: 'easeOutBounce',
			onStep: function(from, to, percent) {
				$(this.el).find('.percent').text(Math.round(percent));
			},
			barColor:'#FFF',
			delay: 3000,
			trackColor:'rgba(255,255,255,0.2)',
			scaleColor:false,
			lineWidth:16,
			lineCap:'butt'
		});
	});
	// Custom animations
	$(".animate-click").click(function(){
		var animation = $(this).data("animate");
		if(animation != undefined){
			
			$(this).find(".animate-wr").addClass(animation);
		}
	});
	
	$(".animate-hover").hover(function(){
		var animation = $(this).data("animate");
		if(animation != undefined){
			
			$(this).find(".animate-wr").addClass(animation);
	
		}
	});
	// Aside Menu
	$("#cmdAsideMenu, #btnHideAsideMenu, .navbar-toggle-aside-menu").click(function(){
		if($("#asideMenu").is(":visible")){
			$("#asideMenu").hide();
			$("body").removeClass("aside-menu-in");
		}
		else{
			$("body").addClass("aside-menu-in");
			$("#asideMenu").show();
		}
		return false;	
	});	
});