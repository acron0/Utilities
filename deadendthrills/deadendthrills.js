// variables
// -------------------------------------

// - the div where we're located;
var _entryPoint; 

// - the minimum delay between a transition (it will surpass this if the load is taking longer)
var _minDelay;

// - the two images used for displaying and transitioning.
var _imageA, _imageB;

// - 
var _preloader;

// - the jsonp callback url
//var _imageCallbackUrl = 'http://localhost:8000/deadendthrills';
//var _imageCallbackUrl = 'http://teamwoods.org/deadendthrills/jsonp_callback=?';
var _imageCallbackUrl = 'http://localhost:8000/jsonp_callback=?';


// functions
// -------------------------------------

// - gets a new image url from offsite
function getNewImage(startMinDelay) 
{	
	// get image url from jsonp	
	var jqxhr = $.getJSON(_imageCallbackUrl, function(json){data = json});
	jqxhr.success(successFunction);
	jqxhr.error(errorFunction);
}

// - the jsonp callback returned successfully
function successFunction()
{
	$(_imageA).attr("src",data.url);	
}

// - the jsonp callback returned an error
function errorFunction(XMLHttpRequest,textStatus, errorThrown) 
{
	console.log("An error occurred.");
}

function createImage()
{
	var newImage =  document.createElement('img');
	newImage.onload = imageLoadedCallback;
	$(newImage).attr("style","width:100%;display:none;");
	return newImage;
}

function imageLoadedCallback(object)
{	
	if(_preloader != null)
	{
		$(_preloader).remove();
	}
		
	console.log("image loaded");
	
	$(_imageA).css("display","block");	
}

// - [jQuery] the DOM is ready 
$(document).ready(function() 
{
	_entryPoint = document.getElementById("deadendthrills_slideshow");
	_minDelay = _entryPoint.getAttribute("delay");
	
	_preloader = document.getElementById("deadendthrills_preloader");
	console.log(_preloader);
	
	var innerDiv = document.createElement('div');
	$(innerDiv).attr("style","width:100%;margin: 0px auto;");

	_imageA = createImage();
	_imageB = createImage();
	
	innerDiv.appendChild(_imageA);
	innerDiv.appendChild(_imageB);
	_entryPoint.appendChild(innerDiv);
	
	getNewImage(false);

});
