// variables
// -------------------------------------

// - the div where we're located;
var _entryPoint; 

// - the minimum delay between a transition (it will surpass this if the load is taking longer)
var _minDelay;

// - the two images used for displaying and transitioning.
var _imageA, _imageB;

// - the jsonp callback url
var _imageCallbackUrl = 'http://localhost:8000/deadendthrills/jsonp?callback=?';
//var _imageCallbackUrl = 'http://teamwoods.org/deadendthrills/jsonp?callback=?';


// functions
// -------------------------------------

// - gets a new image url from offsite
function getNewImage(startMinDelay) 
{	
	// get image url from jsonp	
	var jqxhr = $.getJSON(randomImageUrl, function(json){data = json});
	jqxhr.success(successFunction);
	jqxhr.error(errorFunction);
	
}

// - the jsonp callback returned successfully
function successFunction()
{
	
}

// - the jsonp callback returned an error
function errorFunction() 
{
	console.log("An error occurred.");
}

// - [jQuery] the DOM is ready 
$(document).ready(function() 
{
	_entryPoint = document.getElementById("deadendthrills_slideshow");
	_minDelay = _entryPoint.getAttribute("delay");

	_imageA = document.createElement('img');	
	_imageB = document.createElement('img');	
	
	_entryPoint.appendChild(_imageA);
	_entryPoint.appendChild(_imageB);
	
	//getNewImage(false);

});
