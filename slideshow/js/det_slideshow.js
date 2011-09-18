// globals
var canvas, context, data, imgIndex, timer, alpha, minDelay, minDelayTimeoutID, imageCanBeShown;
var imgs = new Array();
imgIndex = 0;
alpha = 0.0;
timer = 0;
minDelayTimeoutID = 0;
imageCanBeShown = true;

// helpers
function getNewImage(startMinDelay) {
	
	// get image url from jsonp	
	var jqxhr = $.getJSON('http://teamwoods.org/deadendthrills/jsonp?callback=?', function(json){data = json});
	jqxhr.success(successFunction);
	jqxhr.error(errorFunction);
	
	// kick off the minDelay timer
	if(startMinDelay) {
		minDelayTimeoutID = setTimeout(minDelayReached, minDelay);
	}
}

function minDelayReached() {

	console.log('det_slideshow: Min Delay Reached.');
	
	if(imageCanBeShown) {
		flipImages();
	}
	else {
		imageCanBeShown = true;
	}

}

function flipImages() {

	imageCanBeShown = false;
	clearTimeout(minDelayTimeoutID);
	imgIndex = 1 - imgIndex;			
	alpha = 0.0;
	clearInterval(timer);
	timer = setInterval(drawSlideshowImage, 50);
	
	console.log('det_slideshow: Images Flipped!');
}

function drawSlideshowImage() {

	context.clearRect(0,0, canvas.width,canvas.height);

	context.globalAlpha = alpha;
	context.drawImage(imgs[imgIndex], 0, 0, canvas.width, canvas.height);
	
	if(imgs[1-imgIndex] && alpha < 1.0) {
		context.globalAlpha = 1.0 - alpha;
		context.drawImage(imgs[1-imgIndex], 0, 0, canvas.width, canvas.height);
	}
	
	if (alpha >= 1.0)
	{
		alpha = 0.0;
		clearInterval(timer);
		
		// start the process again
		getNewImage(true);
	}
	alpha = Math.min(1.0, alpha + 0.05);			
}

// callback functions
function successFunction() {

	console.log('det_slideshow: Downloading ' + data.image.url);
	
	var nextImageIndex = 1 - imgIndex;
	
	imgs[nextImageIndex] = new Image();
	imgs[nextImageIndex].src = data.image.url;
	imgs[nextImageIndex].onload = function() {	
		console.log('det_slideshow: Download Complete.');
		
		if(imageCanBeShown) {
			flipImages();
		}
		else {
			imageCanBeShown = true;
		}
	};		
}

flipImages

function errorFunction() {
	$("body").append("An error occurred.");
}

// ---------------------------
$(document).ready(function() {

	canvas = document.getElementById("det_slideshow");
	context = canvas.getContext("2d");	
	minDelay = canvas.getAttribute("delay");		
	getNewImage(false);

});