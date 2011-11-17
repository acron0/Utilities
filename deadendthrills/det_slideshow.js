// globals
var canvas, context, data, imgIndex, timer, titleTimer, alpha, minDelay, minDelayTimeoutID, imageCanBeShown, currentGameTitle, randomImageUrl;
var imgs = new Array();
randomImageUrl = 'http://teamwoods.org/deadendthrills/jsonp?callback=?';
imgIndex = 0;
alpha = 0.0;
timer = 0;
titleTimer = 0;
minDelayTimeoutID = 0;
imageCanBeShown = true;
currentGameTitle = "";

function getNewImage(startMinDelay) {
	
	// get image url from jsonp	
	var jqxhr = $.getJSON(randomImageUrl, function(json){data = json});
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
	
	// resize the image
	imgs[imgIndex].scale = canvas.width / imgs[imgIndex].width;
	imgs[imgIndex].yOffset = (canvas.height - (imgs[imgIndex].height * imgs[imgIndex].scale))/2;
	
	console.log('det_slideshow: Images Flipped!');
}

function drawTitle() {
	
	context.font = "bold 20px sans-serif";
	context.textBaseline = "top";
	
	var left = 10;
	var top = 10;
	var textLength = context.measureText(currentGameTitle).width;
	//var textHeight = context.measureText(currentGameTitle).height;
	
	context.globalAlpha = alpha;
	context.fillStyle  = "#000000";	
	context.fillRect(left,top,textLength+2, 24);
	context.fillStyle  = "#ffffff";
	context.fillText(currentGameTitle, left+1, top-1);
	
	if (alpha >= 1.0)
	{
		alpha = 0.0;
		clearInterval(titleTimer);
	}
	
	alpha = Math.min(1.0, alpha + 0.05);
}

function drawSlideshowImage() {

	context.clearRect(0,0, canvas.width,canvas.height);

	if(imgs[imgIndex]) {
		context.globalAlpha = alpha;
		context.drawImage(imgs[imgIndex], 0, imgs[imgIndex].yOffset, imgs[imgIndex].width * imgs[imgIndex].scale, imgs[imgIndex].height * imgs[imgIndex].scale);
	}
	
	if(imgs[1-imgIndex] && alpha < 1.0) {
		context.globalAlpha = 1.0 - alpha;
		context.drawImage(imgs[1-imgIndex], 0, imgs[1-imgIndex].yOffset, imgs[1-imgIndex].width * imgs[1-imgIndex].scale, imgs[1-imgIndex].height * imgs[1-imgIndex].scale);
	}
	
	if (alpha >= 1.0)
	{
		currentGameTitle = data.image.name;
		titleTimer = setInterval(drawTitle, 50);
		
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
		console.log('det_slideshow: Download Complete - ' + imgs[nextImageIndex].naturalWidth + 'x' + imgs[nextImageIndex].naturalHeight);
		
		if(imageCanBeShown) {
			flipImages();
		}
		else {
			imageCanBeShown = true;
		}
	};		
}

function errorFunction() {
	$("body").append("An error occurred.");
}

$(document).ready(function() {

	canvas = document.getElementById("det_slideshow");
	canvas.width = document.width;
    canvas.height = document.height;
	
	context = canvas.getContext("2d");	
	minDelay = canvas.getAttribute("delay");		
	getNewImage(false);

});

function resetSlideShow() {
	imgs[imgIndex] = 0;
	clearInterval(timer);
	clearInterval(titleTimer);
};

var resizeTimer;
$(window).resize(function() {
    clearTimeout(resizeTimer);
    resizeTimer = setTimeout(resetSlideShow, 100);
});