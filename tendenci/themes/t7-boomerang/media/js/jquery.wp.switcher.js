// Variables
var styckyNav;

// Theme Switcher for Preview
$("#cmdShowStyleSwitcher").click(function(){
	if($("#divStyleSwitcher").hasClass("opened")){
		$("#divStyleSwitcher").removeClass("opened");
	}
	else{
		$("#divStyleSwitcher").addClass("opened");
	}
	return false;
});

var scheme = $.cookie('scheme');
if (scheme == 'wp-theme-1') {
	$("body").removeClass();
	$("body").addClass("wp-theme-1");
}
else if (scheme == 'wp-theme-2') {
	$("body").removeClass();
	$("body").addClass("wp-theme-2");
}
else if (scheme == 'wp-theme-3') {
	$("body").removeClass();
	$("body").addClass("wp-theme-3");
}
else if (scheme == 'wp-theme-4') {
	$("body").removeClass();
	$("body").addClass("wp-theme-4");
}
else if (scheme == 'wp-theme-5') {
	$("body").removeClass();
	$("body").addClass("wp-theme-5");
}
else if (scheme == 'wp-theme-6') {
	$("body").removeClass();
	$("body").addClass("wp-theme-6");
}

var layout = $.cookie('layout');
if (layout == 'boxed') {
	$(".wrapper").addClass("boxed");
}
else{
	$(".wrapper").removeClass("boxed");	
}

var topHeader = $.cookie('top-header');
if (topHeader == 'hide') {
	$(".top-header").addClass("hide");
}
else{
	$(".top-header").removeClass("hide");
}

var layout = $.cookie('layout');
if (layout == 'boxed') {
	$(".wrapper").addClass("boxed");
}
else{
	$(".wrapper").removeClass("boxed");	
}

var background = $.cookie('background');
if (background == 'body-bg-1') {
	$("body").addClass("body-bg-1");
}
else if (background == 'body-bg-2') {
	$("body").addClass("body-bg-2");
}
else if (background == 'body-bg-3') {
	$("body").addClass("body-bg-3");
}
else if (background == 'body-bg-4') {
	$("body").addClass("body-bg-4");
}
else if (background == 'body-bg-5') {
	$("body").addClass("body-bg-5");
}
else if (background == 'body-bg-6') {
	$("body").addClass("body-bg-6");
}

var navStyle = $.cookie('navigation-style');
if (navStyle == 'contrasted') {
	$(".navbar").addClass("navbar-contrasted");
}
else{
	$(".navbar").removeClass("navbar-contrasted");	
}

var date = new Date();
date.setTime(date.getTime() + (5 * 60 * 1000));

$("#cmdRed").click(function(){
	$("body").removeClass(scheme);
	$("body").addClass("wp-theme-1");
	checkAsideMenuVisibility();
	$.cookie('scheme', 'wp-theme-1', { expires:date});
	scheme = "wp-theme-1";
	return false;
});
$("#cmdViolet").click(function(){
	$("body").removeClass(scheme);
	$("body").addClass("wp-theme-2");
	checkAsideMenuVisibility();
	$.cookie('scheme', 'wp-theme-2', { expires:date});
	scheme = "wp-theme-2";
	return false;
});
$("#cmdBlue").click(function(){
	$("body").removeClass(scheme);
	$("body").addClass("wp-theme-3");
	checkAsideMenuVisibility();
	$.cookie('scheme', 'wp-theme-3', { expires:date});
	scheme = "wp-theme-3";
	return false;
});
$("#cmdGreen").click(function(){
	$("body").removeClass(scheme);
	$("body").addClass("wp-theme-4");
	checkAsideMenuVisibility();
	$.cookie('scheme', 'wp-theme-4', { expires:date});
	scheme = "wp-theme-4";
	return false;
});
$("#cmdYellow").click(function(){
	$("body").removeClass(scheme);
	$("body").addClass("wp-theme-5");
	checkAsideMenuVisibility();
	$.cookie('scheme', 'wp-theme-5', { expires:date});
	scheme = "wp-theme-5";
	return false;
});
$("#cmdOrange").click(function(){
	$("body").removeClass(scheme);
	$("body").addClass("wp-theme-6");
	checkAsideMenuVisibility();
	$.cookie('scheme', 'wp-theme-6', { expires:date});
	scheme = "wp-theme-6";
	return false;
});

function checkAsideMenuVisibility(){
	if($("#asideMenu").is(":visible")){
		$("#asideMenu").show();
		$("body").addClass("aside-menu-in");
	}
}

// Layout
$("#cmbLayout").change(function(){
	if($("#cmbLayout").val() == 2){
		$(".wrapper").addClass("boxed");	
		$.cookie('layout', 'boxed', { expires:date});
	}
	else{
		$(".wrapper").removeClass("boxed");
		$.cookie('layout', 'fluid', { expires:date});
	}
});

// Layout Style
$("#cmbLayoutStyle").change(function(){
	if($(this).val() == 2){
		$(".wrapper").removeClass("lw");	
		$(".wrapper").addClass("ld");	
		$(".top-header").addClass("top-header-dark");	
		$.cookie('layout-style', 'dark', { expires:date});
	}
	else{
		$(".wrapper").removeClass("ld");	
		$(".wrapper").addClass("lw");	
		$(".top-header").removeClass("top-header-dark");	
		$.cookie('layout-style', 'white', { expires:date});
	}
});

// Top header
$("#cmbTopHeader").change(function(){
	if($("#cmbTopHeader").val() == 2){
		$(".top-header").addClass("hide");
		$("#cmbTopHeaderStyle").attr("disabled", true);
		$.cookie('top-header', 'hide', { expires:date});	
	}
	else{
		$(".top-header").removeClass("hide");
		$("#cmbTopHeaderStyle").attr("disabled", false);
		$.cookie('top-header', 'show', { expires:date});	
	}
});

// Top header style
$("#cmbTopHeaderStyle").change(function(){
	if($(this).val() == 2){
		$(".top-header").addClass("top-header-dark");
		$.cookie('top-header-style', 'dark', { expires:date});	
	}
	else{
		$(".top-header").removeClass("top-header-dark");
		$.cookie('top-header-style', 'white', { expires:date});	
	}
});

// Navigation
$("#cmbNavigation").change(function(){
	if($(this).val() == 2){
		$("#navOne").addClass("hide");
		$("#navTwo").removeClass("hide");
		$.cookie('navigation', 'two', { expires:date});	
	}
	else{
		$("#navTwo").addClass("hide");
		$("#navOne").removeClass("hide");
		$.cookie('navigation', 'one', { expires:date});	
	}
});

// Navigation Style
$("#cmbNavigationStyle").change(function(){
	if($(this).val() == 2){
		$(".navbar-wp").addClass("navbar-contrasted");
		$.cookie('navigation-style', 'contrasted', { expires:date});	
	}
	else{
		$(".navbar-wp").removeClass("navbar-contrasted");
		$.cookie('navigation-style', 'white', { expires:date});	
	}
});


// Stycky nav
$("#cmbNavigationStycky").change(function(){
	if($(this).val() == 2){
		stickyNav = false;
		//$.cookie('sticky-nav', 'disabled', { expires:date});	
		window.location.reload();
	}
	else{
		stickyNav = true;
		//$.cookie('sticky-nav', 'enabled', { expires:date});	
		enableStickyNav();
	}
});
	
function enableStickyNav(){
	$(".navbar").sticky({ 
		topSpacing: 0 ,
		className: "navbar-fixed"
	});	
}

// Pattern/background
$("#cmbBackground").change(function(){
	if($("#cmbBackground").val() == 1){
		$("body").removeClass(background);
		$("body").addClass("body-bg-1");
		$.cookie('background', 'body-bg-1', { expires:date});
		background = "body-bg-1";	
	}
	else if($("#cmbBackground").val() == 2){
		$("body").removeClass(background);
		$("body").addClass("body-bg-2");
		$.cookie('background', 'body-bg-2', { expires:date});	
		background = "body-bg-2";	
	}
	else if($("#cmbBackground").val() == 3){
		$("body").removeClass(background);
		$("body").addClass("body-bg-3");
		$.cookie('background', 'body-bg-3', { expires:date});	
		background = "body-bg-3";	
	}
	else if($("#cmbBackground").val() == 4){
		$("body").removeClass(background);
		$("body").addClass("body-bg-4");
		$.cookie('background', 'body-bg-4', { expires:date});	
		background = "body-bg-4";	
	}
	else if($("#cmbBackground").val() == 5){
		$("body").removeClass(background);
		$("body").addClass("body-bg-5");
		$.cookie('background', 'body-bg-5', { expires:date});	
		background = "body-bg-5";	
	}
	else if($("#cmbBackground").val() == 6){
		$("body").removeClass(background);
		$("body").addClass("body-bg-6");
		$.cookie('background', 'body-bg-6', { expires:date});	
		background = "body-bg-6";	
	}
});